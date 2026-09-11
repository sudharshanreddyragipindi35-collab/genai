"""Deterministic Amazon preparation roadmap and unlock rules."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class PracticeProblem(BaseModel):
    title: str
    slug: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    url: str
    source: Literal["curated", "leetcode_mcp"] = "curated"


class RoadmapTask(BaseModel):
    id: str
    title: str
    kind: Literal["learn", "code", "review"]
    minutes: int
    completed: bool = False
    problem: PracticeProblem | None = None


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


CURATED_PROBLEMS = (
    ("Two Sum", "two-sum", "Easy", "array, hash map"),
    ("Valid Parentheses", "valid-parentheses", "Easy", "stack"),
    (
        "Binary Tree Level Order Traversal",
        "binary-tree-level-order-traversal",
        "Medium",
        "tree, BFS",
    ),
    ("Number of Islands", "number-of-islands", "Medium", "graph, DFS"),
    ("LRU Cache", "lru-cache", "Medium", "design"),
    ("Word Ladder", "word-ladder", "Hard", "graph, BFS"),
)


def _problem(index: int) -> PracticeProblem:
    title, slug, difficulty, _ = CURATED_PROBLEMS[index]
    return PracticeProblem(
        title=title,
        slug=slug,
        difficulty=difficulty,
        url=f"https://leetcode.com/problems/{slug}/",
    )


def build_roadmap(
    *, name: str, experience: str, hours_per_day: int, target_date: date, today: date | None = None
) -> CandidateRoadmap:
    today = today or date.today()
    if target_date <= today:
        raise ValueError("Target date must be after today")
    days = (target_date - today).days
    pace = "compressed" if days < 21 else "steady" if days < 60 else "extended"
    minutes = min(hours_per_day * 60, 180)
    levels = [
        RoadmapLevel(
            number=1,
            title="Level 1 · Foundations",
            objective="Build Python, DSA, and explanation fundamentals.",
            tasks=[
                RoadmapTask(
                    id="l1-concepts",
                    title="Review complexity, arrays, hash maps, and stacks",
                    kind="learn",
                    minutes=minutes,
                ),
                RoadmapTask(
                    id="l1-two-sum",
                    title="Solve Two Sum and explain the trade-offs",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(0),
                ),
                RoadmapTask(
                    id="l1-parentheses",
                    title="Solve Valid Parentheses without hints",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(1),
                ),
            ],
        ),
        RoadmapLevel(
            number=2,
            title="Level 2 · Problem-solving patterns",
            objective="Apply tree, graph, recursion, and design patterns.",
            tasks=[
                RoadmapTask(
                    id="l2-tree",
                    title="Practice breadth-first tree traversal",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(2),
                ),
                RoadmapTask(
                    id="l2-islands",
                    title="Practice graph traversal and edge cases",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(3),
                ),
                RoadmapTask(
                    id="l2-review",
                    title="Review solutions with the AI code coach",
                    kind="review",
                    minutes=minutes,
                ),
            ],
        ),
        RoadmapLevel(
            number=3,
            title="Level 3 · Interview readiness",
            objective="Work under time limits and communicate decisions clearly.",
            tasks=[
                RoadmapTask(
                    id="l3-design",
                    title="Implement and explain an LRU Cache",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(4),
                ),
                RoadmapTask(
                    id="l3-hard",
                    title="Attempt a timed advanced graph problem",
                    kind="code",
                    minutes=minutes,
                    problem=_problem(5),
                ),
                RoadmapTask(
                    id="l3-mock",
                    title="Complete a timed coding rehearsal",
                    kind="review",
                    minutes=minutes,
                ),
            ],
        ),
    ]
    return CandidateRoadmap(
        name=name.strip(),
        experience=experience,
        target_date=target_date,
        hours_per_day=hours_per_day,
        created_on=today,
        levels=levels,
        agent_note=(
            f"This is a {pace} plan with {days} days available. Complete each level in order; "
            "your assessment unlocks after every Level 3 task is complete."
        ),
    )


def complete_task(roadmap: CandidateRoadmap, task_id: str) -> CandidateRoadmap:
    for level in roadmap.levels:
        for task in level.tasks:
            if task.id == task_id:
                if not roadmap.level_unlocked(level.number):
                    raise PermissionError("Complete the previous level first")
                task.completed = True
                return roadmap
    raise KeyError(task_id)


def apply_mcp_problems(
    roadmap: CandidateRoadmap, problems_by_level: list[list[PracticeProblem]]
) -> CandidateRoadmap:
    """Replace coding tasks only with validated problems returned by MCP."""
    replaced = 0
    for level, problems in zip(roadmap.levels, problems_by_level, strict=False):
        coding_tasks = [task for task in level.tasks if task.kind == "code"]
        for task, problem in zip(coding_tasks, problems, strict=False):
            task.problem = problem
            task.title = f"Solve {problem.title} and explain the approach"
            replaced += 1
    roadmap.problem_sync_message = (
        f"Retrieved {replaced} validated problem(s) through LeetCode MCP."
        if replaced
        else "LeetCode MCP returned no usable problems; curated links remain active."
    )
    return roadmap
