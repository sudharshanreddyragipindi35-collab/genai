"""Small local preview store; PostgreSQL ownership replaces this in production."""

from pathlib import Path
from threading import Lock

from interviewforge.roadmap import CandidateRoadmap


class RoadmapStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = Lock()

    def load(self) -> CandidateRoadmap | None:
        if not self.path.exists():
            return None
        return CandidateRoadmap.model_validate_json(self.path.read_text(encoding="utf-8"))

    def save(self, roadmap: CandidateRoadmap) -> None:
        with self._lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            temporary = self.path.with_suffix(".tmp")
            temporary.write_text(roadmap.model_dump_json(indent=2), encoding="utf-8")
            temporary.replace(self.path)
