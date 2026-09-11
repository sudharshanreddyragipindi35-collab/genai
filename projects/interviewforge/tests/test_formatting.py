from interviewforge.formatting import render_answer


def test_steps_code_and_dry_run_render_as_structured_html():
    text = """## 1. Understand the problem

1. Count duplicates.
2. Keep the smaller count.

## 2. Dry run

| Step | Value | State | Result |
| --- | --- | --- | --- |
| 1 | 2 | count = 2 | [2] |

## 3. Python

```python
for value in values:
    result.append(value)
```
"""
    result = str(render_answer(text))
    assert "<h2>1. Understand the problem</h2>" in result
    assert "<ol>" in result and "<table>" in result
    assert '<code class="language-python">' in result
    assert "    result.append(value)" in result


def test_model_html_and_unsafe_links_are_not_executable():
    result = str(
        render_answer(
            "<script>alert(1)</script>\n\n[click](javascript:alert(1))\n\n![track](https://example.com/track)"
        )
    )
    assert "<script>" not in result
    assert 'href="javascript:' not in result
    assert "<img" not in result
    assert "&lt;script&gt;" in result


def test_main_chat_uses_markdown_renderer(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient

    from interviewforge.ai.coach import CoachAnswer
    from interviewforge.app import create_app
    from interviewforge.config import Settings

    monkeypatch.setattr(
        "interviewforge.ui.answer_amazon_question",
        lambda *a: CoachAnswer("## 1. Approach\n\n- Count values", "live"),
    )
    with TestClient(
        create_app(Settings(_env_file=None, local_state_path=tmp_path / "state.json"))
    ) as client:
        response = client.post("/coach", data={"question": "Explain array intersection"})
    assert "<h2>1. Approach</h2>" in response.text
    assert "<li>Count values</li>" in response.text
