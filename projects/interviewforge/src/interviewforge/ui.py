"""Server-rendered candidate application and progress actions."""

import asyncio
import json
import logging
from datetime import date
from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from interviewforge.ai.coach import answer_amazon_question
from interviewforge.ai.leetcode_mcp import search_problems
from interviewforge.roadmap import apply_mcp_problems, build_roadmap, complete_task
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
):
    try:
        roadmap = build_roadmap(
            name=name, experience=experience, hours_per_day=hours_per_day, target_date=target_date
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
        f"Create a concise two-sentence preparation priority for an Amazon software engineering candidate with experience '{experience}', {hours_per_day} study hours per day, and a target date of {target_date.isoformat()}. Do not invent current hiring-process facts.",
    )
    if note.live_model:
        roadmap.agent_note = note.text
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


@router.get("/practice", response_class=HTMLResponse)
def practice(request: Request):
    roadmap = store(request).load()
    return templates.TemplateResponse(
        request=request,
        name="practice.html",
        context=page_context(
            request,
            "practice",
            roadmap=roadmap,
            leetcode_mcp_configured=bool(request.app.state.settings.leetcode_mcp_server_url),
        ),
    )


@router.post("/practice/sync")
async def sync_practice_problems(request: Request):
    settings = request.app.state.settings
    roadmap = store(request).load()
    if roadmap is None:
        return RedirectResponse("/onboarding", status_code=303)
    if not settings.leetcode_mcp_server_url:
        raise HTTPException(status_code=409, detail="LeetCode MCP is not configured")
    try:
        problem_groups = await asyncio.gather(
            *(
                search_problems(
                    settings.leetcode_mcp_server_url, settings.leetcode_mcp_tool, difficulty, 3
                )
                for difficulty in ("EASY", "MEDIUM", "HARD")
            )
        )
        apply_mcp_problems(roadmap, problem_groups)
    except Exception as exc:
        logger.warning(
            json.dumps({"event": "leetcode_mcp_failed", "error_type": type(exc).__name__})
        )
        roadmap.problem_sync_message = (
            "LeetCode MCP could not be reached; curated links remain active."
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
def coach(request: Request):
    settings = request.app.state.settings
    return templates.TemplateResponse(
        request=request,
        name="coach.html",
        context=page_context(
            request,
            "coach",
            question=None,
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
    result = answer_amazon_question(settings, question)
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
