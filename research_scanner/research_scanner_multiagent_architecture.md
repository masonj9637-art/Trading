# Research Scanner: Multi-Agent Architecture

Supersedes the earlier single-agent (Gemma-triage) draft. This document has
two distinct parts — don't mix them when sending to Antigravity:

**PART 1 — CODE TO BUILD.** Five prompts. Each one tells Antigravity to
write or modify actual Python files in the existing research_scanner
project. These are the only prompts needed to build the system out.

**PART 2 — AGENT TASK PROMPTS.** Four prompts. None of these involve writing
code. Each is pasted directly into a live Antigravity CLI session, where
Antigravity itself acts as the researcher/decision-maker and produces output
(JSON, a vault note, a verdict) — not source code. These are only usable
*after* Part 1 is built, and Analyst/Skeptic don't depend on Part 1 at all.

```
┌─────────────┐   requests    ┌───────────┐  raw dump  ┌─────────┐
│  Director   │──────────────▶│ Archivist │───────────▶│ Curator │
│(Antigravity │◀──────────────│  (local   │   SQLite   │(Antigrav│
│    CLI)     │  vault index  │  Qwen)    │            │ity CLI) │
└─────┬───────┘                └───────────┘            └────┬────┘
      │ escalate                                             │ writes
      ▼ (Discord)                                             ▼
  you decide ──manually trigger──▶ Analyst ──▶ Skeptic ──▶ Ledger
                                  (deep dive)  (fresh,     (scores
                                               fact-check)  outcomes)
```

All four LLM roles running through Antigravity CLI share the same Google AI
Pro quota (refreshes every 5 hours). Keeping Archivist local isn't just cost
management — it means Archivist's constant background fetching never
competes with Director/Curator/Analyst/Skeptic for that shared quota.

---

# PART 1 - CODE TO BUILD (send these five, in this order)

## Build 1: Ledger fixes (existing code - thesis_ledger.py, scoring.py)

```
This is EXISTING code in research_scanner: db.py already has correct
thesis_ledger/thesis_scores schema (immutable rows, per-horizon, baseline
comparison fields) - do not change the schema. Three real bugs need fixing
in thesis_ledger.py and scoring.py:

1. CRITICAL - scoring.py's get_alpaca_price() silently returns a fake,
   deterministically-generated mock price (hashed from ticker+date into a
   $50-$150 range) whenever Alpaca credentials are missing OR the API call
   fails for any reason, with no error raised above debug-level logging.
   Since thesis_ledger/thesis_scores rows are immutable once written, this
   means an expired API key or a transient failure would silently bake fake
   prices into the permanent record with no way to later distinguish real
   scores from fabricated ones. FIX: remove the mock-price fallback from the
   live scoring path entirely. If a real price can't be retrieved, log an
   ERROR, skip that ledger entry for this run (leave it unscored, to retry
   next run), and do NOT write a thesis_scores row. A mock-price mode may
   exist ONLY behind an explicit --mock flag used solely in unit tests,
   never as a silent default in scoring.py's normal execution path.

2. scoring.py's BASELINE_TICKER_POOL is currently a fixed list of mega-caps
   (SPY, AAPL, MSFT, etc.) - this doesn't test what it's supposed to test.
   Replace it with a function that pulls a random ticker from the
   fetched_items table (the same source universe Curator/Director actually
   draw from) that was fetched around the same time but never promoted to a
   note - i.e. an item that cleared Archivist's fetch but not Curator's
   relevance bar. This makes the baseline a genuine test of whether
   Curator/Director's judgment adds value over the raw fetch pool, not a
   test of general market beta.

3. thesis_ledger.py's parse_fact_check_note() already does frontmatter-first
   parsing (correct), but its regex fallbacks (for notes written before the
   frontmatter requirement existed) have two bugs: the confidence_level
   regex requires literal "Confidence:" and misses "Confidence Level:"
   phrasing; the fact_check_verdict fallback infers "Supported" / "Refuted"
   / "Inconclusive", which don't match the three actual required verdict
   phrases ("claims well-supported" / "some claims overstated" / "claims
   not well-supported by sources"). Fix both regexes to match the real
   phrasing patterns, keeping frontmatter as the primary source and these
   as fallback-only for legacy notes.

Do not otherwise change scan_vault_and_update_ledger(), the CLI entrypoints,
or the existing horizon-eligibility date math - those are correct as-is.
```

---

## Build 2: Notifier generalization (existing code - notifier.py)

```
notifier.py's send_discord_notification() currently hardcodes its message
content to the old candidate schema (score, source, category, reason, url).
Add a second function send_discord_message(content: str, bot_token=None,
channel_id=None) that reuses the exact same REST POST mechanics (URL
construction, auth header, timeout, error handling - none of that changes)
but accepts a plain pre-formatted message string instead. This is what
Director's wrapper script uses for escalations and proactive check-ins,
which don't fit the fixed candidate-score format. Keep
send_discord_notification() as-is for any legacy callers.
```

---

## Build 3: Archivist refactor (existing code - scan.py, db.py, config.py)

```
This is an EXISTING project called "research_scanner" (attached). Its current
scan.py does fetch -> dedupe -> call triage_item() via local Ollama -> save
to a "candidates" table (with score/reason/category) -> fire Discord directly
if score >= threshold. This conflates fetching and judgment in one step -
we're separating them.

Refactor as follows:

1. In scan.py: REMOVE the triage_item() call, the score-threshold check, and
   the send_discord_notification() call entirely. After dedupe and
   save_fetched_item(), the cycle is done - Archivist's job stops at
   recording raw fetched items. Delete triage.py and test_triage.py; this
   task moves to a separate Curator agent that does not run as Python code
   calling an API - it runs as a direct Antigravity CLI invocation instead
   (see Part 2 of this document, not something this build task needs to
   implement).

2. In db.py: add a "consumed_by_curator" column (INTEGER DEFAULT 0) and a
   "request_id" column (nullable) to the existing fetched_items table, plus
   corresponding get_unconsumed_items() / mark_item_consumed() functions
   mirroring the existing get_unreviewed_candidates() /
   mark_candidate_reviewed() pattern already used for candidates. The
   "candidates" table and its score/reason/category fields are no longer
   populated by Archivist going forward - leave the table and its existing
   functions in place for backward compatibility with old data, but nothing
   new writes to it from this point on.

3. Add a new director_requests table (id, query, source_hint, status
   [pending/fetched/no_results], requested_at) and a new
   process_requests.py entrypoint that polls it, executes each pending query
   against the existing arxiv/uspto/currents source modules unchanged, calls
   save_fetched_item() with request_id set, and updates status. If nothing
   substantive is found, mark "no_results" honestly rather than stretching a
   weak result to look complete.

4. Leave sources/arxiv.py, sources/currents.py, sources/uspto.py, and the
   dedup logic in db.py completely unchanged - they already work correctly.

5. In config.py: update GEMMA_MODEL's default from "gemma2:2b" to the actual
   model Archivist now uses ("qwen3.5:9b" or the exact Ollama tag for
   Qwen 3.5 9B Q4_K_M - verify current tag name against Ollama's library).
   SCORE_THRESHOLD is no longer used by anything and can be left in place
   for backward compatibility but isn't read by the new pipeline.

Do not have Archivist write to Obsidian or judge relevance - that's Curator's
job now (a task prompt, not code - see Part 2), reading fetched_items where
consumed_by_curator = 0.
```

---

## Build 4: export_to_obsidian.py extension (existing code)

```
This is an EXISTING module in research_scanner. Its current
export_unreviewed_candidates() reads from the "candidates" table by score
threshold and calls export_candidate_to_vault() for each. Do NOT change
export_candidate_to_vault()'s file-writing mechanics - its collision handling
(numeric suffix on filename clash) and its write-then-verify-then-mark
ordering (only mark consumed after os.path.exists + getsize > 0 confirms the
write) are already correct and must be preserved exactly, just repointed at
the new data model.

Changes needed:

1. Add a new function export_from_curator_decisions(decisions_json_path,
   db_path, vault_path) that reads a JSON file (produced by a separate
   Curator agent invocation - see Part 2, not code this task needs to write)
   containing a list of: { fetched_item_id, category, reasoning,
   escalation_theme (optional) }. For each decision, look up the
   corresponding row from fetched_items (not candidates), then reuse the
   existing get_folder_for_source(), format_theme_title(),
   ensure_theme_note_exists(), slugify_title(), and the collision-handling
   file-write block from export_candidate_to_vault() - refactor that
   function to accept category/reasoning as parameters instead of reading
   candidate["score"]/candidate["reason"], so both the old candidates path
   (kept for backward compatibility) and the new decisions path can share
   the same write logic.

2. Update generate_candidate_note_content() (rename acceptable, e.g.
   generate_note_content()) to drop the numeric "Triage Score" line and
   "Gemma Triage Reason" header - replace with the category and Curator's
   reasoning text, tied to whatever current-priorities.md said at the time
   (Curator's reasoning field should already reference this). If
   escalation_theme is present in the decision, add a second wikilink
   connecting this note to that theme as a supporting-research connector,
   in addition to the category theme link.

3. After a successful write, call mark_item_consumed() (from Build 3's
   db.py changes) on the fetched_items row - using the same
   write-then-verify-then-mark ordering already in place.

4. Add CLI entrypoint: python export_to_obsidian.py --decisions
   path/to/curator_decisions.json (alongside the existing --min-score path,
   which can remain for any legacy unreviewed candidates).
```

---

## Build 5: Director wrapper script (new code - director_apply.py)

```
Add a new module director_apply.py to research_scanner. This reads Director's
JSON output (produced by a headless Antigravity CLI run - see Part 2, not
something this task needs to invoke, only to consume its saved output file)
and applies it deterministically. Director itself never writes to the vault,
database, or Discord directly - this script is the only thing that does.

Expected input JSON schema:
{
  "updated_priorities": optional string,
  "fetch_requests": optional list of {"query": str, "source_hint": str},
  "escalation": optional {"theme": str, "message": str, "vault_note_path": str},
  "proactive_message": optional string
}

Behavior:
1. If updated_priorities is present, overwrite current-priorities.md in the
   vault root with it (keep a dated backup of the previous version rather
   than just discarding it, in case a bad run needs to be rolled back).
2. For each entry in fetch_requests, insert a row into the director_requests
   table (status="pending") using the existing db.py connection pattern -
   reuse Build 3's db functions, don't duplicate the schema logic.
3. If escalation is present, call notifier.send_discord_message() (from
   Build 2) with a formatted version of its message (include the theme and,
   if vault_note_path is present, a note pointing to it).
4. If proactive_message is present (and escalation is not - don't send two
   messages in one run), call notifier.send_discord_message() with it
   directly.
5. Log every action taken (priorities updated, N requests queued, message
   sent) to a run log, and handle a malformed or unparseable JSON input by
   logging the raw output and exiting non-zero rather than partially
   applying a broken decision.

CLI entrypoint: python director_apply.py --input director_output.json
Designed to be called immediately after each scheduled headless Director run
in the same cron job, e.g.:
  python build_vault_index.py \
    && antigravity -p --prompt-file director_prompt.md --output-format json \
    < /dev/null > director_output.json \
    && python director_apply.py --input director_output.json
```

---

# PART 2 - AGENT TASK PROMPTS (not code; use after Part 1 is built)

## Task A: Curator (Antigravity CLI, invoked whenever Archivist has unconsumed items)

```
You are Curator, part of an existing project called research_scanner. Read
rows from the fetched_items SQLite table where consumed_by_curator = 0, and
read current-priorities.md in the vault root for what Director currently
cares about. Decide which raw fetched items are worth promoting into real
Obsidian notes.

Do NOT write files yourself. Output a JSON decision list - for each item
you're promoting: its fetched_items id, a normalized lowercase category
(reuse an existing theme category when the topic genuinely matches one,
don't invent near-duplicates), your reasoning tied explicitly to
current-priorities.md, and, if the item's request_id is set, which
escalation/theme note this finding supports and what specific claim it
addresses. A separate script (export_to_obsidian.py's new
export_from_curator_decisions function, Build 4) performs the actual file
writes and marks items consumed from your decision list.

Be a genuine filter, not a rubber stamp - a mechanical fetch of 200 arXiv
results is not 200 findings; most of it was never actually looked at by
anyone until now. Only include what you'd stand behind as worth Director's
or a human's time. Items you don't include in your decision list simply
remain unconsumed and unpromoted - still available in SQLite for audit, not
cluttering the vault.
```

---

## Task B: Director (Antigravity CLI, scheduled headless - see runtime logistics below)

```
You are Director, the strategic mind of a research monitoring system. You run
periodically, not continuously - each run, you read the current state of the
vault and decide what happens next.

Each run, do the following:

1. Read the vault INDEX (a maintained summary file, not full note text) plus
   current-priorities.md and anything in the context/ folder (files the user
   has deliberately placed there for you to be aware of - this is your only
   source of outside context about the user; you do not have general
   filesystem access).

2. Decide what's actually interesting, missing, or worth digging into
   further. Every 5th run, set aside your own prior threads first and
   evaluate the most recent unconsumed raw findings and new theme notes on
   their own merits before returning to anything you were already pursuing -
   this exists specifically to stop you from just reinforcing your own past
   interests instead of reassessing them.

3. Update current-priorities.md if your priorities have genuinely shifted.

4. Request 2-3 new fetches (batched, not one at a time) - specific,
   well-scoped queries, not vague topic names.

5. Decide whether anything currently in the vault is worth escalating to the
   user via Discord. This is a real judgment call, not a threshold - use your
   actual assessment of significance, and say why in the notification.

6. You are also encouraged to reach out via Discord even without a clear
   escalation, when it's genuinely useful: you've been stuck on the same
   thread for several runs and want redirection, you found nothing worth
   escalating and want to say so plainly rather than go silent, or you
   noticed a pattern connecting two things that's worth a question rather
   than a conclusion. This is a real communication channel, not just an
   alert siren - use it like one.

7. If any theme/thread has had no new activity in 60+ days, condense it: keep
   the theme note but archive its detail so future runs of yours don't have
   to keep re-reading full context on it every time.

Output your decisions as a single JSON object with exactly this schema (omit
keys with no content this run rather than including empty values):
{
  "updated_priorities": "full replacement text for current-priorities.md, only if changed",
  "fetch_requests": [{"query": "...", "source_hint": "arxiv|patents|news"}],
  "escalation": {"theme": "...", "message": "...", "vault_note_path": "..."},
  "proactive_message": "a Discord message with no escalation attached, e.g. a status check-in or redirect request"
}
Do not take any action directly beyond producing this JSON. A separate
deterministic script (director_apply.py, Build 5) applies it. This keeps
your own permissions minimal and everything you decide auditable before it
takes effect.
```

**Director runtime logistics**: authenticate once interactively (antigravity
login) before any headless use. Set scoped permissions in
~/.gemini/antigravity-cli/settings.json (read-only on vault/context, write
only to a scratch output path) - never --dangerously-skip-permissions for an
unattended process. Cron roughly every 5-6 hours (matching the Pro quota
refresh window):

  python build_vault_index.py \
    && antigravity -p --prompt-file director_prompt.md --output-format json \
    --no-color < /dev/null > director_output.json \
    && python director_apply.py --input director_output.json

Headless runs are stateless by default (no --continue) - correct here, since
Director's real memory is the vault and current-priorities.md, not
conversation history.

---

## Task C: Analyst (Antigravity CLI, manually triggered - no dependency on Part 1)

```
I want you to research and draft an investment thesis audit for [theme or
company name], to be added to my Obsidian vault as a new note in the
audits/ folder, linked back to the [[Theme Name]] note via wikilink.

Research recent 10-K/10-Q filings language, earnings call themes, patent
activity, hiring trends, and competitive positioning for this theme/company.

Structure the output with these REQUIRED sections, in this order:
1. Thesis Summary (2-3 sentences)
2. Supporting Evidence (bullet list, each bullet cites its source)
3. Valuation Snapshot (current multiples vs. sector/historical average, if
   available)
4. Bear Case - REQUIRED, argued with equal rigor to the bull case, not a
   token paragraph. If you genuinely cannot construct a serious bear case,
   say so explicitly and treat that inability itself as a red flag.
5. Confidence Level (low/medium/high) with your reasoning

REQUIRED - end the note with a literal YAML frontmatter-style block using
exactly these keys:
---
ticker: [TICKER]
audit_date: [YYYY-MM-DD, today's date]
confidence_level: [low/medium/high - lowercase, single word]
theme_note: [Theme Name]
---

This produces analysis only - no buy/sell recommendation, no action. Flag
clearly anywhere you had to guess, couldn't verify a figure, or ran out of
good sources - don't smooth over gaps to look more complete than the
research actually was.
```

---

## Task D: Skeptic (Antigravity CLI, fresh session, manually triggered - no dependency on Part 1)

```
IMPORTANT: this must run in a fresh session with no access to any prior
audit, summary, or conclusion about this company/theme. If you have any
memory of having analyzed this before, disregard it and work only from what
I give you below.

Here are the raw sources for [company/theme]: [paste the actual filing
excerpts, transcript excerpts, or links the audit cited - not the audit's
summary of them].

1. Before looking at anything else, independently build your own bear case
   for this thesis from scratch, based only on the raw sources above.
2. Given this claim list from a separate audit: [paste the audit's
   Supporting Evidence bullets only], verify each one against the raw
   sources and flag any that are unsupported, overstated, or not actually
   present in the source text.
3. Compare your independently-built bear case (step 1) to the audit's stated
   bear case: [paste it here] - note where they agree or diverge, and
   whether the audit's version omitted anything yours identified.
4. Give an overall verdict, using EXACTLY one of these three phrases,
   verbatim: "claims well-supported" / "some claims overstated" / "claims
   not well-supported by sources"

REQUIRED - end your output with:
---
fact_check_verdict: [one of the three exact phrases above]
---

Analysis only - no recommendation beyond the verdict categories. I'll paste
this into the "## Independent Fact-Check" section of the audit note.
```
