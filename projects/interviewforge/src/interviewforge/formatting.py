"""Render model Markdown with raw HTML and embedded images disabled."""

from markdown_it import MarkdownIt
from markupsafe import Markup

_markdown = MarkdownIt("js-default").disable("image")


def render_answer(value: str) -> Markup:
    return Markup(_markdown.render(value))
