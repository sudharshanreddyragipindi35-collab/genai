"""Server-rendered candidate application and progress actions."""

import json
import logging
from datetime import date
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from interviewforge.ai.amazon_client import call_amazon
from interviewforge.ai.coach import answer_amazon_question
from interviewforge.roadmap import PracticeProblem, apply_mcp_problems, build_roadmap, complete_task
from interviewforge.state import RoadmapStore

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")
logger = logging.getLogger("interviewforge.mcp")


def page_context(request: Request, active: str, **values: object) -> dict[str, object]:
    return {"request": request, "active": active, **values}


def store(request: Request) -> RoadmapStore:
    return RoadmapStore(request.app.state.settings.local_state_path)


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    roadmap = store(request).load()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=page_context(request, "dashboard", roadmap=roadmap),
    )


@router.get("/companies", response_class=HTMLResponse)
def companies(request: Request):
    return templates.TemplateResponse(
        request=request, name="companies.html", context=page_context(request, "onboarding")
    )


@router.get("/onboarding", response_class=HTMLResponse)
def onboarding(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="onboarding.html",
        context=page_context(request, "onboarding", profile=store(request).load(), error=None),
    )


@router.post("/onboarding", response_class=HTMLResponse)
def create_candidate_roadmap(
    request: Request,
    name: str = Form(min_length=2, max_length=60),
    experience: str = Form(),
    hours_per_day: int = Form(ge=1, le=8),
    target_date: date = Form(),
    role: Literal["SDE I", "SDE II"] = Form("SDE I"),
    skill: Literal["beginner", "intermediate", "advanced"] = Form("beginner"),
    include_genai: bool = Form(False),
):
    try:
        roadmap = build_roadmap(
            name=name,
            experience=experience,
            hours_per_day=hours_per_day,
            target_date=target_date,
            role=role,
            skill=skill,
            include_genai=include_genai,
        )
    except ValueError as exc:
        return templates.TemplateResponse(
            request=request,
            name="onboarding.html",
            status_code=422,
            context=page_context(request, "onboarding", profile=None, error=str(exc)),
        )
    settings = request.app.state.settings
    note = answer_amazon_question(
        settings,
        f"Create a concise two-sentence preparation priority for an Amazon software engineering candidate targeting {role} with experience '{experience}', {hours_per_day} study hours per day, and a target date of {target_date.isoformat()}. Do not invent current hiring-process facts.",
    )
    if note.live_model:
        roadmap.agent_note += "\n\n" + note.text
        roadmap.agent_note_source = "deep_agent"
    store(request).save(roadmap)
    return RedirectResponse("/roadmap", status_code=303)


@router.get("/roadmap", response_class=HTMLResponse)
def roadmap_page(request: Request):
    roadmap = store(request).load()
    if roadmap is None:
        return RedirectResponse("/onboarding", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="roadmap.html",
        context=page_context(request, "roadmap", roadmap=roadmap),
    )


@router.post("/roadmap/tasks/{task_id}/complete")
def mark_task_complete(request: Request, task_id: str):
    roadmap = store(request).load()
    if roadmap is None:
        return RedirectResponse("/onboarding", status_code=303)
    try:
        complete_task(roadmap, task_id)
    except PermissionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
    except KeyError:
        raise HTTPException(status_code=404, detail="Roadmap task not found") from None
    store(request).save(roadmap)
    return RedirectResponse("/roadmap", status_code=303)


def _selected_problem(roadmap, slug: str | None):
    if roadmap is None or not slug:
        return None
    for level in roadmap.levels:
        if not roadmap.level_unlocked(level.number):
            continue
        for task in level.tasks:
            if task.problem and task.problem.slug == slug:
                return task.problem
    return None


def _practice_page(
    request: Request,
    *,
    selected=None,
    question: str | None = None,
    answer: str | None = None,
    response_kind: str | None = None,
):
    roadmap = store(request).load()
    return templates.TemplateResponse(
        request=request,
        name="practice.html",
        context=page_context(
            request,
            "practice",
            roadmap=roadmap,
            leetcode_mcp_configured=bool(request.app.state.settings.amazon_mcp_server_url),
            selected=selected,
            question=question,
            answer=answer,
            response_kind=response_kind,
        ),
    )


@router.get("/practice", response_class=HTMLResponse)
def practice(request: Request, problem: str | None = Query(default=None, max_length=120)):
    roadmap = store(request).load()
    return _practice_page(request, selected=_selected_problem(roadmap, problem))


@router.post("/practice/coach", response_class=HTMLResponse)
def practice_coach(
    request: Request,
    problem_slug: str = Form(min_length=1, max_length=120),
    question: str = Form(min_length=2, max_length=2_000),
):
    roadmap = store(request).load()
    selected = _selected_problem(roadmap, problem_slug)
    if selected is None:
        raise HTTPException(status_code=404, detail="Unlocked roadmap problem not found")
    prompt = (
        f"You are coaching this Amazon-targeted candidate on the public LeetCode problem "
        f"'{selected.title}' ({selected.difficulty}, slug: {selected.slug}) using Python. "
        "Answer their question directly. Teach the reasoning, ask a useful follow-up when "
        "appropriate, and prefer progressive hints before a complete solution unless they "
        f"explicitly request one. Candidate question: {question}"
    )
    result = answer_amazon_question(request.app.state.settings, prompt)
    return _practice_page(
        request,
        selected=selected,
        question=question,
        answer=result.text,
        response_kind=result.kind,
    )


@router.post("/practice/sync")
async def sync_practice_problems(request: Request):
    settings = request.app.state.settings
    roadmap = store(request).load()
    if roadmap is None:
        return RedirectResponse("/onboarding", status_code=303)
    if not settings.amazon_mcp_server_url:
        raise HTTPException(status_code=409, detail="Amazon content MCP is not configured")
    try:
        data = await call_amazon(
            settings.amazon_mcp_server_url,
            "amazon_reported_coding_questions",
            {"role": roadmap.role},
        )
        if data.get("company") != "amazon" or data.get("role") != roadmap.role:
            raise ValueError("Wrong company or role")
        from interviewforge.amazon_content import REPORTS

        registry = {p["slug"]: p for p in REPORTS[roadmap.role]}
        approved = []
        for item in data.get("problems", []):
            if item != registry.get(item.get("slug")):
                continue
            if settings.leetcode_mcp_server_url:
                from interviewforge.ai.leetcode_mcp import get_reported_problem

                await get_reported_problem(settings.leetcode_mcp_server_url, item["slug"])
            approved.append(
                PracticeProblem(
                    **item,
                    url=f"https://leetcode.com/problems/{item['slug']}/",
                    source="amazon_mcp",
                )
            )
        apply_mcp_problems(roadmap, [approved])
    except Exception as exc:
        logger.warning(json.dumps({"event": "amazon_mcp_failed", "error_type": type(exc).__name__}))
        roadmap.problem_sync_message = (
            "Amazon evidence retrieval failed. No generic questions were added."
        )
    store(request).save(roadmap)
    return RedirectResponse("/practice", status_code=303)


@router.get("/assessment", response_class=HTMLResponse)
def assessment(request: Request):
    roadmap = store(request).load()
    if roadmap is None:
        return RedirectResponse("/onboarding", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="assessment.html",
        context=page_context(request, "roadmap", roadmap=roadmap),
    )


@router.post("/assessment/complete")
def assessment_complete(request: Request):
    roadmap = store(request).load()
    if roadmap is None or not roadmap.assessment_unlocked:
        raise HTTPException(status_code=409, detail="Complete all roadmap levels first")
    roadmap.assessment_completed = True
    store(request).save(roadmap)
    return RedirectResponse("/roadmap", status_code=303)


@router.get("/coach", response_class=HTMLResponse)
def coach(request: Request, lesson: str | None = None):
    settings = request.app.state.settings
    return templates.TemplateResponse(
        request=request,
        name="coach.html",
        context=page_context(
            request,
            "coach",
            question=lesson,
            answer=None,
            live_model=False,
            response_kind=None,
            configured=settings.claude_ready,
            model=settings.llm_model,
        ),
    )


@router.post("/coach", response_class=HTMLResponse)
def ask_coach(request: Request, question: str = Form(min_length=2, max_length=2_000)):
    settings = request.app.state.settings
    roadmap = store(request).load()
    context = (
        f"Target Amazon {roadmap.role}; experience {roadmap.experience}; current skills {roadmap.skill}; interview {roadmap.target_date}; hours/day {roadmap.hours_per_day}. "
        if roadmap
        else ""
    )
    result = answer_amazon_question(settings, context + question)
    return templates.TemplateResponse(
        request=request,
        name="coach.html",
        context=page_context(
            request,
            "coach",
            question=question,
            answer=result.text,
            live_model=result.live_model,
            response_kind=result.kind,
            configured=settings.claude_ready,
            model=result.model or settings.llm_model,
        ),
    )


@router.get("/coach/status")
def coach_status(request: Request):
    settings = request.app.state.settings
    return {
        "provider": settings.llm_provider,
        "model": settings.llm_model,
        "configured": settings.claude_ready,
        "amazon_mcp_configured": bool(settings.amazon_mcp_server_url),
        "leetcode_mcp_configured": bool(settings.leetcode_mcp_server_url),
    }
