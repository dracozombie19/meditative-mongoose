# How to Read the Bible

Small group hub for a 19-week study through BibleProject's *How to Read the Bible* video series.

- `index.html` — the study hub: video links, related podcast episodes, and the discussion guide for each week, all on one page.
- `guides/` — the discussion guides, as both markdown source and print-ready PDF, one pair per week.

## Publishing

This is a static site with no build step. To serve it with GitHub Pages:

1. Push this repo to GitHub.
2. In the repo's **Settings → Pages**, set the source to the `main` branch, root folder.
3. The hub will be live at `https://<username>.github.io/<repo-name>/`.

## Updating a week's guide

Edit the markdown in `guides/`, then regenerate the matching PDF and re-check the discussion questions embedded in `index.html` match.
