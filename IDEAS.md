# Team Desk — review and roadmap

A critical pass over the whole app (12 Nov 2026), using Demand Desk as the reference
for what has already worked (and broken) in a tool built the same way. Nothing here is
decided; pick, drop or reorder freely. Anything that changes how the app looks goes to
a mockup first, as with Demand Desk.

How the review was done: the code was read end to end (8,995 lines, 437 functions),
every screen was opened in Bench, and the app was timed on synthetic data — about five
years of use (2,500 tickets, 1,000 syncs, 300 meetings, ~15,000 updates, 5.7 MB) and
slices of it at 300, 600 and 1,200 tickets.

## What the measurements say

- **Unlike Demand Desk, Team Desk does get slow as the years pile up.** With five
  years of data: Today 2.7 s, the ticket list 0.55 s, opening a ticket 0.95 s, People
  0.2 s. Everything else stays under 0.1 s and search answers in ~9 ms.
- **Almost all of Today's time is one card:** "We may have solved this before" scores
  every open ticket against every past ticket, and rebuilds the word index from
  scratch for each one. With 123 open tickets: 0.39 s at 300 tickets, 0.71 s at 600,
  1.32 s at 1,200. With a more typical 30–50 open it is about a third of that — not
  felt today, felt within a year or two.
- **The ticket list draws every ticket, done ones included** (2,500 cards after five
  years), and is redrawn in full after every edit — so every change on a ticket costs
  the whole list.
- **Every single change rewrites the whole browser backup**, synchronously, to both
  stores (29 ms per change at five years). Demand Desk fixed exactly this in v45.
- **The animations never rest.** The Today instruments redraw at the screen's full
  frame rate even when nothing on them moves (about half a second of script every
  5 s, estimated). Team Desk copied Demand Desk's animation engine before Demand Desk
  found and fixed this (v45: 30 fps with focus, 10 behind other windows, none hidden,
  settled charts left alone).

## Bugs found

1. **Global search can't be clicked in Bench (or Instrument White).** The title bar
   and the page sit on the same layer and the page comes later, so it paints over the
   search results; a click in the results list lands on the page underneath. Bench
   has been the default since 28 Sep, so search has effectively been broken since
   then. One-line fix (lift the title bar above the page). **Demand Desk has the same
   CSS rule — check it there too.**
2. **An older copy of Team Desk silently strips newer data.** The data file carries no
   real version (every load stamps `version:1`), and each record is rebuilt field by
   field, so anything an older copy doesn't know about is dropped — and saved back
   that way. Verified: an extra field on a ticket does not survive a load. Demand Desk
   added a "this file is from a newer version" guard in v38.
3. **The lookalike scan, the full ticket list and the per-change backup** — the speed
   problems above; they are bugs in the sense that they get worse every week.
4. **Naming collisions.** "Incidents" means two different things — the Performance
   log's logged vendor failures, and Knowledge's incident notes from calls. "Patterns"
   also means two things — Knowledge's fix write-ups and the Performance log's failure
   patterns.
5. **Duplicated controls on the Bench ticket page.** The header has the status segment
   and the Raised/Due readouts; the Work tab underneath still has the old My status
   dropdown and the Raised/Due/Closed date fields.
6. **Readout grids with holes.** Insights (3 + 2 tiles) and Effort (3 + 1) wrap into
   uneven rows; the legends use squares while the charts use dots and rings.

## Decisions (answered 12 Nov 2026)

- **A — retire the classic themes: YES — done.** Bench (Paper / Backlit / Follow Windows) is the
  only look; a saved classic choice opens as Bench; the second copies of Today, the ticket header,
  the epic page and the Updates list are gone, with the classic colour blocks.
- **B — rename: YES — done.** Performance log entries are **Failures** (their rollup **Failure
  trends**); Knowledge's are **Incident notes**; "Incidents" is left only for the roll-call count.
- **C — Risks get their own place: YES — done.** A ⚠ item in the rail (count = reviews due);
  Knowledge keeps patterns, contacts, decisions and incident notes.
- **D — per-person review pack: NO.** Dropped.
- **Syncs are ~90% of the use** — Phase 2 is the priority, all of it, plus *last time* for the
  roll-call's incidents (below). Goes to a mockup first.

## Phase 0 — Fix what's broken (no visible change) — DONE 12 Nov 2026

1. ✓ Search results above the page (bug 1).
2. ✓ A data version and a "this file is from a newer Team Desk" guard (bug 2).
3. ✓ Lookalike index built once per change, not once per ticket — identical matches; at five
   years of data the whole Today screen draws in ~0.2 s (was 2.7 s).
4. ✓ Ticket list: done tickets older than 30 days folded behind "Show older". That alone made
   the whole-list redraw after an edit cheap (0.9 s → 0.07 s at five years), so the edit still
   redraws the list rather than only its card.
5. ✓ Backup about a second after changes stop, time-stamped, the newer copy loads,
   flushed when the window hides (Demand Desk v45).
6. ✓ The calmer animation loop (Demand Desk v45).

## Phase 1 — Foundations

7. **Source in modules, one HTML out** — `src/` + `build.py`, byte-identical first
   build, as Demand Desk did. The file is 690 KB and every change is an exact-text
   patch.
8. **A self-test** (`?selftest`) — Demand Desk runs 381 checks after every change;
   Team Desk has none, so every change is verified by hand.
9. **The app's own dialogs and Undo** — 23 browser confirm boxes and 4 prompt boxes.
   Deletes become "Deleted · Undo"; only irreversible ones still ask.

## Phase 2 — The sync loop (where most of your time in the app goes) — MOCKUP BUILT 12 Nov 2026, not applied yet

All of it is in `mockups/sync-rehaul.html` (compare `mockups/sync-current.html`); the change is
`mockups/sync-rehaul.patch.py` and goes into the app once approved. Data v3 (adds fields only).

10. ◐ **An agenda on Today** — under the greeting, one ordered list, late first: today's (or the
    live) sync with what's waiting in it, action points due, ETAs passed or due tomorrow (*Ask next
    sync* parks a point), approvals waiting, risk reviews (*Reviewed*), incident notes without a
    close-out. Ticking one offers Undo. The approvals, risk-review and incident-note cards fold
    into it; what remains is the **Watchlist**.
11. ◐ **Sync as an instrument** — a header over the call: live, team, title (click to rename),
    the buttons; covered as dots (the open ticket ringed); what's been captured this call
    (updates, ETAs, hurdles raised/cleared, actions, incident notes, roll-call); a running
    timer; and **Next up**.
12. ◐ **Keys during a call** — J / K next and previous, C covered, U type, E new ETA, H hurdle,
    A action, R roll-call, L last time, N notes, ? the sheet; while typing Alt+↓ / Alt+↑ move and
    Ctrl+Enter covers. A half-typed note is kept whichever way you move.
13a. ◐ **Last time, for the roll-call's incidents** — a *What they were* list (one line each,
    never marks the numbers recorded) and, below it, the previous call's lines with **Still
    there** (carries the line into today's list), **Gone**, or **Ask** (keeps their answer).
13. ◐ **Last time** — the first row of every sync's queue opens the previous call with that team:
    what changed on the tickets, what they said ticket by ticket, what they read out (with today's
    follow-ups on its incident lines), points, actions, decisions, incident notes.
13b. ◐ **A close sheet** instead of the confirm box — what changed in this call and what carries
    over; the recap is kept on the sync, and that is what the next call's Last time shows.
13c. ◐ **On a ticket, without leaving the call** — the ETA history (dates, slips), clear a hurdle
    in place (with how), add a hurdle or an action inline, my status as a segment, ‹ Prev / Skip ›.

## Phase 3 — People

14. **The person page in Bench** — a header with readouts (open tickets, ETAs kept,
    slips, hurdles owned, last 1:1, ratings age) and a timeline of observations, 1:1s,
    ratings and slips, instead of the Team/Role form at the top.
15. **1:1 prep** — open points from the last 1:1, observations since, their tickets'
    slips and wins, in one panel when you start a 1:1 meeting.
16. **Person workload forecast** — agreed earlier, still queued.
17. ~~A per-person review pack~~ — not wanted (decision D).

## Phase 4 — One coherent look

18. **Line icons instead of emoji** — ~325 emoji on screen across the views.
19. **The ticket page tidied** — no duplicated status/dates (bug 5); the Work tab in
    groups (What / When / Who / Delivery) with rarely used fields (estimated and actual
    hours, evidence) shown once they're used.
20. **Ticket list views** — saved-view chips ("Past ETA", "Blocked", "Waiting on the
    other team", "Mine to chase"), a quick filter, group by team / epic / status, sort
    by ETA / age / last update (Demand Desk v25).
21. **Insights full width** with a readout strip and legends that match the marks;
    the same strip on Effort (bug 6).
22. **Meetings and Sync get the Bench header** (Demand Desk v48).
23. **Knowledge regrouped** per decisions B and C.
24. **A "?" key sheet** and G-then-a-letter to move between workspaces.

## Phase 5 — Tracking and memory

25. **Status history & dwell time** — agreed earlier, still queued.
26. **Vendor obligation chasing** — agreed earlier, still queued.
27. **A readable copy every year** — everything as Markdown files by year, readable
    in Notepad if the app is ever gone (Demand Desk v49). On demand, not automatic.
28. **"Seen before" across everything** — the lookalike panel also searching incident
    notes, meetings and decisions, not only tickets and patterns.

## Suggested earlier — you passed on these (kept for reference)

- Pre-call template and paste-parser · CSV / paste import · attachments · email drafts
- SLA targets · hours reasonableness at approval · second-folder auto-backup
- Vendor action points counted as missed commitments
