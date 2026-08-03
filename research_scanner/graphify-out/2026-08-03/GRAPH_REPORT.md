# Graph Report - research_scanner  (2026-08-02)

## Corpus Check
- 46 files · ~20,579 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 300 nodes · 432 edges · 25 communities (16 shown, 9 thin omitted)
- Extraction: 75% EXTRACTED · 25% INFERRED · 0% AMBIGUOUS · INFERRED: 110 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8e47d6e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- get_db_connection
- score_unscored_theses
- run_scan_cycle
- parse_fact_check_note
- build_vault_index.py
- save_fetched_item
- research_scanner
- send_discord_notification
- PART 1 - CODE TO BUILD (send these five, in this order)
- init_db
- Research Scanner - Agent Task Prompts
- Vault Index
- context/README.md
- __init__.py
- sources/__init__.py
- tests/__init__.py
- Artificial Intelligence
- Machine Learning
- Quantum Computing
- Robotics
- Semiconductors
- test_scan.py

## God Nodes (most connected - your core abstractions)
1. `get_db_connection()` - 22 edges
2. `init_db()` - 17 edges
3. `save_fetched_item()` - 15 edges
4. `score_unscored_theses()` - 15 edges
5. `export_candidate_to_vault()` - 11 edges
6. `export_from_curator_decisions()` - 11 edges
7. `run_scan_cycle()` - 11 edges
8. `parse_fact_check_note()` - 11 edges
9. `compute_item_hash()` - 9 edges
10. `run_process_requests()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `test_run_scan_cycle_end_to_end()` --calls--> `run_scan_cycle()`  [INFERRED]
  tests/test_scan.py → scan.py
- `render_dashboard()` --calls--> `get_unreviewed_candidates()`  [INFERRED]
  dashboard.py → db.py
- `test_render_dashboard_min_score_filter()` --calls--> `render_dashboard()`  [INFERRED]
  tests/test_dashboard.py → dashboard.py
- `test_render_dashboard_stdout()` --calls--> `render_dashboard()`  [INFERRED]
  tests/test_dashboard.py → dashboard.py
- `run_process_requests()` --calls--> `compute_item_hash()`  [INFERRED]
  process_requests.py → db.py

## Import Cycles
- None detected.

## Communities (25 total, 9 thin omitted)

### Community 0 - "get_db_connection"
Cohesion: 0.11
Nodes (26): Connection, compute_item_hash(), get_all_candidates(), get_db_connection(), get_unconsumed_items(), get_unscored_ledger_entries(), is_item_fetched(), mark_candidate_reviewed() (+18 more)

### Community 1 - "score_unscored_theses"
Cohesion: 0.11
Nodes (29): get_all_thesis_scores(), Saves an immutable audit thesis record into thesis_ledger.     Returns True if s, Retrieves all records from thesis_scores JOINed with thesis_ledger metadata., save_thesis_ledger_entry(), add_trading_days(), calculate_cost_adjusted_return(), generate_scoring_report(), get_alpaca_price() (+21 more)

### Community 2 - "run_scan_cycle"
Cohesion: 0.06
Nodes (32): Entrypoint to process director requests. Polls the director_requests table and e, run_process_requests(), Main scan entrypoint for research_scanner. Runs one full fetch -> deduplicate ->, Executes one full fetch + triage cycle across all configured data sources., run_scan_cycle(), fetch_arxiv_items(), Any, arXiv API data fetcher using feedparser. (+24 more)

### Community 3 - "parse_fact_check_note"
Cohesion: 0.11
Nodes (25): get_all_ledger_entries(), Retrieves all thesis_ledger records sorted by id DESC., parametrize, fixture, Unit and integration tests for research_scanner.thesis_ledger module., temp_db(), temp_vault(), test_compute_ledger_hash() (+17 more)

### Community 4 - "build_vault_index.py"
Cohesion: 0.10
Nodes (23): build_vault_index(), extract_first_sentence(), extract_gist(), extract_h1_title(), main(), parse_note(), parse_yaml_frontmatter(), Any (+15 more)

### Community 5 - "save_fetched_item"
Cohesion: 0.08
Nodes (39): get_fetched_item_by_id(), get_unreviewed_candidates(), Any, Saves a newly fetched item into the fetched_items table.     Returns True if ins, Retrieves all unreviewed candidates (reviewed = 0 or NULL) scoring at or above m, Retrieves a fetched item by its database ID., save_fetched_item(), clean_filename_title() (+31 more)

### Community 6 - "research_scanner"
Cohesion: 0.12
Nodes (16): 1. Install Ollama & Pull Gemma Model, 1. Running the Fetch & Triage Scanner, 2. Install Python Dependencies, 2. Terminal CLI Dashboard (`dashboard.py`), 3. Environment & Credentials Configuration, 3. Exporting to Obsidian (`export_to_obsidian.py`), 4. Vault Thesis Ledger Scan (`thesis_ledger.py`), 5. Forward Performance Scoring & Statistical Report (`scoring.py`) (+8 more)

### Community 7 - "send_discord_notification"
Cohesion: 0.15
Nodes (13): main(), director_apply.py  Applies Director's JSON output deterministically., setup_logging(), Any, Discord REST notification dispatcher for research_scanner., Sends a Discord notification via direct REST POST to the specified channel., Sends a plain string message to Discord via REST POST.      :param content: The, send_discord_message() (+5 more)

### Community 8 - "PART 1 - CODE TO BUILD (send these five, in this order)"
Cohesion: 0.15
Nodes (12): Build 1: Ledger fixes (existing code - thesis_ledger.py, scoring.py), Build 2: Notifier generalization (existing code - notifier.py), Build 3: Archivist refactor (existing code - scan.py, db.py, config.py), Build 4: export_to_obsidian.py extension (existing code), Build 5: Director wrapper script (new code - director_apply.py), PART 1 - CODE TO BUILD (send these five, in this order), PART 2 - AGENT TASK PROMPTS (not code; use after Part 1 is built), Research Scanner: Multi-Agent Architecture (+4 more)

### Community 9 - "init_db"
Cohesion: 0.12
Nodes (18): main(), Terminal CLI dashboard for research_scanner. Lists unreviewed candidate items fr, Fetches and displays unreviewed candidates from the database in a terminal-frien, render_dashboard(), init_db(), Initializes the SQLite database schema if tables do not exist., fixture, Unit tests for research_scanner.dashboard module. (+10 more)

### Community 10 - "Research Scanner - Agent Task Prompts"
Cohesion: 0.33
Nodes (5): Research Scanner - Agent Task Prompts, Task A: Curator, Task B: Director, Task C: Analyst, Task D: Skeptic

### Community 11 - "Vault Index"
Cohesion: 0.40
Nodes (4): Audits, Raw Signals, Themes, Vault Index

### Community 23 - "test_scan.py"
Cohesion: 0.40
Nodes (4): fixture, Integration tests for research_scanner.scan entrypoint., temp_db_path(), test_run_scan_cycle_end_to_end()

## Knowledge Gaps
- **36 isolated node(s):** `Features`, `Prerequisites`, `1. Install Ollama & Pull Gemma Model`, `2. Install Python Dependencies`, `3. Environment & Credentials Configuration` (+31 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `init_db()` connect `init_db` to `get_db_connection`, `score_unscored_theses`, `run_scan_cycle`, `parse_fact_check_note`, `save_fetched_item`, `send_discord_notification`?**
  _High betweenness centrality (0.252) - this node is a cross-community bridge._
- **Why does `run_scan_cycle()` connect `run_scan_cycle` to `get_db_connection`, `init_db`, `save_fetched_item`, `test_scan.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `score_unscored_theses()` connect `score_unscored_theses` to `get_db_connection`, `init_db`, `send_discord_notification`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `get_db_connection()` (e.g. with `main()` and `run_process_requests()`) actually correct?**
  _`get_db_connection()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `init_db()` (e.g. with `render_dashboard()` and `main()`) actually correct?**
  _`init_db()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `save_fetched_item()` (e.g. with `run_process_requests()` and `run_scan_cycle()`) actually correct?**
  _`save_fetched_item()` has 10 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `score_unscored_theses()` (e.g. with `get_unscored_ledger_entries()` and `init_db()`) actually correct?**
  _`score_unscored_theses()` has 7 INFERRED edges - model-reasoned connections that need verification._