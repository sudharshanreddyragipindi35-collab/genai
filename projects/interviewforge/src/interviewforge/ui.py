"""Server-rendered application shell for the first visible product slice."""

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(include_in_schema=False)
templates = Jinja2Templates(directory=Path(__file__).resolve().parent / "templates")


def page_context(request: Request, active: str, **values: object) -> dict[str, object]:
    return {"request": request, "active": active, **values}


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context=page_context(request, "dashboard"),
    )


@router.get("/onboarding", response_class=HTMLResponse)
def onboarding(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="onboarding.html",
        context=page_context(request, "onboarding", profile=None),
    )


@router.post("/onboarding", response_class=HTMLResponse)
def onboarding_preview(
    request: Request,
    name: str = Form(min_length=2, max_length=60),
    experience: str = Form(),
    hours_per_day: int = Form(ge=1, le=8),
    target_date: str = Form(),
):
    profile = {
        "name": name,
        "experience": experience,
        "hours_per_day": hours_per_day,
        "target_date": target_date,
    }
    return templates.TemplateResponse(
        request=request,
        name="onboarding.html",
        context=page_context(request, "onboarding", profile=profile),
    )


@router.get("/practice", response_class=HTMLResponse)
def practice(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="practice.html",
        context=page_context(request, "practice"),
    )
