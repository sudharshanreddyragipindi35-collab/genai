"""Verify the planning scaffold and relative Markdown file links, offline."""

from pathlib import Path
import re
import tomllib


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    project = root / "projects" / "interviewforge"
    errors = []
    for name in ("ARCHITECTURE", "PHASE_1", "PHASE_2", "ROADMAP", "REQUIREMENTS"):
        if not (project / "docs" / f"{name}.md").is_file():
            errors.append(f"Missing {name} plan")
    with (project / "pyproject.toml").open("rb") as stream:
        metadata = tomllib.load(stream)
    if metadata["project"]["name"] != "genai-interviewforge":
        errors.append("Unexpected project name")
    ignored_parts = {".git", ".venv", ".tools", ".uv-cache", "site-packages"}
    for document in root.rglob("*.md"):
        if ignored_parts.intersection(document.parts):
            continue
        for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in link or link.startswith("#"):
                continue
            target = link.split("#", 1)[0]
            if not (document.parent / target).exists():
                errors.append(f"Broken link in {document.relative_to(root)}: {target}")
    for folder in (project / "src", project / "tests", root / "scripts"):
        for path in folder.rglob("*"):
            if path.suffix in {".js", ".jsx", ".ts", ".tsx", ".java"}:
                errors.append(f"Non-Python implementation: {path.relative_to(root)}")
    if errors:
        raise SystemExit("\n".join(errors))
    print("Planning files, relative links, project metadata and Python-only scaffold verified.")


if __name__ == "__main__":
    main()
