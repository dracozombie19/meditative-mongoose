#!/usr/bin/env python3
"""
Converts weekly Bible study markdown guides into printable PDFs.

Expects each markdown file to follow this exact shape:

    # Week N: Title
    *Subtitle*

    Intro paragraph (one or more lines, blank-line separated from what follows).

    1. First question...
    2. Second question...
    ...

Usage:
    python build_study_pdfs.py                     # convert every .md in guides/
    python build_study_pdfs.py guides/Week 01 - What Is the Bible.md
    python build_study_pdfs.py path/to/some/dir     # convert every .md in that dir

Each PDF is written next to its source markdown file, same name, .pdf extension
(e.g. guides/Week 01 - What Is the Bible.md -> guides/Week 01 - What Is the Bible.pdf)
so the flat "guides/" layout that index.html links against stays in sync.
"""

import base64
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent
DEFAULT_DIR = WORKSPACE / "guides"

# Common install locations for a headless-capable Chromium browser on Windows.
BROWSER_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]

CSS = """
  @page { size: letter; margin: 1in; }
  body {
    font-family: Georgia, 'Times New Roman', serif;
    color: #1a1a1a;
    line-height: 1.5;
    font-size: 12pt;
  }
  h1 { font-size: 20pt; margin-bottom: 2px; }
  .subtitle { font-style: italic; color: #555; margin-top: 0; margin-bottom: 20px; font-size: 11pt; }
  .intro { margin-bottom: 22px; }
  ol { padding-left: 1.3em; }
  li { margin-bottom: 16px; }
"""


def find_browser() -> str:
    for path in BROWSER_CANDIDATES:
        if Path(path).exists():
            return path
    sys.exit(
        "No headless-capable browser found (checked Edge/Chrome default install paths). "
        "Edit BROWSER_CANDIDATES in this script to point at your browser's .exe."
    )


def inline_markdown(text: str) -> str:
    """Convert **bold** and *italic* spans to HTML. Order matters: bold before italic."""
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.+?)\*", r"<em>\1</em>", text)
    return text


def parse_study_guide(md_text: str) -> dict:
    lines = [line.rstrip("\n") for line in md_text.splitlines()]
    lines = [line for line in lines if line.strip() != "" or True]  # keep blanks as separators

    # Strip leading blank lines
    idx = 0
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    title_line = lines[idx].lstrip("#").strip()
    idx += 1
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    subtitle_line = lines[idx].strip().strip("*")
    idx += 1

    # Skip blank lines before intro paragraph
    while idx < len(lines) and not lines[idx].strip():
        idx += 1

    intro_parts = []
    while idx < len(lines) and lines[idx].strip() and not re.match(r"^\d+\.\s", lines[idx].strip()):
        intro_parts.append(lines[idx].strip())
        idx += 1
    intro = " ".join(intro_parts)

    items = []
    while idx < len(lines):
        stripped = lines[idx].strip()
        m = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m:
            items.append(m.group(1))
        idx += 1

    return {
        "title": title_line,
        "subtitle": subtitle_line,
        "intro": intro,
        "items": items,
    }


def build_html(parsed: dict) -> str:
    items_html = "\n".join(f"<li>{inline_markdown(item)}</li>" for item in parsed["items"])
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>{inline_markdown(parsed['title'])}</title>
<style>{CSS}</style>
</head>
<body>
<h1>{inline_markdown(parsed['title'])}</h1>
<p class="subtitle">{inline_markdown(parsed['subtitle'])}</p>
<p class="intro">{inline_markdown(parsed['intro'])}</p>
<ol>
{items_html}
</ol>
</body>
</html>
"""


def convert_one(md_path: Path, browser: str) -> Path:
    md_path = md_path.resolve()
    parsed = parse_study_guide(md_path.read_text(encoding="utf-8"))
    html = build_html(parsed)

    # Pass the page as a data: URI instead of a temp file on disk. Writing a temp
    # .html file and deleting it after the browser call is a race condition on
    # Windows: if a real (non-headless) instance of the browser is already
    # running, launching it again — even with an isolated --user-data-dir —
    # sometimes hands the navigation off asynchronously, and the temp file can
    # already be gone by the time it's actually loaded, producing a PDF of
    # Edge's own "File not found" error page instead of the real content.
    # A data: URI has no file to race against.
    b64 = base64.b64encode(html.encode("utf-8")).decode("ascii")
    data_uri = f"data:text/html;base64,{b64}"

    pdf_path = md_path.parent / (md_path.stem + ".pdf")
    with tempfile.TemporaryDirectory(prefix="pdfbuild-", ignore_cleanup_errors=True) as profile_dir:
        result = subprocess.run(
            [
                browser,
                "--headless=new",
                "--disable-gpu",
                "--no-sandbox",
                "--no-pdf-header-footer",
                f"--user-data-dir={profile_dir}",
                f"--print-to-pdf={pdf_path}",
                data_uri,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
    if result.returncode != 0:
        raise RuntimeError(f"browser exited {result.returncode}: {result.stderr}")
    if not pdf_path.exists() or pdf_path.stat().st_size == 0:
        raise RuntimeError("browser exited cleanly but no PDF was written")

    return pdf_path


def main(argv: list[str]) -> None:
    browser = find_browser()

    targets: list[Path] = []
    if len(argv) <= 1:
        targets = sorted(DEFAULT_DIR.glob("*.md"))
    else:
        for arg in argv[1:]:
            p = Path(arg)
            if p.is_dir():
                targets.extend(sorted(p.glob("*.md")))
            else:
                targets.append(p)

    if not targets:
        sys.exit("No markdown files found to convert.")

    for md_path in targets:
        if not md_path.exists():
            print(f"SKIP (not found): {md_path}")
            continue
        pdf_path = convert_one(md_path, browser)
        print(f"OK: {pdf_path.name}")


if __name__ == "__main__":
    main(sys.argv)
