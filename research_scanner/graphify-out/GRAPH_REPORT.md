# Graph Report - research_scanner  (2026-08-03)

## Corpus Check
- 76 files · ~58,941 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 467 nodes · 612 edges · 52 communities (41 shown, 11 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 130 edges (avg confidence: 0.8)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eafdce80`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma
- score_unscored_theses
- run_scan_cycle
- parse_fact_check_note
- build_vault_index.py
- get_db_connection
- research_scanner
- patch
- PART 1 - CODE TO BUILD (send these five, in this order)
- init_db
- Research Scanner - Agent Task Prompts
- Vault Index
- context/README.md
- __init__.py
- sources/__init__.py
- tests/__init__.py
- current-priorities.md
- Artificial Intelligence
- Machine Learning
- Quantum Computing
- Robotics
- Semiconductors
- test_scan.py
- Advancements in magnetic steering of soft magnetic continuum robots for medical applications
- Advocating the potential of AI for syndrome discovery: a scoping review
- Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review
- Artificial Intelligence in Plant Sciences
- Artificial Intelligence in Plant Sciences
- Assessing the Role of Digital Transformation in Strengthening Customer Engagement: A Case Study of bKash
- Avaliação tomográfica do seio frontal no dimorfismo sexual
- Code and Experimental Data for Feasibility-Oriented Dung Beetle Optimization for Collision-Constrained Robotic Path Planning
- Combating foreign bribery and corruption : an integrated corporate governance, sustainability, and artificial intelligence approach
- Des villes en pixels aux cités réelles : influence des jeux vidéo sur l’architecture urbaine contemporaine
- DESIGNING AND EXPERIMENTING AS THE NEW WAY OF LEARNING – EDUCATIONAL INNOVATION FOR MORE RELEVANCE IN THE AGE OF AI
- Development of an Advanced Artificial Intelligence-based Model (Deep Business Analytics) for Managing and Improving Control and Decision Making in Modern Organisations: Application in a Hospital Clinical Laboratory
- Enabling Next-Generation Power Conversion: Design, Dynamic Characterization, and Application of Gallium Nitride Bidirectional Switches
- Feature Importance and Growth Rate Prediction in SiC PVT Processes through Advanced Machine Learning Models
- Funding Innovation for Future-Ready Healthcare Systems
- Funding Innovation for Future-Ready Healthcare Systems
- L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition
- Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France
- Mechs
- MODELING HOSPITALITY AND TOURISM STRATEGIES
- On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning
- Places and Non-Places for Language
- Progress of major emitters towards climate targets: 2025 Update
- Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap
- Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)
- General Technology

## God Nodes (most connected - your core abstractions)
1. `get_db_connection()` - 22 edges
2. `init_db()` - 17 edges
3. `save_fetched_item()` - 15 edges
4. `score_unscored_theses()` - 15 edges
5. `export_from_curator_decisions()` - 12 edges
6. `run_scan_cycle()` - 12 edges
7. `export_candidate_to_vault()` - 11 edges
8. `run_curator_export_step()` - 11 edges
9. `parse_fact_check_note()` - 11 edges
10. `run_process_requests()` - 10 edges

## Surprising Connections (you probably didn't know these)
- `run_continuous_daemon()` --calls--> `build_vault_index()`  [INFERRED]
  run_daemon.py → build_vault_index.py
- `render_dashboard()` --calls--> `get_unreviewed_candidates()`  [INFERRED]
  dashboard.py → db.py
- `test_render_dashboard_min_score_filter()` --calls--> `render_dashboard()`  [INFERRED]
  tests/test_dashboard.py → dashboard.py
- `test_render_dashboard_stdout()` --calls--> `render_dashboard()`  [INFERRED]
  tests/test_dashboard.py → dashboard.py
- `test_compute_item_hash()` --calls--> `compute_item_hash()`  [INFERRED]
  tests/test_db.py → db.py

## Import Cycles
- None detected.

## Communities (52 total, 11 thin omitted)

### Community 0 - "We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Summary / Abstract, We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma

### Community 1 - "score_unscored_theses"
Cohesion: 0.11
Nodes (29): get_all_thesis_scores(), Saves an immutable audit thesis record into thesis_ledger.     Returns True if s, Retrieves all records from thesis_scores JOINed with thesis_ledger metadata., save_thesis_ledger_entry(), add_trading_days(), calculate_cost_adjusted_return(), generate_scoring_report(), get_alpaca_price() (+21 more)

### Community 2 - "run_scan_cycle"
Cohesion: 0.06
Nodes (38): compute_item_hash(), is_item_fetched(), Checks whether an item with the given hash has already been stored in fetched_it, Computes a deterministic SHA256 hash for deduplication given a source and extern, Entrypoint to process director requests. Polls the director_requests table and e, run_process_requests(), Main scan entrypoint for research_scanner. Runs one full fetch -> deduplicate ->, Executes one full fetch + triage cycle across all configured data sources. (+30 more)

### Community 3 - "parse_fact_check_note"
Cohesion: 0.11
Nodes (25): get_all_ledger_entries(), Retrieves all thesis_ledger records sorted by id DESC., parametrize, fixture, Unit and integration tests for research_scanner.thesis_ledger module., temp_db(), temp_vault(), test_compute_ledger_hash() (+17 more)

### Community 4 - "build_vault_index.py"
Cohesion: 0.10
Nodes (23): build_vault_index(), extract_first_sentence(), extract_gist(), extract_h1_title(), main(), parse_note(), parse_yaml_frontmatter(), Any (+15 more)

### Community 5 - "get_db_connection"
Cohesion: 0.06
Nodes (61): Connection, get_all_candidates(), get_db_connection(), get_fetched_item_by_id(), get_unconsumed_items(), get_unreviewed_candidates(), get_unscored_ledger_entries(), mark_candidate_reviewed() (+53 more)

### Community 6 - "research_scanner"
Cohesion: 0.12
Nodes (16): 1. Install Ollama & Pull Gemma Model, 1. Running the Fetch & Triage Scanner, 2. Install Python Dependencies, 2. Terminal CLI Dashboard (`dashboard.py`), 3. Environment & Credentials Configuration, 3. Exporting to Obsidian (`export_to_obsidian.py`), 4. Vault Thesis Ledger Scan (`thesis_ledger.py`), 5. Forward Performance Scoring & Statistical Report (`scoring.py`) (+8 more)

### Community 7 - "patch"
Cohesion: 0.08
Nodes (38): Exception, Any, Sends a Discord notification via direct REST POST to the specified channel., send_discord_notification(), patch, get_curator_prompt(), is_quota_error(), main() (+30 more)

### Community 8 - "PART 1 - CODE TO BUILD (send these five, in this order)"
Cohesion: 0.15
Nodes (12): Build 1: Ledger fixes (existing code - thesis_ledger.py, scoring.py), Build 2: Notifier generalization (existing code - notifier.py), Build 3: Archivist refactor (existing code - scan.py, db.py, config.py), Build 4: export_to_obsidian.py extension (existing code), Build 5: Director wrapper script (new code - director_apply.py), PART 1 - CODE TO BUILD (send these five, in this order), PART 2 - AGENT TASK PROMPTS (not code; use after Part 1 is built), Research Scanner: Multi-Agent Architecture (+4 more)

### Community 9 - "init_db"
Cohesion: 0.09
Nodes (21): main(), Terminal CLI dashboard for research_scanner. Lists unreviewed candidate items fr, Fetches and displays unreviewed candidates from the database in a terminal-frien, render_dashboard(), init_db(), Initializes the SQLite database schema if tables do not exist., main(), director_apply.py  Applies Director's JSON output deterministically. (+13 more)

### Community 10 - "Research Scanner - Agent Task Prompts"
Cohesion: 0.33
Nodes (5): Research Scanner - Agent Task Prompts, Task A: Curator, Task B: Director, Task C: Analyst, Task D: Skeptic

### Community 11 - "Vault Index"
Cohesion: 0.40
Nodes (4): Audits, Raw Signals, Themes, Vault Index

### Community 23 - "test_scan.py"
Cohesion: 0.40
Nodes (4): fixture, Integration tests for research_scanner.scan entrypoint., temp_db_path(), test_run_scan_cycle_end_to_end()

### Community 25 - "Advancements in magnetic steering of soft magnetic continuum robots for medical applications"
Cohesion: 0.40
Nodes (4): Advancements in magnetic steering of soft magnetic continuum robots for medical applications, Curator Reasoning, My Notes, Summary / Abstract

### Community 26 - "Advocating the potential of AI for syndrome discovery: a scoping review"
Cohesion: 0.40
Nodes (4): Advocating the potential of AI for syndrome discovery: a scoping review, Curator Reasoning, My Notes, Summary / Abstract

### Community 27 - "Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review"
Cohesion: 0.40
Nodes (4): Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review, Curator Reasoning, My Notes, Summary / Abstract

### Community 28 - "Artificial Intelligence in Plant Sciences"
Cohesion: 0.40
Nodes (4): Artificial Intelligence in Plant Sciences, Curator Reasoning, My Notes, Summary / Abstract

### Community 29 - "Artificial Intelligence in Plant Sciences"
Cohesion: 0.40
Nodes (4): Artificial Intelligence in Plant Sciences, Curator Reasoning, My Notes, Summary / Abstract

### Community 30 - "Assessing the Role of Digital Transformation in Strengthening Customer Engagement: A Case Study of bKash"
Cohesion: 0.40
Nodes (4): Assessing the Role of Digital Transformation in Strengthening Customer Engagement: A Case Study of bKash, Curator Reasoning, My Notes, Summary / Abstract

### Community 31 - "Avaliação tomográfica do seio frontal no dimorfismo sexual"
Cohesion: 0.40
Nodes (4): Avaliação tomográfica do seio frontal no dimorfismo sexual, Curator Reasoning, My Notes, Summary / Abstract

### Community 32 - "Code and Experimental Data for Feasibility-Oriented Dung Beetle Optimization for Collision-Constrained Robotic Path Planning"
Cohesion: 0.40
Nodes (4): Code and Experimental Data for Feasibility-Oriented Dung Beetle Optimization for Collision-Constrained Robotic Path Planning, Curator Reasoning, My Notes, Summary / Abstract

### Community 33 - "Combating foreign bribery and corruption : an integrated corporate governance, sustainability, and artificial intelligence approach"
Cohesion: 0.40
Nodes (4): Combating foreign bribery and corruption : an integrated corporate governance, sustainability, and artificial intelligence approach, Curator Reasoning, My Notes, Summary / Abstract

### Community 34 - "Des villes en pixels aux cités réelles : influence des jeux vidéo sur l’architecture urbaine contemporaine"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Des villes en pixels aux cités réelles : influence des jeux vidéo sur l’architecture urbaine contemporaine, My Notes, Summary / Abstract

### Community 35 - "DESIGNING AND EXPERIMENTING AS THE NEW WAY OF LEARNING – EDUCATIONAL INNOVATION FOR MORE RELEVANCE IN THE AGE OF AI"
Cohesion: 0.40
Nodes (4): Curator Reasoning, DESIGNING AND EXPERIMENTING AS THE NEW WAY OF LEARNING – EDUCATIONAL INNOVATION FOR MORE RELEVANCE IN THE AGE OF AI, My Notes, Summary / Abstract

### Community 36 - "Development of an Advanced Artificial Intelligence-based Model (Deep Business Analytics) for Managing and Improving Control and Decision Making in Modern Organisations: Application in a Hospital Clinical Laboratory"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Development of an Advanced Artificial Intelligence-based Model (Deep Business Analytics) for Managing and Improving Control and Decision Making in Modern Organisations: Application in a Hospital Clinical Laboratory, My Notes, Summary / Abstract

### Community 37 - "Enabling Next-Generation Power Conversion: Design, Dynamic Characterization, and Application of Gallium Nitride Bidirectional Switches"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Enabling Next-Generation Power Conversion: Design, Dynamic Characterization, and Application of Gallium Nitride Bidirectional Switches, My Notes, Summary / Abstract

### Community 38 - "Feature Importance and Growth Rate Prediction in SiC PVT Processes through Advanced Machine Learning Models"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Feature Importance and Growth Rate Prediction in SiC PVT Processes through Advanced Machine Learning Models, My Notes, Summary / Abstract

### Community 39 - "Funding Innovation for Future-Ready Healthcare Systems"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Funding Innovation for Future-Ready Healthcare Systems, My Notes, Summary / Abstract

### Community 40 - "Funding Innovation for Future-Ready Healthcare Systems"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Funding Innovation for Future-Ready Healthcare Systems, My Notes, Summary / Abstract

### Community 41 - "L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition"
Cohesion: 0.40
Nodes (4): Curator Reasoning, L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition, My Notes, Summary / Abstract

### Community 42 - "Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France, My Notes, Summary / Abstract

### Community 43 - "Mechs"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Mechs, My Notes, Summary / Abstract

### Community 44 - "MODELING HOSPITALITY AND TOURISM STRATEGIES"
Cohesion: 0.40
Nodes (4): Curator Reasoning, MODELING HOSPITALITY AND TOURISM STRATEGIES, My Notes, Summary / Abstract

### Community 45 - "On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning, Summary / Abstract

### Community 46 - "Places and Non-Places for Language"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Places and Non-Places for Language, Summary / Abstract

### Community 47 - "Progress of major emitters towards climate targets: 2025 Update"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Progress of major emitters towards climate targets: 2025 Update, Summary / Abstract

### Community 48 - "Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap, Summary / Abstract

### Community 49 - "Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Summary / Abstract, Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)

## Knowledge Gaps
- **116 isolated node(s):** `Features`, `Prerequisites`, `1. Install Ollama & Pull Gemma Model`, `2. Install Python Dependencies`, `3. Environment & Credentials Configuration` (+111 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `init_db()` connect `init_db` to `score_unscored_theses`, `run_scan_cycle`, `parse_fact_check_note`, `get_db_connection`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `run_continuous_daemon()` connect `patch` to `run_scan_cycle`, `build_vault_index.py`?**
  _High betweenness centrality (0.076) - this node is a cross-community bridge._
- **Why does `run_scan_cycle()` connect `run_scan_cycle` to `init_db`, `test_scan.py`, `get_db_connection`, `patch`?**
  _High betweenness centrality (0.060) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `get_db_connection()` (e.g. with `main()` and `run_process_requests()`) actually correct?**
  _`get_db_connection()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `patch` (e.g. with `test_export_from_curator_decisions_write_failure_integrity()` and `test_export_unreviewed_candidates_transactional_integrity()`) actually correct?**
  _`patch` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `init_db()` (e.g. with `render_dashboard()` and `main()`) actually correct?**
  _`init_db()` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 10 inferred relationships involving `save_fetched_item()` (e.g. with `run_process_requests()` and `run_scan_cycle()`) actually correct?**
  _`save_fetched_item()` has 10 INFERRED edges - model-reasoned connections that need verification._