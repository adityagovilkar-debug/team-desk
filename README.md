# Team Desk

A tracker for the two teams you oversee — the tickets they work, the people who work them,
and the institutional knowledge that otherwise evaporates.

Companion to Demand Desk. Same constraints: **one self-contained HTML file, no install,
no CDNs, fully offline.** Double-click `TeamDesk.html` in Edge.

Where Demand Desk tracks *your* work, Team Desk tracks *other people's work that you're
accountable for* — which is a different problem. Its three jobs:

1. Make you well-armed for the next call
2. Turn what you hear into durable memory
3. Make you credible with your boss

---

## Phase 1 (built)

### Tickets
One record per JIRA / ServiceNow ticket, tagged to a team. Portal Team and P&C IT are
colour-demarcated everywhere (blue / purple) and never mix by accident.

- **Quick-add** — ticket ID + title + team is enough. Alt+N. Everything else optional.
- **Filters only offer tags in use.** The tag vocabulary is curated, not auto-pruned — it
  deliberately holds tags nothing uses yet — but a *filter* offering a value that returns
  nothing is just a dead option. The ⋯ menu lists unused tags so you can drop them deliberately.
- **Multi-select status filter** — status chips with live counts. Click one to show only that
  status; **shift-click** to build a set. "New + In progress, skipping blocked and done" is two
  clicks. An explicit selection overrides the *Hide done* checkbox, so the two can't contradict.
- **Two status fields** — *their* status (free text, JIRA/SNOW wording varies) and *your*
  status. When they contradict each other, a banner says so. That disagreement is
  information.
- **Commitment ledger** — every ETA they give you is logged with the date they gave it.
  The card then shows `2026-07-10 → 2026-07-16 → 2026-07-23` and a `2× slipped` chip.
  No interpretation, just history — which is impossible to hold in your head across
  30 tickets and two teams.
- **Hurdles** as structured records (dependency / access / knowledge / vendor / decision /
  environment), each with owner, raised date, resolution and days-open. Resolving the last
  open hurdle automatically moves the ticket out of *Blocked*.
- **Updates** — the running narrative, each stamped with which sync it came from.
- **People & POCs** — who worked it, and which external contacts you had to consult.
- **Resolution card** — symptom / root cause / fix steps / time taken. This is the record
  you'll search when the lookalike ticket arrives.
- **Boss flag** + note, for the P&C IT items you need to brief upward on.

### Sync — the twice-weekly call screen
Start a sync and the **ask-about queue builds itself**, scored and ordered:

| Signal | Weight |
|---|---|
| ETA missed | 100 |
| Overdue | 60 |
| Open hurdle | 50 |
| Status mismatch | 45 |
| Never updated | 40 |
| Nothing since last sync | 30 |
| Quiet N+ days | 28 |
| New since last sync | 25 |
| Due within a week | 20 |

Each ticket shows *why* it's in the queue. The capture pane shows what they said last time,
warns about open hurdles, and takes the update, both statuses and a new ETA in one place —
**everything lands directly on the ticket**, so there's no re-typing after the call.
Ctrl+Enter saves and jumps to the next ticket.

**Tickets on the same epic are grouped in the queue**, because the call runs epic-first: the
epic comes up, then each ticket under it. A group is ordered by its *most urgent* ticket, so
grouping never buries something that needed asking. Click the epic header to open **one screen
for all its tickets** — your headline line for context, then a compact row each (what they
said, status, new ETA), with *Save all & mark covered* at the bottom. Depth — hurdles, gates,
POCs, decisions — stays one click away on the individual pane, which is untouched.

Closing a sync tells you what wasn't covered and what carries over. Open action points from
previous syncs appear at the top of the next one. Live syncs are persisted immediately, so a
crash mid-call loses nothing.

### People
The roster **builds itself** — type any name on a ticket and that person is created on that
ticket's team. Each person shows skill *evidence* derived from the tags on tickets they
actually worked (`Fiori ×2`), independent of any rating.

---

## Phase 2a (built)

### Skills & pairing
- **Your own 0–10 rating per skill**, with the date you gave it and an `observed` /
  `reported` confidence flag. Ratings older than six months are marked stale — otherwise the
  matrix quietly becomes fiction.
- **Full rating history.** Deepa going 4 → 7 on BTP renders as `7 ↑ from 4 (2026-06)` with
  the whole trail beneath. The trajectory tells you who to invest in; the number alone doesn't.
- Skills share the tag vocabulary, so a rating and its ticket evidence line up automatically.
- **Skill matrix** — people × skills, coloured by rating with evidence counts beneath,
  grouped by team, horizontally scrollable. Click a column to rank everyone for that skill
  across *both* teams, with current open load so you don't pair someone already buried.
- **Single point of failure** — skills exactly one person is rated 6+ on. Kept separate from
  merely *unrated* skills, because those are a blank to fill, not a risk.

### Observations
Dated records about a person: kind (commendation / concern / growth / note), what happened,
how you know (`I saw it` vs `Thomas told me`), and an optional ticket link.

- **Suggested from data you already captured** — a hurdle someone owned that sat open 38
  days, a ticket whose ETA moved three times, or work that came in well under estimate.
  Accept or wave it away; dismissals stick.
- **🔒 Excluded from every export by default.** You unlock an individual observation
  deliberately, with a confirmation. A performance concern can never ride along into a brief
  for your boss by accident.
- The entry form asks for *what happened and when*, not what someone is like — the dated,
  ticket-linked version is the one that holds up when a delivery slips and someone asks why.

### Epics
First-class and **cross-team** — LUCA spans P&C IT and Portal.

- **Your own headline line at the top**: the one sentence you'd say out loud if your boss
  asked right now, dated, with a nudge when it's more than two weeks old. Auto-summaries
  never say the thing you actually want to say.
- **Stated health vs implied health.** Mark LUCA green while a ticket is blocked and another
  is overdue and the screen says: *"You have this as On track, but the tickets read Off
  track — 1 blocked, 1 overdue."* Same idea as `myStatus` vs `theirStatus`, one level up.
- Rollup: counts, every open hurdle across the epic, tickets grouped by team then person.

### Plumbing
File System Access API (real `.json`) + IndexedDB / localStorage mirror, persistent file
handle with reconnect, 30s auto-save, daily snapshots (14 kept), defensive save guard,
optional AES-GCM master password (PBKDF2 200k) with snapshot re-keying and a 15-minute idle
lock, global search (Ctrl+K) across tickets, updates, hurdles, resolutions, people and syncs.

**Encryption matters more here than in Demand Desk** — this file names colleagues and tracks
their commitment history. Today shows a banner until you set a password.

---

---

## Phase 2b (built)

### Lookalike detection
The "this sounds familiar" instinct, automated — so it fires even when your memory doesn't.

IDF-weighted token overlap over every ticket and pattern. Rare words (`launchpad`, `catalog`)
count for far more than common ones; a stopword list strips the noise that appears in half
your tickets (`issue`, `error`, `user`, `system`…).

**Tags amplify textual similarity rather than substituting for it.** This matters: an earlier
version gave a flat bonus per shared tag, which let one broad tag (`Authorizations`) match a
launchpad-tiles pattern to an AC3 access request with *zero shared wording*. No shared words
now means no match, however many tags coincide.

It appears in two places:
- **Live in quick-add**, as you type the title — before the ticket even exists
- **On an open ticket's Work tab**, once there's a description and tags

Results **expand in place** to show the actual fix — mid-typing you want the answer, not a
navigation. Patterns rank above raw tickets (the hardened write-up beats the original), and
a ticket already filed under a pattern is suppressed so you don't see it twice.

Today gains a **"⟲ We may have solved this before"** card for open tickets that strongly
resemble solved work.

### Patterns
A resolution that has hardened — the same problem seen more than once, written up once
properly. Promote from any ticket's Resolution tab, or from a lookalike hit directly.

`ticketIds` are the sightings, so **"seen 3×" is derived** and can never drift out of step
with the links. A pattern carries its own tags, and the **contacts to ask** for that class of
problem — so next time nobody has to work out who to chase.

### Contacts
The external network that otherwise lives only in your head. Name, stack, org, how to reach
them, what they help with — filterable by stack, so *"who do I ask about SSO?"* is one click.
Each contact shows the tickets they were consulted on and the patterns they're the go-to for.

---

## Phase 3 (built)

### Boss Brief
Your recurring deliverable, generated. **Per-epic first, then loose tickets by team** —
the shape the conversation actually takes.

Sections: Programmes (each with *your* headline line quoted verbatim and dated, plus the
⚠ challenge if the tickets read worse than your stated health) · Needs a decision · By team ·
Risks · Closed this period · People notes. Each is a toggle; the period is 7/14/30 days or
everything, and the last generation date is remembered so "since last brief" works.

Output: live HTML preview, **Copy Markdown**, **download .md**, or **print → PDF**.

**Observations are locked out by three independent gates.** The People-notes section is off
by default; locked observations are excluded even when it's on; and unlocking one is a
per-observation toggle with a confirmation. Verified: a performance concern cannot reach a
brief by accident.

### Insights
Six charts, each answering exactly one question. Hand-rolled SVG — no CDN, offline.

| Chart | Question |
|---|---|
| Throughput | How much is each team actually closing per week? |
| Ageing of open work | What's rotting? |
| Where delays come from | What should I escalate? |
| Cycle time by tag | Is their estimate realistic? |
| Current load | Who's drowning? |
| Commitment reliability | How often does the first ETA hold? |
| Where the failures are | Which *kind* of failure does each team have? |
| Failure trend | Is their conduct improving? |

The last two appear only once something is logged in the Performance log, and they take the
cross-team cut deliberately — Performance → Patterns goes deep on one team, Insights compares
them and shows the trend.

Plus a KPI row (open / blocked / median days to close / first-ETA-met rate, and days lost to
failures once incidents exist). Every chart has hover + keyboard-focus tooltips and a
**table view** toggle for reading or pasting the numbers.

**On colour.** The team palette was validated with a contrast/CVD checker against this app's
own card surface, not eyeballed. The original pair — blue `#4ea1ff` and violet `#a97cff` —
measured **ΔE 1.1 under deuteranopia**: to a red-green colourblind reader the two teams were
the same colour. It's now blue `#3987e5` + magenta `#d55181` (CVD ΔE 15.9, normal-vision 26.5,
both ≥3:1 on the surface), and **team colour no longer carries identity alone anywhere** —
every ticket card names its team. Magnitude charts stay one hue because bar *length* carries
the value; colour is spent only where the job is telling series apart.

---

## Phase 4 (built) — oversight & reporting

### Delivery gates
Per-ticket checklists copied from editable templates (⋯ menu) — *ABAP/Fiori change*,
*Config/customizing*, *Analysis/spike* seeded. The strip shows passed gates in green with
dates and highlights the next open gate as "you are here", on both the Work tab and the
Sync capture pane. The sync question changes from "how's it going?" to "which gate are you
at?". Templates are copied at attach time, so editing one never rewrites ticket history.

### Evidence on done
One field: what proves this is done — transport number, test result, screenshot filename.
Closed-without-evidence gets an amber nudge. Searchable, so a transport number found in
JIRA six weeks later leads straight back to the ticket.

### No-movement signal
"Quiet" (no update text) and "stalled" (no update, no status change, no gate passed, no
hurdle activity, no new ETA) are different questions. Stalled is the sharper one — it feeds
a Today card, a 🧊 card chip, and outranks quiet in the sync queue. All status changes now
route through one `setStatus` so the signal can't be skipped. Threshold in ⋯ menu (14d).

### Talking points
Park "ask John about X" on a person; it surfaces in that team's next sync queue with a ✓,
on their card as a 🗣 badge, and in their detail. Replaces the mental note that evaporates
between Tuesday and Thursday.

### Decision log
Third tab in Knowledge: what was decided, by whom, when, optionally linked to a ticket/epic.
Loggable mid-sync (🧭 button in capture and notes). Feeds a **Decisions taken** section in
the Boss Brief. The "why did we route it through AC3?" answer, with a date and a name on it.

### Landing soon
Forward-looking brief section: everything the current ETAs say arrives in the next 14 days,
each line tinted by that ticket's promise history — *held so far / slipped once / slipped
N×, treat with caution / already late*.

### Reliability trend
Deferred by design — the ledger already retains every promise, so the quarter-over-quarter
view can be added once a few months of real data exist.

---

## Planned

Possible next steps, none committed:

- Tune the lookalike thresholds (`1.2` strip / `2.2` Today card) against a real corpus
- Tune `MENTION_SIM_MIN` (`0.45`) once there are real incident notes in the file
- Status history & dwell time — which would let the roll-call's "never empties" flag say whether
  it's the *same* pile, at least for the demands you track
- Vendor obligation chasing ("August hours not yet received")
- Person workload forecast
- A tools cockpit / launcher across Demand Desk, Team Desk and future apps (designed, not built)
- Trend arrows on the KPI tiles once there's enough history to compare periods

---

## Sync agenda — points to raise

Park a point to bring up in an **upcoming** sync for a team, added any time (e.g. the
morning before an afternoon call), optionally tied to a ticket. It surfaces in a **📋 To
raise** section at the top of that team's queue when you start the sync; tick it off when
raised (which also drops it into the meeting notes). Add from Today, the Sync picker, or
inside a live sync. Distinct from per-person **talking points** (🗣, "raise with John") —
agenda is team-level ("raise in the Portal sync").

## Vendor effort, capacity & approvals

For an **outsourced** team (mark it so in the ⋯ menu, with the firm's name), an **Effort** tab
appears — it only exists when a vendor team does.

- **Contract vs actuals.** Set contracted hours per quarter; log their monthly hours per
  demand (manual entry, as they send it). A KPI row and burn bar show *contracted · approved ·
  pending your approval · remaining*, with a per-demand breakdown.
- **Approval of hours.** Every logged line starts **pending your approval**; tick it, or
  "approve all" for a month. Matches the monthly sign-off you do against their Excel.
- **Forecast → the hours decision.** Record the vendor's forward forecast per quarter; the tab
  flags *"next quarter: forecast 560h vs contracted 480h — negotiate ~17% more"* (or reduce),
  which is exactly the increase/reduce call your forecasts are meant to inform.
- **Approvals log.** Their changes need your email sign-off to reach **Production** (plus the
  odd weekend patch or non-demand ask). Log each — kind, demand, requested date, status — for
  a dated record of what you approved and when. Prod approvals also show on the demand's own
  Work tab.

All of it feeds Today (pending approvals, pending hours, forecast flag) and the **Boss Brief**
(a "Vendor effort & capacity" section with the contract position and the forecast recommendation).

## Meetings (calls that aren't syncs)

The **Sync** tab is really a **Calls** hub. Alongside the structured status syncs, you can
**log a meeting** — an effort/governance talk, an epic review, a 1:1 — with the same points /
actions / decisions surface, minus the ticket queue, plus a **scope**: a team, an epic, and/or
specific people and demands.

- Its **actions feed Today's open action points** and its **decisions feed the Boss Brief**,
  exactly like a sync — nothing is siloed because it happened in a general call.
- **Its open actions also carry into that team's syncs, every sync, until closed.** An
  open commitment belongs to the team, not to the call that produced it: *"send next
  quarter's effort forecast"* keeps surfacing at the top of the Portal queue — labelled with
  the call it came from and how long it has been open — until you tick it off. You can close
  it straight from the queue, and it asks for the outcome while it's being said.
- Each action has a **⇄ carry toggle**. It defaults on, but a minor action from a call can be
  muted so it stays on Today without filling the sync queue.
- Scoped meetings surface where they belong: an epic-review meeting shows on that **epic's
  page**, a 1:1 shows on the **person's card**. Log buttons there prefill the scope.
- Recent syncs and meetings share one "Recent calls" list.

Built for cases like: a governance call with the (outsourced) Portal lead about effort and
next quarter's hours; an impromptu check-in on the DECOM epic; a 1:1 with a P&C person about
their demands.

## Performance log

Everything else in the app records *state*. This records **conduct** — how a team actually
fails, over months, with evidence.

The unit is an **incident**, and one real episode usually carries several distinct failures.
A single late delivery might be `late-response` → `missed-eta` → `false-done` → `untested` →
`misdiagnosis` → `deflection` → `escalation-only` → `customer-visible`. Tagging all of them is
what makes the pattern emerge: after ten incidents you can say *"seven involved a 'done' that
wasn't"* — with the incidents behind it.

Failure modes are grouped into **Communication · Commitment · Quality · Analysis · Effort ·
Process · Impact**, so the rollup answers *which kind* of failure this team has.

**Evidence assembles itself.** Link a demand and the incident automatically cites that demand's
ETA history, the hours logged against it, its hurdles and its dates — always current, straight
from your own records. You add only what the app can't know: the quote, the third party's
finding, what you saw.

**Facts and inference are kept apart.** *"Delivered 27-06, the tile did not render"* is
evidence. *"They never tested it"* is your reading. Both are recorded, in separate fields, and
the evidence pack labels the second as an inference — because the first is what survives being
challenged.

**Three detections** surface candidates from data you already have: an effort claim far above
comparable work, a demand with repeated broken ETAs, and work that sat for weeks then closed
within a day or two of the final commitment.

**Evidence pack** — a dated document (Markdown or print/PDF): totals, recurring modes, then
each incident with its sequence, evidence and cost. Deliberately separate from the Boss Brief,
so conduct never rides along in a routine status update.

One care taken throughout: an incident usually carries several modes, so per-mode day counts
**overlap and must not be summed**. Both the UI and the pack say so, and the headline totals are
the non-overlapping figures.

## Risk register

Hurdles belong to a ticket. Risks don't — *"the AD team is reliably slow"*, *"cutting Q4 hours
before LUCA is sized"*. Without a home those stay in a meeting note and resurface as a surprise.

Lives as a fourth tab in **Knowledge**: severity, status (open / mitigating / accepted / closed),
owner, what it is, what you're doing about it, and links to demands and epics.

- A **review date** — the register's whole value is that risks resurface. Overdue reviews land
  on Today, and one click pushes the date out 30 days.
- **High risks** and **review-due** risks appear on Today; live risks head the Boss Brief's Risks
  section, above the slipped-ticket list, each with its mitigation.
- Risks linked to an epic show on that epic's page.
- **Suggested from your data** — when the same *kind* of hurdle costs real time across several
  tickets, it stops being a ticket problem. The seeded data trips this: *"Access / auth delays
  are a recurring pattern — 46 days lost across 2 tickets."* Accept it and you get a risk with
  those demands already linked; dismiss it and it stays gone.

## Dependencies between tickets

You oversee two teams that hand work to each other, and that seam is where things stall. A
ticket can record **what it's waiting on**; the inverse ("what this holds up") is *derived*, so
the two halves can never drift apart.

- A banner on the Work tab names the blockers, and turns **red when the blocker belongs to the
  other team** — with the blocker's own slippage shown, so *"waiting on PC-8903 · P&C IT · 2×
  slipped"* tells you the whole story at a glance.
- When every blocker closes, the ticket flips to **"✅ unblocked — can start"**: a Today card and
  the top of the sync queue. That moment otherwise passes unnoticed.
- The **epic** page draws the dependency chain, flagging cross-team edges.
- Loops are impossible — the picker walks the chain and disables any choice that would create
  one, showing *"would loop"* rather than silently hiding it.

## Subtasks

A flat checklist inside one ticket — title, done, optional owner and note per step. Built for
the case where one unit of work has fixed phases: a **system decommission** as *analyse →
migrate ADS → decommission* lives in **one** ticket with three subtasks, instead of three
tickets. Progress (`☑ 2/3`) shows on ticket cards, in the sync queue, and — crucially — on
each ticket line in the **epic rollup**, so a "decommission N systems" epic is followable at
a glance. **⧉ Duplicate** (ticket detail, top-right) clones a ticket's structure — subtasks,
gates, tags, epic — with the history stripped and steps reset, so the next system is one
click, not a retype.

Subtasks are the ad-hoc breakdown of *this* ticket; **delivery gates** remain the standardized
pipeline checklist (dev → QA → prod) from templates. A ticket can have both.

## Roll-call — the numbers they read out

Most syncs open with headline counts rather than a walk through every demand: *"two blocked,
seven in validation, three in progress, one waiting."* Those numbers are now recorded per call,
per team, as the first row of the sync queue.

**They are recorded as a claim, not derived.** Team Desk already knows how many of *your* tickets
sit in each status, and charting that would have cost nothing — but it measures your tracking,
not their queue. They say seven in validation; you may only track four of those. Deriving the
figure would quietly answer a different question than the one asked in the call.

Their status names are a small managed list per team (`✎ statuses`), because "validation" one
week and "In validation" the next are two series, and the trend dies. The list is theirs, not
your five `myStatus` values.

**Entry is the whole design constraint.** The pane pre-fills last call's figures — most cells
don't change — so it's a few keystrokes during a live call. Typing any number records it; the
button is for the week nothing changed, where confirming is the deliberate act. That is also why
an untouched pre-fill is a *draft*: it is last week's data wearing this week's date, and it is
discarded when the sync closes rather than entering the trend as a fabricated data point.

Number inputs patch only the derived nodes around them rather than re-rendering the pane —
otherwise a re-render on `change` steals focus mid-tab, which in a live call is the difference
between usable and not.

Four readings, in descending order of usefulness:

| Reading | What it answers |
| --- | --- |
| **Flow** | In-progress falls, validation rises, done doesn't move → work is piling at a stage. The strongest signal weekly counts can give. |
| **Balance check** | They said 3 closed and 1 new, but the total didn't move. Arithmetic, dated, in your own record. |
| **Reconciliation** | Their declared count vs. what you track, per status. |
| **Level** | Total open over time. Least interesting; most often the only thing anyone tracks. |

The balance check is **silent unless both "closed since" and "new since" were stated** — with one
missing, arrivals confound the sum and the tool would be accusing them on incomplete numbers.
`""` and `0` are therefore stored as different things: didn't say, versus said none.

The reconciliation joins on **their** words: a ticket's `theirStatus` uses the same vocabulary the
roll-call does, so no mapping table is needed, and keeping `theirStatus` current suddenly pays for
itself. Open tickets whose `theirStatus` isn't in the list are counted and called out, so the
"you track" figures are never silently wrong.

### What counts deliberately cannot tell you

"2 blocked" every week looks stable, but the *same* 2 blocked for eight weeks is a completely
different story from 2 fresh ones each week — and counts alone cannot distinguish them. The tool
flags the softer, checkable version only: a status that **never drains and never really moves**
(`min ≥ 2` and `max − min ≤ 1` across at least 4 calls), and says in as many words that whether
it is the same items is exactly what it can't know. A bare floor test was tried first and flagged
"In progress", which is supposed to be non-empty and tells you nothing.

### Trend view

Insights carries one block per team: **small multiples** — one thin line per status, one panel per
row. A stacked area would hide the one thing that matters, which stage is filling while the others
drain. The status rows share a scale so they're comparable; totals and incident counts are
different quantities an order of magnitude larger and carry their own, or every status line
flattens onto the baseline. Single pen throughout — every panel is labelled, so colour would carry
no information and only risk another palette that fails on a deuteranope.

Below the lines sit the three readings, and the header states plainly that these figures are
self-reported by the party being measured. The Boss Brief repeats that caveat and lists every call
in the covered window whose arithmetic failed.

## Incidents raised in calls

They mention an incident, say they'll close it, and by the next call it's closed — with the answer
walking out of the room. These are logged as deliberately thin notes: what it was, the area, their
reference, and then the three fields that make it knowledge rather than a diary entry — **what
actually happened**, what they did, and what would stop it next time.

Two structural decisions:

**Not the performance log.** That one is boss-facing evidence about *conduct*, and filling it with
routine operational incidents would make "N incidents this quarter" meaningless. There is a
one-click **promote** for when the handling turns out to be the story — a false "closed", a missed
callback, no explanation at all — which carries the note across and cites itself as evidence.

**Not a ticket.** Tickets carry gates, promises, epics, assignees, dependencies and effort. A
mention needs four fields, and forcing it into `normTicket` would pollute every rollup — ageing,
portfolio, workload — with things that were never work you manage.

The mechanic that makes it work is the same one the action points use: **an unanswered note
follows you into every sync for that team until you write down what happened.** Marking it
*Closed, never explained* is the deliberate give-up — it stops the chase and records that they
never said, which is its own signal and its own count in Insights.

Notes run through their own similarity pass (`similarMentions`), so the fourth time the same
interface falls over you get told. It requires **two shared meaningful words minimum**, because a
single rare token matching is exactly how the ticket lookalikes produced false positives.
Recurring notes and unexplained ones surface to the Boss Brief; routine ones stay out.

## Sync capture — you mark covered, nothing else does

Moving between demands during a call never marks anything done — your notes are auto-saved and
restored when you come back. A demand is covered only when you click **✓ Mark covered** (or
Ctrl+Enter), and you can **↩ Reopen** one. Any notes typed but never marked covered are still
committed to their ticket when you close the sync, so nothing is lost.

## Quarterly vendor scorecard

**Effort → 📋 Quarterly scorecard** (also in the capacity header and the ⋯ menu). One team's
quarter on one page, for the contract or governance call, with every headline figure set against
the previous quarter so the conversation is about the trend: hours used against the contract,
demands delivered, share of ETAs met, incidents logged, and days lost.

Below the headline figures: hours by demand and next quarter's forecast; delivery (raised, delivered,
open, median days to close); **commitments** — every ETA that fell due in the quarter, judged one
at a time; the performance log (counts, most frequent failure modes, titles); the roll-call
(their reported total at the start and end of the quarter, and which calls didn't add up);
incidents raised in calls; open commitments from calls, split into owed by them and owed by me;
and approvals. Sections switch off individually, and the export has the same four outputs as
the Boss Brief.

How an ETA is judged (`etaOutcomes`): **met** if the work closed on or before that date;
**broken** if the date was pushed later, or passed with the work still open, or the work was
delivered late with no new date ever logged; **superseded** — not counted either way — if it was
replaced by an earlier or identical date. A date still in the future only counts once the work is
done. This is why the rate can differ from the ticket-level slip count: it scores each commitment,
not each ticket.

It deliberately carries **counts and titles** from the performance log but never the narratives or
your inferences — those stay in the evidence pack — and never anything from people's
observations. Open commitments are as of today, not the quarter, and the heading says so.

## Epic steering summary

**📄 Steering summary** on every epic. One epic in depth for its steering call; the Boss Brief
covers all epics in a few lines each. In order: the health you set (and a warning when the tickets
read worse) and your headline sentence; the figures; **what needs a decision** first; **what changed
since** — delivered, gates passed, steps finished, new tickets, ETAs moved either way, blockers
raised and cleared; blockers and cross-team dependencies; what lands in the next 30 days (and
what's already late); risks; decisions; open actions from the epic's meetings; and every ticket by
team.

"What changed since" defaults to the last time you exported a summary for that epic
(`epic.summaryOn`, set on copy / download / print), else the last epic-review meeting, else a
month back — so each month's summary starts where the last one ended.

Both documents share one shell (`openDocModal`) and paper styles that stay the same in every theme.

## Header on narrower windows

With nine tabs, the header outgrew windows under about 1100px and pushed **Save and the ⋯ menu
off-screen** — a bug from before the review pass, found while testing these documents. The file
buttons now never shrink; the search box gives way first (Ctrl+K still reaches it), then the tabs
tighten and Open/Save drop to icons. Checked at 1366, 1100, 987 and 900px in all three themes.

## Data safety

A review pass found several ways the app could destroy or misreport data. Each was reproduced
in the browser before it was fixed, and re-tested after.

**Opening the wrong file.** The "is this a Team Desk file?" check ran *after* `migrate()`, which
fills in every missing array — so any JSON passed. A Demand Desk file (or a `package.json`) opened
as an empty Team Desk, became the save target, and the next auto-save wrote Team Desk data over
it. The check now runs on the raw file (`looksLikeTeamDesk`: `tickets` and `people` arrays), and
an encrypted file whose envelope names another app is refused before decryption.

**Cancelling the startup unlock.** Cancelling left the app usable with an empty *placeholder*
state standing in for the encrypted data. Adding one ticket replaced the encrypted backup with a
plaintext one-ticket backup, and with a remembered file, auto-save wrote that over the real data
file 30 seconds later. The startup lock is now a veil over an inert app — the only ways out are
the right password or deliberately opening a different file — and nothing can be persisted while
it's up (`safeToPersist`, `saveGuardOk`, and every keyboard shortcut check for it).

**The idle lock** now makes the app underneath `inert` rather than just covering it: a covered
page still let Tab reach the controls behind the veil, and shortcuts still fired.

**Writes.** There is now one write path (`writeFile`):
- **Queued** — a manual save and an auto-save can't run two write streams against the file at once.
- **Edits during a write stay unsaved.** `dirty` used to be cleared after every write, so an edit
  landing mid-write was marked saved without ever reaching the disk (`editSeq`).
- **The file is checked before it's written.** Its size and modified time are recorded after each
  save; if they've changed since (another tab, OneDrive from another machine, a restored copy),
  auto-save pauses, the save status turns red, and you choose: load the file's version (yours is
  snapshotted first) or keep yours and overwrite. The same check runs when a remembered file is
  reconnected at startup.
- **An empty app never overwrites a full file.** If the local backup is missing or unreadable, a
  reconnected file is *loaded* rather than becoming the target of the next near-empty save. An
  unreadable backup is set aside instead of being overwritten.

**Half-typed text.** A field only reports a change when it loses focus, so text typed and never
tabbed out of was lost on close — and not even counted as unsaved, so the browser didn't warn.
Closing the tab, the idle lock, and Ctrl+S now commit the focused field first (Ctrl+S puts you
back where you were typing).

**Two copies open.** A banner appears in both when Team Desk is open in two tabs or windows,
since whichever saves last wins. It uses BroadcastChannel plus a localStorage heartbeat (file://
pages don't reliably get BroadcastChannel) and clears within a minute of one closing.

**Smaller ones.** *Download a copy* no longer marks the connected file as saved. Ctrl+S with a
remembered file reconnects to it instead of opening Save As. Restoring a snapshot taken before
encryption was switched on no longer switches it off, and the current data is snapshotted before
any restore or conflict load. The master-password dialog has explicit Change / Remove / Cancel
buttons (Cancel used to mean *remove encryption*). Esc closes dialogs, asking first if you've
typed something. The tab title shows ● while there are unsaved changes.

### Correctness fixes from the same pass

- **Reopened tickets stayed "closed".** Setting a Done ticket back to open kept its `closedDate`,
  so it appeared in the Boss Brief's *Closed this period*, counted in throughput, and had a cycle
  time. Reopening now clears it, and every closed-ticket figure checks `isClosed()` (done *and*
  dated), which also covers files saved before the fix.
- **Slip counting.** Every ETA revision counted as a slip, including dates brought *forward* or
  re-confirmed unchanged. A slip is now a date pushed later. Separately, a single ETA that had
  already passed with the work still open counted as "first ETA held" — `brokenETAs()` now counts
  it, and the reliability chart and *first ETA met* KPI use it. The ledger is ordered by when each
  date was given, so a back-filled older ETA no longer becomes "latest".
- **Deletes left dangling links** — a pattern kept counting a deleted sighting, a meeting kept a
  removed person — until the next reload. One `purgeDeadLinks()` now runs on load and after every
  delete, and also covers links `migrate` used to miss (assignees, observation → ticket).
- **Deleting a meeting deleted its decisions.** Decisions now stay in the log with the link
  cleared, which is what the decision log is for.
- **Stale sync panes.** Opening a call from Today, search, a person or an epic could reuse the
  roll-call pane left open on a *different* call, creating a roll-call draft there. Every way into
  a call now goes through `openCall()`.
- Skill rating: clicking a score wiped the skill name, date and note already typed.
- Pattern *First/Last seen* came from a list sorted by close date, so an open recurrence read as
  the first sighting.
- Status mismatch: "Incomplete" and "Not done" read as "they say it's done".
- An epic headline with text but no date was treated as fresh forever.
- Dates: the throughput axis was month-first (09/21); roll-call labels ended in a dash; the live
  sync banner, search results and the decision ledger showed ISO dates.
- Labels cut *after* escaping could show a broken entity (`P&am…`) — `clip()` cuts first.
- *hrs to approve* counted lines, not hours. Incident notes were missing from global search.

## Dates

Everything displays **day-first: `DD-MM-YYYY`**.

Dates are still *stored* as ISO `YYYY-MM-DD` — that's what makes date sorting and all the
since/until comparisons work — so only the display changes. Two helpers (`fmtDate`, `fmtMonth`)
handle it at render time.

The date-picker fields need a workaround worth knowing about: a native `<input type="date">`
always renders in the **browser's** locale (`mm/dd/yyyy` on an en-US machine), and neither the
`lang` attribute nor CSS can reorder it — both were tested and neither works. So the app masks
the native text and paints a `dd-mm-yyyy` label over it. The input element itself is untouched,
so its value stays ISO and the calendar picker still works normally.

## Bench — the default look (Paper + Backlit)

Team Desk now opens in **Bench**, the same look Demand Desk uses: an icon rail on the left
(with live counts — open tickets, live syncs, pending vendor approvals, incidents awaiting a
close-out), a status bar along the bottom (which file, saved or not, the auto-save countdown,
record counts), an animated dot wordmark that sweeps when a save lands, and a clock. **Paper**
is light, **Backlit** is dark; by default it follows Windows. The ☀/🌙 button flips light ↔
dark inside whichever family you picked; ⋯ Settings → Appearance picks any theme (Bench or the
three classic ones), the motion level, and an optional first name for the greeting.

**Today is a cockpit.** A greeting over a flow field whose streams are coloured by where your
tickets stand; Ctrl K search; one-click New ticket / Start or Resume sync / Point to raise /
Boss brief / Scorecard. Then four instruments read from your data: **Open tickets** (a dot ring
split by status), **ETAs & due dates** (a radar — distance from the centre is days past the
latest ETA), **Next sync** (countdown gauge + tickets queued), and **Vendor hours** (this
quarter's approved hours as dots, pending as rings, against the contract — or live risks by
severity if no team is outsourced). Below: a **delivery pipeline** (one lane per team, tickets
parked at New → In progress → Review → Done-in-30-days; red ring = blocked, red pulse = past its
ETA), **epic rings** (share of tickets done, in the epic's health colour), and a **10-week
calendar** (sync days, ETAs/due dates, action-point dues, risk reviews). Every "needs
attention" card from before sits underneath, unchanged.

**Pages.** A ticket opens with a header of readouts — raised, due, age, ETA (with slips),
gates, subtasks, open hurdles, last update — a segmented control for *my status* (the change
flies to its card in the list), and bands for a missed ETA, a blocker, or a boss flag. Updates
read as a timeline with month headers (ochre dot = captured in a sync, blue = typed by hand).
An epic page has a health segment, readouts (tickets/done/blocked/missed ETA/overdue/slipping/
target), the headline as an editable band, a disagreement band when the tickets read worse than
your call, and a two-column body: tickets by team and the dependency chain on the left; open
hurdles, risks and meetings beside them. Across every view, each titled section is framed as
its own panel.

Motion is decorative and optional: Settings → Motion *Off*, or Windows' "reduce animations",
stops all of it. Team colours were re-validated for both surfaces (Paper `#1B4FA0`/`#B07500`,
Backlit `#5B8DEF`/`#BB8514` — Bench's own ochre sat just outside the dark lightness band), and
the team mark keeps its shape (Portal a dot, P&C a ring). The classic themes render exactly as
before — no rail, no cockpit. Theme, motion and name live in `localStorage` only.

## Themes — dark, light, instrument

The classic themes, still available in ⋯ Settings. **Instrument** is a scientific-plotter look adapted
from the `instrument-white/` design system: warm-white paper with an engineering dot-grid,
hairline rules, registration tics on every panel, silkscreen micro-labels, mono tabular
figures, and **quantities drawn as discrete dots rather than filled bars**.

In instrument mode the six Insights charts and the vendor capacity meter re-render as dots —
verified as zero `<rect>` elements. The unlit track is always drawn, because it shows the
scale: the contract meter reads as *30 of 120 cells*, with approved hours filled and pending
hours as **rings** (claimed but not yet yours).

Two deliberate deviations from the source system, both forced by the data:

- **Its palette can't serve this app unmodified.** It has six pens, but three double as its
  state colours, and the warm three are mutually indistinguishable (ochre↔cinnabar measures
  ΔE 1.7 under deuteranopia). There's no way to get two team colours *and* three state colours
  all separable by hue. So they're split by **role**: prussian + ochre carry team identity
  (validated CVD ΔE 27.2, normal-vision 31.9), warm pens are reserved for state, and the team
  tick also differs in **shape** — Portal a filled dot, P&C a ring — so identity survives
  without relying on hue at all.
- **Its dot-column form is built for hundreds of dense samples.** Twelve weekly counts of 0–5
  rendered that way read as scattered specks, and a count of 1 against a max of 1 drew a *full*
  run. Small integer counts now get **one dot per unit** against a floor of 4, so "1 of 4" looks
  like 1 of 4.

Themes are presentational only — the choice lives in `localStorage`, never in your data file.

## Light / dark theme

A ☀/🌙 toggle in the header. The whole app is driven by CSS variables, so the switch
redefines one `[data-theme]` block and touches **no execution logic** — no function, data
model, or persistence path reads a colour. The choice lives in its own plain-localStorage key
(`teamdesk.theme`), deliberately **not** in the encrypted data file, so it applies on the
lock screen and never sits behind the master password.

The light palette isn't a naive flip: surfaces invert (white cards on a grey plane), hues are
deepened so they stay legible on white, and the six charts' colours were **re-validated
against a white surface** with the contrast/CVD checker — team pair `#2a78d6`/`#c1367a`,
ordinal ramp `#6da7ec`/`#2a78d6`/`#16457e`. The Boss Brief / Tech-Spec "paper" stays light in
both themes by design.

## Notes

- Tags are load-bearing: they drive lookalike detection, skill evidence and cycle-time
  analysis. The vocabulary is managed (canonicalised case-insensitively) and editable in
  the ⋯ menu.
- Sync days per team drive the countdown on Today (⋯ menu).
- Data file is separate from Demand Desk's by design — the two apps stay decoupled.

Preview: `python -m http.server 8142 --directory team-desk`
