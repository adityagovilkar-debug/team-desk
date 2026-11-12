# Mockups

Proposed changes to Team Desk, shown on invented data before they go into the app.

## Sync rehaul — approved and APPLIED 12 Nov 2026

| File | What it is |
|---|---|
| `sync-rehaul.html` | The approved mockup — kept as a record of what was signed off. |
| `sync-current.html` | The app as it was before, on the same data. |
| `sync-rehaul.patch.py` | The change itself — applied to `TeamDesk.html`; running it again fails safely (every replacement must land exactly once). |
| `mockdata.js` | The invented sample data (no real names, tickets or numbers; dates relative to today). Still useful for trying the app. |
| `build.py` | Built both pages from the app *before* the rehaul. To rebuild them, run it against that version: `git show 1e856f9:TeamDesk.html`. |

The two `.html` pages can be deleted now that the change is in the app; git history keeps them.

Both pages are sandboxed: they keep their browser storage under their own names
(`tdmockup.*`) and never write to a file, so opening them cannot touch real data.
