"""Shared parsing for the weekly study guides in ``guides/``.

Both ``build_study_pdfs.py`` (markdown -> PDF) and ``build_index.py``
(markdown + ``weeks.yml`` -> ``index.html``) read the guides through this
module, so the two outputs can't drift in how a guide is interpreted.

Each guide follows this exact shape::

    # Week N: Title
    *Subtitle*

    Intro paragraph (one or more lines, blank-line separated from what follows).

    1. First question...
    2. Second question...
    ...
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent
GUIDES_DIR = REPO / "guides"


def guide_paths(target: Path | None = None) -> list[Path]:
    """Every ``*.md`` under ``guides/`` (or under *target* if given)."""
    root = target or GUIDES_DIR
    return sorted(root.glob("*.md"))


def parse_guide(md_text: str) -> dict:
    lines = [line.rstrip("\n") for line in md_text.splitlines()]

    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    title_line = lines[idx].lstrip("#").strip()
    idx += 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    subtitle_line = lines[idx].strip().strip("*")
    idx += 1

    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    intro_parts = []
    while idx < len(lines) and lines[idx].strip() and not re.match(r"^\d+\.\s", lines[idx].strip()):
        intro_parts.append(lines[idx].strip())
        idx += 1
    intro = " ".join(intro_parts)

    items = []
    while idx < len(lines):
        m = re.match(r"^\d+\.\s+(.*)$", lines[idx].strip())
        if m:
            items.append(m.group(1))
        idx += 1

    return {
        "title": title_line,
        "subtitle": subtitle_line,
        "intro": intro,
        "items": items,
    }


def inline_markdown(text: str, *, ref_class: bool = False) -> str:
    """Convert ``**bold**`` and ``*italic*`` spans to HTML. Bold before italic.

    With ``ref_class=True`` the bold spans become ``<strong class="ref">`` --
    index.html uses that to highlight the "Read <passage>." prompts. The PDF
    build leaves it False for a plain ``<strong>``.
    """
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    open_tag = '<strong class="ref">' if ref_class else "<strong>"
    text = re.sub(r"\*\*(.+?)\*\*", open_tag + r"\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text
