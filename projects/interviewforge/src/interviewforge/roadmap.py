"""Deterministic Amazon preparation roadmap and unlock rules."""

from datetime import date, timedelta
from typing import Literal

from pydantic import BaseModel, Field

from interviewforge.amazon_content import LESSONS, SOURCES


class PracticeProblem(BaseModel):
    title: str
    slug: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    url: str
    source: Literal["curated", "leetcode_mcp", "amazon_mcp"] = "curated"
    report_url: str | None = None
    reported_date: str | None = None
    match_type: str | None = None


class RoadmapTask(BaseModel):
    id: str
    title: str
    kind: Literal["learn", "code", "review"]
    minutes: int
    completed: bool = False
    problem: PracticeProblem | None = None
    lesson: str = ""
    exercise: str = ""
    source_url: str = ""
    scheduled_date: date | None = None


class RoadmapLevel(BaseModel):
    number: int
    title: str
    objective: str
    tasks: list[RoadmapTask]

    @property
    def completed(self) -> bool:
        return bool(self.tasks) and all(task.completed for task in self.tasks)


class CandidateRoadmap(BaseModel):
    company: Literal["Amazon"] = "Amazon"
    curriculum_version: int = 2
    role: Literal["SDE I", "SDE II"] = "SDE I"
    skill: Literal["beginner", "intermediate", "advanced"] = "beginner"
    include_genai: bool = False
    language: Literal["Python"] = "Python"
    name: str = Field(min_length=2, max_length=60)
    experience: str
    target_date: date
    hours_per_day: int = Field(ge=1, le=8)
    created_on: date
    levels: list[RoadmapLevel]
    assessment_completed: bool = False
    agent_note: str
    agent_note_source: Literal["deep_agent", "local_planner"] = "local_planner"
    problem_sync_message: str = "Curated public LeetCode links are active."

    @property
    def days_remaining(self) -> int:
        return max((self.target_date - date.today()).days, 0)

    @property
    def completed_tasks(self) -> int:
        return sum(task.completed for level in self.levels for task in level.tasks)

    @property
    def total_tasks(self) -> int:
        return sum(len(level.tasks) for level in self.levels)

    @property
    def readiness_percent(self) -> int:
        return round(self.completed_tasks / self.total_tasks * 100) if self.total_tasks else 0

    @property
    def assessment_unlocked(self) -> bool:
        return bool(self.levels) and all(level.completed for level in self.levels)

    @property
    def interview_unlocked(self) -> bool:
        return self.assessment_unlocked and self.assessment_completed

    def level_unlocked(self, level_number: int) -> bool:
        if level_number <= 1:
            return True
        return all(level.completed for level in self.levels if level.number < level_number)


def build_roadmap(
    *,
    name: str,
    experience: str,
    hours_per_day: int,
    target_date: date,
    today: date | None = None,
    role: Literal["SDE I", "SDE II"] = "SDE I",
    skill: Literal["beginner", "intermediate", "advanced"] = "beginner",
    include_genai: bool = False,
) -> CandidateRoadmap:
    today = today or date.today()
    if target_date <= today:
        raise ValueError("Target date must be after today")
    days = (target_date - today).days
    # More repetitions for beginners and longer preparation windows.
    repeats = (2 if skill == "beginner" else 1) + (1 if days >= 45 else 0)
    levels = []
    topics = [["coding", "lp"], ["lld", "design"] if role == "SDE II" else ["lld", "lp"], ["mock"]]
    if include_genai:
        topics[1].append("genai")
    for number, keys in enumerate(topics, 1):
        tasks = []
        for key in keys:
            title, source, lesson, exercise = LESSONS[key]
            for repetition in range(repeats if key in {"coding", "lp"} else 1):
                suffix = f" ? rehearsal {repetition + 1}" if repetition else ""
                task = RoadmapTask(
                    id=f"l{number}-{key}-{repetition}",
                    title=title + suffix,
                    kind="learn",
                    minutes=45 if skill == "advanced" else 60,
                    lesson=lesson,
                    exercise=exercise
                    + (
                        " Use a professional project and explain your personal ownership."
                        if experience != "Student / fresher" and key == "lp"
                        else ""
                    ),
                    source_url=SOURCES[source][1],
                )
                tasks.append(task)
        if number == 2:
            tasks.append(
                RoadmapTask(
                    id="l2-amazon-code",
                    title="Amazon-reported coding practice (sync evidence)",
                    kind="code",
                    minutes=60,
                )
            )
        levels.append(
            RoadmapLevel(
                number=number,
                title=[
                    "Learn concepts and Leadership Principles",
                    "Apply role-specific skills",
                    "Rehearse and review",
                ][number - 1],
                objective=f"Amazon {role} ? {skill} preparation",
                tasks=tasks,
            )
        )
    total = sum(t.minutes for level in levels for t in level.tasks)
    capacity = days * hours_per_day * 60
    elapsed = 0
    for level in levels:
        for task in level.tasks:
            task.scheduled_date = today + timedelta(
                days=min(
                    days - 1,
                    max(elapsed // (hours_per_day * 60), int(elapsed * days / max(total, 1))),
                )
            )
            elapsed += task.minutes
    warning = (
        f" Core work needs {total} minutes; your available {capacity} minutes are insufficient. Extend the date or increase study time."
        if total > capacity
        else ""
    )
    return CandidateRoadmap(
        name=name.strip(),
        experience=experience,
        target_date=target_date,
        hours_per_day=hours_per_day,
        created_on=today,
        levels=levels,
        role=role,
        skill=skill,
        include_genai=include_genai,
        agent_note=f"Amazon {role}: {days} days, {hours_per_day} hours/day. Learn concepts and LP first, then attributed coding practice and rehearsal.{warning}",
        problem_sync_message="Only Amazon-attributed reports are eligible. Sync the reviewed question registry after learning the foundations.",
    )


def complete_task(roadmap: CandidateRoadmap, task_id: str) -> CandidateRoadmap:
    for level in roadmap.levels:
        for task in level.tasks:
            if task.id == task_id:
                if task.id == "l2-amazon-code":
                    raise PermissionError(
                        "Retrieve Amazon-attributed problems before completing coding practice"
                    )
                if not roadmap.level_unlocked(level.number):
                    raise PermissionError("Complete the previous level first")
                task.completed = True
                return roadmap
    raise KeyError(task_id)


def apply_mcp_problems(
    roadmap: CandidateRoadmap, problems_by_level: list[list[PracticeProblem]]
) -> CandidateRoadmap:
    """Replace coding tasks only with validated problems returned by MCP."""
    eligible = [
        p
        for group in problems_by_level
        for p in group
        if p.report_url and p.reported_date and p.match_type
    ]
    level = roadmap.levels[1]
    existing = {task.problem.slug for task in level.tasks if task.problem}
    for problem in eligible:
        if problem.slug in existing:
            continue
        level.tasks.append(
            RoadmapTask(
                id=f"amazon-{problem.slug}",
                title=f"Amazon report: {problem.title}",
                kind="code",
                minutes=60,
                problem=problem,
            )
        )
        existing.add(problem.slug)
    if eligible:
        level.tasks = [t for t in level.tasks if t.id != "l2-amazon-code"]
    roadmap.problem_sync_message = f"{len(eligible)} Amazon-attributed problems retrieved. Report age and role are shown; no generic fallback."
    return roadmap
