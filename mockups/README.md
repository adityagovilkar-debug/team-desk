# Mockups

Proposed changes to Team Desk, shown on invented data before they go into the app.

| File | What it is |
|---|---|
| `sync-rehaul.html` | **The proposal** — Team Desk with the sync rehaul applied. Opens straight into a live Portal sync. |
| `sync-current.html` | The app as it is today, on the same data, for comparison. |
| `sync-rehaul.patch.py` | The change itself. Once approved: `python mockups/sync-rehaul.patch.py TeamDesk.html` |
| `mockdata.js` | The invented sample data (no real names, tickets or numbers; dates relative to today). |
| `build.py` | Rebuilds both pages from the current `TeamDesk.html`: `python mockups/build.py` |

Both pages are sandboxed: they keep their browser storage under their own names
(`tdmockup.*`) and never write to a file, so opening them cannot touch your real data.
Reload a page to start over.

Open them by double-clicking, or from a local server (`python -m http.server` in
`team-desk/`, then `/mockups/sync-rehaul.html`).
