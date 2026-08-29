#!/usr/bin/env python3
"""Regenerate index.html from weeks.yml + the guide markdown in guides/.

The discussion questions and their counts come straight from the guide
markdown; everything else about a week (category, blurb, video and podcast
links, ordering, short nav label) lives in weeks.yml.

Usage:
    python build_index.py            # write index.html
    python build_index.py --check    # exit 1 if index.html is stale, write nothing
"""

import sys
from pathlib import Path
from urllib.parse import quote

try:
    import yaml
    from jinja2 import Environment, FileSystemLoader, StrictUndefined
except ModuleNotFoundError as exc:  # pragma: no cover - setup hint
    sys.exit(
        f"missing build dependency ({exc.name}). Install with:\n"
        "    python -m pip install -r requirements.txt"
    )

import studyguide

REPO = Path(__file__).resolve().parent
CONFIG = REPO / "weeks.yml"
TEMPLATE_DIR = REPO / "templates"
OUTPUT = REPO / "index.html"


def render() -> str:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))

    weeks = []
    for w in config["weeks"]:
        guide_path = REPO / w["guide"]
        if not guide_path.exists():
            sys.exit(f"weeks.yml points at a missing guide: {w['guide']}")
        parsed = studyguide.parse_guide(guide_path.read_text(encoding="utf-8"))
        weeks.append(
            {
                **w,
                "questions": [
                    studyguide.inline_markdown(q, ref_class=True) for q in parsed["items"]
                ],
                "pdf_url": "guides/" + quote(guide_path.stem + ".pdf"),
            }
        )

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        autoescape=False,  # weeks.yml and the guides are trusted, first-party content
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
        keep_trailing_newline=True,
    )
    template = env.get_template("index.html.j2")
    return template.render(site=config.get("site", {}), weeks=weeks, total=len(weeks))


def main(argv: list[str]) -> int:
    html = render()

    if "--check" in argv:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != html:
            print("index.html is out of date - run: python build_index.py", file=sys.stderr)
            return 1
        print("index.html is up to date")
        return 0

    OUTPUT.write_text(html, encoding="utf-8", newline="\n")
    print(f"wrote {OUTPUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
