# How to Read the Bible

Small group hub for a 19-week study through BibleProject's *How to Read the Bible* video series.

- `index.html` — the study hub: video links, related podcast episodes, and the discussion guide for each week, all on one page.
- `guides/` — the discussion guides, as both markdown source and print-ready PDF, one pair per week.

## Publishing

This is a static site with no build step. To serve it with GitHub Pages:

1. In the repo's **Settings → Pages**, set the source to the `main` branch, root folder.
2. The hub will be live at `https://dracozombie19.github.io/meditative-mongoose/`.

## Updating a week's guide

Edit the markdown in `guides/`, then regenerate the matching PDF with `build_study_pdfs.py` (requires Edge or Chrome installed):

```
python build_study_pdfs.py                                 # rebuild every guide in guides/
python build_study_pdfs.py "guides/Week 01 - What Is the Bible.md"   # rebuild just one
```

Re-check that the discussion questions embedded in `index.html` still match afterward — the hub inlines the guide text rather than linking out to the markdown.

## License

This content is licensed under [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — see [LICENSE](LICENSE).
