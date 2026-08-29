# How to Read the Bible

Small group hub for a 19-week study through BibleProject's *How to Read the Bible* video series.

- `index.html` — the study hub: video links, related podcast episodes, and the discussion guide for each week, all on one page. **Generated** from `weeks.yml` + the guide markdown; don't hand-edit it.
- `guides/` — the discussion guides, as both markdown source and print-ready PDF, one pair per week. Edit the `.md`; the `.pdf` is generated.
- `weeks.yml` — per-week metadata that isn't in the guides themselves: category, blurb, ordering, and the video / podcast links.
- `templates/index.html.j2` — the page shell the hub is rendered into.
- `studyguide.py` / `build_index.py` / `build_study_pdfs.py` / `build.py` — the build scripts.

## Publishing

This is a static site with no build step. To serve it with GitHub Pages:

1. In the repo's **Settings → Pages**, set the source to the `main` branch, root folder.
2. The hub will be live at `https://dracozombie19.github.io/meditative-mongoose/`.

## Setup (once per clone)

```
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # Windows
# .venv/bin/python -m pip install -r requirements.txt     # macOS / Linux

git config core.hooksPath .githooks                       # enable the pre-commit hook
```

`.venv/` is gitignored and holds the build-time deps (Jinja2 + PyYAML); the
published site itself has no runtime dependencies. The build scripts run under
whatever Python you invoke them with — activate the venv, or call
`.venv/Scripts/python build.py` directly.

The pre-commit hook prefers `.venv` automatically (falling back to Python on
`PATH`) and regenerates the derived files whenever their sources are staged —
the PDF for any changed guide, and `index.html` when a guide, `weeks.yml`, or
the template changes — staging the results into the same commit. PDF rendering
needs Edge or Chrome installed. Bypass with `git commit --no-verify`.

## Making changes

- **A week's questions, title, or intro** — edit `guides/Week NN - *.md`.
- **A week's blurb, category, or video / podcast links; the week order** — edit `weeks.yml`.
- **Page layout or styling** — edit `templates/index.html.j2`.

Commit, and the hook rebuilds everything. To regenerate by hand:

```
python build.py                    # everything: all PDFs, then index.html
python build_index.py              # just index.html
python build_index.py --check      # exit 1 if index.html is stale (no write)
python build_study_pdfs.py "guides/Week 01 - What Is the Bible.md"   # one PDF
```

## License

This content is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — see [LICENSE](LICENSE).
