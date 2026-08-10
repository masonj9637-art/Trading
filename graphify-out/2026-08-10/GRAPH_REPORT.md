# Graph Report - Trading  (2026-08-09)

## Corpus Check
- 286 files · ~690,450 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1328 nodes · 1960 edges · 195 communities (145 shown, 50 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 51 edges (avg confidence: 0.58)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6f03fc2a`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- ConditionalAutoencoder
- BacktestEngine
- SECForm4Parser
- get_db_connection
- run_daemon.py
- OrderManager
- PortfolioRanker
- ChronosInference
- **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**
- .evaluate_trades
- GovernanceEngine
- engine.py
- .generate_signal
- update_last_success
- build_vault_index.py
- ThompsonSampler
- verified_45_pipeline.py
- pead_strategy_backtest.py
- scan.py
- test_export_to_obsidian.py
- VolatilityGuard
- test_leakage.py
- SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)
- check_unprotected_positions
- test_thesis_ledger.py
- AnalyticsEngine
- PART 1 - CODE TO BUILD (send these five, in this order)
- SEC Filings & Market Data Reactions
- Insider Cluster Buying Backtest & Walk-Forward Evaluation Results
- pead_fast_universe_builder_v3.py
- pead_fast_universe_builder_v5.py
- pead_fast_universe_builder_v7.py
- init_db
- .smooth
- send_discord_notification
- orchestrate_daily.py
- Filtered SEC Filings Subset
- pead_fast_universe_builder_v2.py
- pead_fast_universe_builder_v4.py
- pead_fast_universe_builder_v6.py
- pead_perfect_universe_builder.py
- Baseline Price-Reaction Classification (Random Dates)
- SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors
- verified_45_comparison.py
- yes_vs_no_comparison.py
- AI Statistical Arbitrage Backtest - Backtest Report
- Deep OFI Agent Only (2020-2022) - Backtest Report
- Investment Thesis Audit: NVIDIA (NVDA) & AI Hardware Accelerators
- health_monitor.py
- SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies
- SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies
- pead_fast_universe_builder.py
- pead_universe_builder.py
- scan_biotech.py
- trading_system/main.py
- AI Arbitrage Backtest 2024 - Backtest Report
- AI Arbitrage Backtest 2025 - Backtest Report
- orchestrate_bootstrap.py
- datetime
- fetch_and_build_report.py
- test_bootstrap.py
- scan_fintech.py
- scan_mining.py
- sec_scanner.py
- Research Scanner - Agent Task Prompts
- .fetch_historical_data
- run_director_step
- export_to_obsidian.py
- package.json
- test_log_trade.py
- test_run_daemon.py
- start.sh
- Rules for Backtesting, Model Training, and Risk Parameters
- rules/graphify.md
- workflows/graphify.md
- test_heartbeat_check.py
- compilerOptions
- index.ts
- research_scanner
- AI Hardware Accelerators
- research_scanner/__init__.py
- research_scanner/tests/__init__.py
- current-priorities.md
- RegimeDetector
- We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma
- Advancements in magnetic steering of soft magnetic continuum robots for medical applications
- Advocating the potential of AI for syndrome discovery: a scoping review
- Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review
- Artificial Intelligence in Plant Sciences
- Vault Index
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
- Google DeepMind Unveils Gemini Robotics 2: An AI Brain for Full-Body Humanoid Control
- L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition
- Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France
- Mechs
- MODELING HOSPITALITY AND TOURISM STRATEGIES
- On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning
- Places and Non-Places for Language
- Progress of major emitters towards climate targets: 2025 Update
- Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap
- Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)
- Vault Index
- TradingSystem
- Agent Evaluation & Benchmarking
- Agentic Systems & Benchmarking
- Artificial Intelligence
- General Technology
- Machine Learning
- Quantum Computing
- Robotics
- Semiconductors
- Agentic Systems & Debugging
- context/README.md
- Agentic Systems & Rag
- Agentic Systems & Synthetic Data
- AI Governance & Safety
- Database Systems & Neurosymbolic AI
- Llm Post-training & Reasoning
- Llm Reasoning & Alignment
- Llm Reinforcement Learning
- Machine Learning Theory
- Model Compression & Quantization
- Multimodal Llms & Evaluation
- Optimization & Ml Theory
- Quantum Computing
- Quantum Computing & Hardware
- Quantum Computing & Qec
- Robotics & Embodied AI
- Robotics & World Models
- Time Series & Quantitative Modeling
- Autonomous Llm Agents & Sequential Decision Making
- Fault-tolerant Quantum Computing & Error Correction
- Physical Robotics & Humanoid Safety Control

## God Nodes (most connected - your core abstractions)
1. `init_db()` - 38 edges
2. `get_db_connection()` - 29 edges
3. `BacktestEngine` - 28 edges
4. `save_fetched_item()` - 25 edges
5. `run_curator_export_step()` - 23 edges
6. `TradingSystem` - 22 edges
7. `run_director_step()` - 21 edges
8. `AlpacaDataFetcher` - 21 edges
9. `score_unscored_theses()` - 19 edges
10. `SECForm4Parser` - 19 edges

## Surprising Connections (you probably didn't know these)
- `BacktestEngine` --uses--> `DeepOrthogonalizer`  [INFERRED]
  trading_system/backtest/engine.py → trading_system/core/conditional_autoencoder.py
- `BacktestEngine` --uses--> `EnsembleAgent`  [INFERRED]
  trading_system/backtest/engine.py → trading_system/core/ensemble_agent.py
- `BacktestEngine` --uses--> `RegimeDetector`  [INFERRED]
  trading_system/backtest/engine.py → trading_system/core/regime_detector.py
- `BacktestEngine` --uses--> `GovernanceEngine`  [INFERRED]
  trading_system/backtest/engine.py → trading_system/governance/firewall.py
- `BacktestEngine` --uses--> `ChronosInference`  [INFERRED]
  trading_system/backtest/engine.py → trading_system/inference/model.py

## Import Cycles
- None detected.

## Communities (195 total, 50 thin omitted)

### Community 0 - "ConditionalAutoencoder"
Cohesion: 0.22
Nodes (5): ndarray, ConditionalAutoencoder, DataFrame, Orthogonalizes returns using a Conditional Autoencoder in a strictly CAUSAL…, Deep neural network that learns complex, non-linear market beta conditioned on…

### Community 1 - "BacktestEngine"
Cohesion: 0.13
Nodes (10): BacktestEngine, DataFrame, DeepOFIAgent, DEPRECATED / UNUSED MODULE This agent uses a Volume-Weighted Return proxy to…, AdaptiveKalmanAgent, DataFrame, Series, Calculates zero-lag momentum using an Adaptive Kalman Filter state-space model.… (+2 more)

### Community 2 - "SECForm4Parser"
Cohesion: 0.06
Nodes (29): InsiderClusterBacktester, Fetches historical daily bars for all symbols in a single batch call from…, Fetches Form 4 filings for a ticker via SEC Submissions API., Groups qualifying buys into cluster events (>= min_distinct_insiders distinct…, Downloads or loads SEC CIK-to-Ticker mapping from data.sec.gov. Returns a dict…, Fetches small-cap universe ($50M-$500M market cap)., Parses Form 4 XML string. Extracts qualifying open-market purchases (Code "P"),…, SECForm4Parser (+21 more)

### Community 3 - "get_db_connection"
Cohesion: 0.07
Nodes (54): Connection, get_all_ledger_entries(), get_all_thesis_scores(), get_all_trades(), get_db_connection(), get_unscored_ledger_entries(), Any, Creates and returns a SQLite connection with row factory set to sqlite3.Row. (+46 more)

### Community 4 - "run_daemon.py"
Cohesion: 0.08
Nodes (31): Configuration settings for research_scanner. All settings (score threshold,…, Entrypoint to process director requests. Polls the director_requests table and…, run_process_requests(), Continuous daemon runner for research_scanner. Runs fetch -> process requests…, fetch_arxiv_items(), Any, arXiv API data fetcher using feedparser., Fetches recent papers from arXiv API for specified categories using feedparser.… (+23 more)

### Community 5 - "OrderManager"
Cohesion: 0.06
Nodes (17): LimitOrderRequest, TimeInForce, AlpacaTradingClient, Retrieves current account equity for sizing limits., Retrieves the current market clock., Retrieves all currently open positions., Cancels all pending or open orders to prevent conflicting executions., Closes all open positions on Alpaca. (+9 more)

### Community 6 - "PortfolioRanker"
Cohesion: 0.13
Nodes (12): MeanReversionAgent, DataFrame, Series, Generates portfolio weights based on statistical mean reversion. Assets that…, MomentumAgent, DataFrame, Series, Generates portfolio weights based on cross-sectional momentum. close_data:… (+4 more)

### Community 7 - "ChronosInference"
Cohesion: 0.17
Nodes (10): BaseModel, on_event, post, TimeSeriesDataFrame, forecast(), ForecastRequest, startup_event(), ChronosInference (+2 more)

### Community 8 - "**Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**"
Cohesion: 0.10
Nodes (19): **Addressing Non-Stationarity with CADTS**, **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**, **AlphaEval Metrics: Information Coefficient (IC)**, **Average True Range (ATR) Dynamics**, **Conclusion**, **Continuous Adaptive Pipelines**, **Econometric Variance Forecasting: The GARCH Family**, **Institutional Decoupling of Alpha and Execution** (+11 more)

### Community 9 - ".evaluate_trades"
Cohesion: 0.50
Nodes (3): DataFrame, Series, Applies agent-specific rules before blending, followed by global portfolio…

### Community 10 - "GovernanceEngine"
Cohesion: 0.22
Nodes (8): AuditLogger, Commits blocked or modified trade rationales to an immutable log., GovernanceEngine, Assert that instantiating GovernanceEngine() with no arguments produces the new…, Test drawdown circuit breaker edge cases: account_nav exactly at the drawdown…, test_drawdown_circuit_breaker_edge_cases(), test_governance_engine_conservative_defaults(), test_quantile_fan_var_scaling()

### Community 11 - "engine.py"
Cohesion: 0.19
Nodes (10): load_data(), main(), run_backtest(), run_backtest(), run_backtest(), bootstrap(), DeepOrthogonalizer, AlpacaDataFetcher (+2 more)

### Community 12 - ".generate_signal"
Cohesion: 0.50
Nodes (3): DataFrame, Series, Since real L2 Limit Order Book data isn't available, we use a Volume-Weighted…

### Community 13 - "update_last_success"
Cohesion: 0.67
Nodes (3): Updates the shared last_success.json timestamp file for the specified key,…, update_last_success(), test_update_last_success_preserves_existing_keys()

### Community 14 - "build_vault_index.py"
Cohesion: 0.14
Nodes (22): build_vault_index(), extract_first_sentence(), extract_gist(), extract_h1_title(), main(), parse_note(), parse_yaml_frontmatter(), Any (+14 more)

### Community 16 - "ThompsonSampler"
Cohesion: 0.31
Nodes (3): Samples from the Beta distribution for each agent to determine dynamic trust…, Update Beta priors based on binary trade outcomes. profit_outcome: True if…, ThompsonSampler

### Community 17 - "verified_45_pipeline.py"
Cohesion: 0.20
Nodes (7): fetch_8k_filings(), fetch_filing_text(), get_cik(), End-to-end pipeline for the verified 45-ticker dataset: 1. For each ticker,…, Fetch full text of an 8-K filing., Lookup CIK from EDGAR company tickers JSON., Fetch recent 8-K filings from EDGAR for a given CIK.

### Community 18 - "pead_strategy_backtest.py"
Cohesion: 0.53
Nodes (7): compute_events_dataset(), find_effective_trading_date(), generate_random_baseline(), get_trading_days(), load_data(), run_pead_backtest(), test_pead_pipeline_integrity()

### Community 19 - "scan.py"
Cohesion: 0.18
Nodes (13): compute_item_hash(), is_item_fetched(), Computes a deterministic SHA256 hash for deduplication given a source and…, Checks whether an item with the given hash has already been stored in…, Main scan entrypoint for research_scanner. Runs one full fetch -> deduplicate…, Executes one full fetch + triage cycle across all configured data sources.…, run_scan_cycle(), test_compute_item_hash() (+5 more)

### Community 20 - "test_export_to_obsidian.py"
Cohesion: 0.22
Nodes (16): get_fetched_item_by_id(), Saves a newly fetched item into the fetched_items table. Returns True if…, Retrieves a fetched item by its database ID., save_fetched_item(), export_from_curator_decisions(), Reads a JSON file containing curator decisions and exports the corresponding…, fixture, Unit and integration tests for research_scanner.export_to_obsidian module. (+8 more)

### Community 21 - "VolatilityGuard"
Cohesion: 0.32
Nodes (4): Series, Fits a GJR-GARCH(1,1,1) model to the returns and predicts the next day's…, Returns (take_profit, stop_loss) based on asymmetric GJR-GARCH volatility…, VolatilityGuard

### Community 22 - "test_leakage.py"
Cohesion: 0.29
Nodes (7): asyncio, Assert that the final out-of-sample evaluation window used to report…, Assert that the date range bootstrap_model.py passes into…, Assert that optimize_optuna.py's training window and test window are…, test_bootstrap_model_train_window_leakage(), test_final_eval_window_no_overlap_with_finetune_window(), test_optuna_train_test_split_and_objective()

### Community 23 - "SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)"
Cohesion: 0.29
Nodes (6): 1. Dataset & Bar Window Coverage Summary, 2. Direct Comparison Results, 3. Industry-Level Breakdown, 4. Key Findings & Strategic Conclusion, Executive Summary, SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)

### Community 24 - "check_unprotected_positions"
Cohesion: 0.38
Nodes (6): check_unprotected_positions(), Simulate a position existing in get_open_positions() with no matching open OCO…, Replicates the unprotected position verification routine in main.py, Simulate a position existing in get_open_positions() WITH a matching open OCO…, test_protected_position_no_alert(), test_unprotected_position_alerting_path()

### Community 25 - "test_thesis_ledger.py"
Cohesion: 0.13
Nodes (23): parametrize, fixture, Unit and integration tests for research_scanner.thesis_ledger module., temp_db(), temp_vault(), test_compute_ledger_hash(), test_parse_fact_check_note_confidence_regex_patterns(), test_parse_fact_check_note_full_frontmatter() (+15 more)

### Community 26 - "AnalyticsEngine"
Cohesion: 0.33
Nodes (3): AnalyticsEngine, DataFrame, Takes the history dataframe from BacktestEngine and generates a quantstats HTML…

### Community 27 - "PART 1 - CODE TO BUILD (send these five, in this order)"
Cohesion: 0.15
Nodes (12): Build 1: Ledger fixes (existing code - thesis_ledger.py, scoring.py), Build 2: Notifier generalization (existing code - notifier.py), Build 3: Archivist refactor (existing code - scan.py, db.py, config.py), Build 4: export_to_obsidian.py extension (existing code), Build 5: Director wrapper script (new code - director_apply.py), PART 1 - CODE TO BUILD (send these five, in this order), PART 2 - AGENT TASK PROMPTS (not code; use after Part 1 is built), Research Scanner: Multi-Agent Architecture (+4 more)

### Community 28 - "SEC Filings & Market Data Reactions"
Cohesion: 0.33
Nodes (5): Market Data Price & Volume Reactions, Notes on Insufficient Data Filings, SEC Filings Disclosure List, SEC Filings & Market Data Reactions, Summary

### Community 29 - "Insider Cluster Buying Backtest & Walk-Forward Evaluation Results"
Cohesion: 0.33
Nodes (5): 1. Walk-Forward Performance Comparison (In-Sample vs. Out-of-Sample), 2. Dominant Feature Evaluation: "Bought into Strength" vs. "Bought into Weakness", 3. Key Statistical Findings & Conclusions, Executive Summary, Insider Cluster Buying Backtest & Walk-Forward Evaluation Results

### Community 30 - "pead_fast_universe_builder_v3.py"
Cohesion: 0.73
Nodes (5): check_sec_filings(), fetch_json(), get_mcap(), is_common_stock(), main()

### Community 31 - "pead_fast_universe_builder_v5.py"
Cohesion: 0.60
Nodes (4): fetch_json(), is_common_stock(), main(), process_sec_item()

### Community 32 - "pead_fast_universe_builder_v7.py"
Cohesion: 0.60
Nodes (4): fetch_json(), is_common_stock(), main(), process_sec_item()

### Community 33 - "init_db"
Cohesion: 0.11
Nodes (29): main(), Terminal CLI dashboard for research_scanner. Lists unreviewed candidate items…, Fetches and displays unreviewed candidates from the database in a terminal-…, render_dashboard(), get_all_candidates(), get_unconsumed_items(), init_db(), mark_item_consumed() (+21 more)

### Community 35 - "send_discord_notification"
Cohesion: 0.16
Nodes (14): Exception, Any, Sends a Discord notification via direct REST POST to the specified channel.…, send_discord_notification(), Unit tests for research_scanner.notifier module., test_send_discord_notification_failure(), test_send_discord_notification_missing_credentials(), test_send_discord_notification_success() (+6 more)

### Community 36 - "orchestrate_daily.py"
Cohesion: 0.70
Nodes (4): get_run_state(), main(), run_command(), save_run_state()

### Community 37 - "Filtered SEC Filings Subset"
Cohesion: 0.40
Nodes (4): Filtered Market Data Price & Volume Reactions, Filtered SEC Filings Subset, Filtering Funnel & Breakdown, Summary

### Community 38 - "pead_fast_universe_builder_v2.py"
Cohesion: 0.80
Nodes (4): check_sec_filings(), fetch_json(), get_mcap(), main()

### Community 39 - "pead_fast_universe_builder_v4.py"
Cohesion: 0.90
Nodes (4): fetch_json(), is_common_stock(), main(), process_single_ticker()

### Community 40 - "pead_fast_universe_builder_v6.py"
Cohesion: 0.80
Nodes (4): fetch_json(), is_common_stock(), main(), process_and_eval_mcap()

### Community 41 - "pead_perfect_universe_builder.py"
Cohesion: 0.80
Nodes (4): fetch_json(), is_common_stock(), main(), process_sec_smallcap()

### Community 42 - "Baseline Price-Reaction Classification (Random Dates)"
Cohesion: 0.40
Nodes (4): Baseline Price-Reaction Classification (Random Dates), Direct Comparison: Filing-Linked vs. Random Baseline Data, Key Takeaways, Random Baseline Market Data Reactions Table

### Community 43 - "SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors"
Cohesion: 0.40
Nodes (4): 1. Specialty Finance & Fintech Companies (15 Filings), 2. Mining & Exploration Companies (15 Filings), 3. Biotech & Pharma Companies (15 Filings), SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors

### Community 46 - "AI Statistical Arbitrage Backtest - Backtest Report"
Cohesion: 0.50
Nodes (3): Agent Performance Summary, AI Statistical Arbitrage Backtest - Backtest Report, Summary Metrics

### Community 47 - "Deep OFI Agent Only (2020-2022) - Backtest Report"
Cohesion: 0.50
Nodes (3): Agent Performance Summary, Deep OFI Agent Only (2020-2022) - Backtest Report, Summary Metrics

### Community 48 - "Investment Thesis Audit: NVIDIA (NVDA) & AI Hardware Accelerators"
Cohesion: 0.29
Nodes (6): 1. Thesis Summary, 2. Supporting Evidence, 3. Valuation Snapshot, 4. Bear Case, 5. Confidence Level, Investment Thesis Audit: NVIDIA (NVDA) & AI Hardware Accelerators

### Community 49 - "health_monitor.py"
Cohesion: 0.83
Nodes (3): check_health(), log_state(), run_cmd()

### Community 50 - "SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies"
Cohesion: 0.50
Nodes (3): Detailed SEC 8-K Filings Analysis, Executive Summary, SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies

### Community 54 - "SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies"
Cohesion: 0.50
Nodes (3): Detailed SEC 8-K Filings Analysis, Executive Summary, SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies

### Community 56 - "pead_fast_universe_builder.py"
Cohesion: 1.00
Nodes (3): check_sec_filings_and_mcap(), fetch_json(), main()

### Community 57 - "pead_universe_builder.py"
Cohesion: 1.00
Nodes (3): fetch_json(), main(), process_company()

### Community 60 - "trading_system/main.py"
Cohesion: 0.08
Nodes (16): EnsembleAgent, Executes Mean-Variance Thompson Sampling (MVTS) with Combinatorial Adaptive…, Updates the MVTS priors using CADTS geometric discounting based on continuous…, AlphaIsolator, DataFrame, Strips out the autoregressive momentum component to calculate the adjusted…, PCAOrthogonalizer, DataFrame (+8 more)

### Community 72 - "Research Scanner - Agent Task Prompts"
Cohesion: 0.33
Nodes (5): Research Scanner - Agent Task Prompts, Task A: Curator, Task B: Director, Task C: Analyst, Task D: Skeptic

### Community 73 - ".fetch_historical_data"
Cohesion: 0.40
Nodes (3): DataFrame, Fetches daily bars for the given symbols from Alpaca. Returns a wide-format…, Fetches macroeconomic covariates (^VIX, ^TNX) from Yahoo Finance. Returns a…

### Community 74 - "run_director_step"
Cohesion: 0.05
Nodes (61): apply_director_output(), main(), director_apply.py Applies Director's JSON output deterministically., setup_logging(), get_director_prompt(), main(), Any, director_run.py Director execution runner module for research_scanner. Invokes… (+53 more)

### Community 75 - "export_to_obsidian.py"
Cohesion: 0.09
Nodes (29): get_unreviewed_candidates(), mark_candidate_reviewed(), Retrieves all unreviewed candidates (reviewed = 0 or NULL) scoring at or above…, Marks a candidate as reviewed (reviewed = 1) given its database ID. Returns…, clean_filename_title(), ensure_theme_note_exists(), export_candidate_to_vault(), export_unreviewed_candidates() (+21 more)

### Community 76 - "package.json"
Cohesion: 0.10
Nodes (19): bin, antigravity-bridge, dependencies, @modelcontextprotocol/sdk, zod, description, devDependencies, @types/node (+11 more)

### Community 78 - "test_log_trade.py"
Cohesion: 0.16
Nodes (18): ArgumentParser, Namespace, build_parser(), main(), parse_args(), CLI module for manually logging real trade entries into research_scanner…, Constructs the command-line argument parser for logging trades., Parses and validates CLI arguments. (+10 more)

### Community 79 - "test_run_daemon.py"
Cohesion: 0.06
Nodes (57): get_agy_executable_path(), get_curator_prompt(), main(), Constructs the Curator prompt by loading the base prompt template, fetching…, Returns the full absolute path to the agy executable. Priority: 1.…, Step 3: Invokes Curator via agy CLI in headless mode, parses the JSON decision…, Executes a single cycle of the research_scanner pipeline: 1. Scan cycle…, Executes the research_scanner pipeline continuously every interval_seconds.… (+49 more)

### Community 94 - "test_heartbeat_check.py"
Cohesion: 0.17
Nodes (18): check_heartbeat(), get_timestamp_age_seconds(), main(), parse_iso_timestamp(), Any, Heartbeat monitor for research_scanner scheduled jobs. Checks…, Registers or updates the Task Scheduler entry for heartbeat_check.py to run…, Parses an ISO 8601 timestamp string into a datetime object. Returns None if… (+10 more)

### Community 97 - "compilerOptions"
Cohesion: 0.15
Nodes (12): compilerOptions, esModuleInterop, forceConsistentCasingInFileNames, module, moduleResolution, outDir, rootDir, skipLibCheck (+4 more)

### Community 110 - "index.ts"
Cohesion: 0.29
Nodes (8): CHECK_STATUS_TOOL, getRepoRoot(), handleCheckStatus(), handleRunAgent(), isQuotaError(), RUN_AGENT_TOOL, runCommand(), server

### Community 111 - "research_scanner"
Cohesion: 0.12
Nodes (16): 1. Install Ollama & Pull Gemma Model, 1. Running the Fetch & Triage Scanner, 2. Install Python Dependencies, 2. Terminal CLI Dashboard (`dashboard.py`), 3. Environment & Credentials Configuration, 3. Exporting to Obsidian (`export_to_obsidian.py`), 4. Vault Thesis Ledger Scan (`thesis_ledger.py`), 5. Forward Performance Scoring & Statistical Report (`scoring.py`) (+8 more)

### Community 116 - "AI Hardware Accelerators"
Cohesion: 0.50
Nodes (3): AI Hardware Accelerators, Investment Thesis Audits, Sub-topics & Architecture

### Community 138 - "RegimeDetector"
Cohesion: 0.33
Nodes (3): DataFrame, Classifies market structure into distinct regimes. market_returns: df where…, RegimeDetector

### Community 139 - "We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Summary / Abstract, We aim to make Uttar Pradesh India’s AI, electronics and startup capital: IT Minister Sunil Sharma

### Community 140 - "Advancements in magnetic steering of soft magnetic continuum robots for medical applications"
Cohesion: 0.40
Nodes (4): Advancements in magnetic steering of soft magnetic continuum robots for medical applications, Curator Reasoning, My Notes, Summary / Abstract

### Community 141 - "Advocating the potential of AI for syndrome discovery: a scoping review"
Cohesion: 0.40
Nodes (4): Advocating the potential of AI for syndrome discovery: a scoping review, Curator Reasoning, My Notes, Summary / Abstract

### Community 142 - "Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review"
Cohesion: 0.40
Nodes (4): Artificial Intelligence–Enabled mHealth Technologies for Rehabilitation in Patients with Cancer: A Scoping Review, Curator Reasoning, My Notes, Summary / Abstract

### Community 143 - "Artificial Intelligence in Plant Sciences"
Cohesion: 0.40
Nodes (4): Artificial Intelligence in Plant Sciences, Curator Reasoning, My Notes, Summary / Abstract

### Community 144 - "Vault Index"
Cohesion: 0.40
Nodes (4): Audits, Raw Signals, Themes, Vault Index

### Community 145 - "Assessing the Role of Digital Transformation in Strengthening Customer Engagement: A Case Study of bKash"
Cohesion: 0.40
Nodes (4): Assessing the Role of Digital Transformation in Strengthening Customer Engagement: A Case Study of bKash, Curator Reasoning, My Notes, Summary / Abstract

### Community 146 - "Avaliação tomográfica do seio frontal no dimorfismo sexual"
Cohesion: 0.40
Nodes (4): Avaliação tomográfica do seio frontal no dimorfismo sexual, Curator Reasoning, My Notes, Summary / Abstract

### Community 147 - "Code and Experimental Data for Feasibility-Oriented Dung Beetle Optimization for Collision-Constrained Robotic Path Planning"
Cohesion: 0.40
Nodes (4): Code and Experimental Data for Feasibility-Oriented Dung Beetle Optimization for Collision-Constrained Robotic Path Planning, Curator Reasoning, My Notes, Summary / Abstract

### Community 148 - "Combating foreign bribery and corruption : an integrated corporate governance, sustainability, and artificial intelligence approach"
Cohesion: 0.40
Nodes (4): Combating foreign bribery and corruption : an integrated corporate governance, sustainability, and artificial intelligence approach, Curator Reasoning, My Notes, Summary / Abstract

### Community 149 - "Des villes en pixels aux cités réelles : influence des jeux vidéo sur l’architecture urbaine contemporaine"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Des villes en pixels aux cités réelles : influence des jeux vidéo sur l’architecture urbaine contemporaine, My Notes, Summary / Abstract

### Community 150 - "DESIGNING AND EXPERIMENTING AS THE NEW WAY OF LEARNING – EDUCATIONAL INNOVATION FOR MORE RELEVANCE IN THE AGE OF AI"
Cohesion: 0.40
Nodes (4): Curator Reasoning, DESIGNING AND EXPERIMENTING AS THE NEW WAY OF LEARNING – EDUCATIONAL INNOVATION FOR MORE RELEVANCE IN THE AGE OF AI, My Notes, Summary / Abstract

### Community 151 - "Development of an Advanced Artificial Intelligence-based Model (Deep Business Analytics) for Managing and Improving Control and Decision Making in Modern Organisations: Application in a Hospital Clinical Laboratory"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Development of an Advanced Artificial Intelligence-based Model (Deep Business Analytics) for Managing and Improving Control and Decision Making in Modern Organisations: Application in a Hospital Clinical Laboratory, My Notes, Summary / Abstract

### Community 152 - "Enabling Next-Generation Power Conversion: Design, Dynamic Characterization, and Application of Gallium Nitride Bidirectional Switches"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Enabling Next-Generation Power Conversion: Design, Dynamic Characterization, and Application of Gallium Nitride Bidirectional Switches, My Notes, Summary / Abstract

### Community 153 - "Feature Importance and Growth Rate Prediction in SiC PVT Processes through Advanced Machine Learning Models"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Feature Importance and Growth Rate Prediction in SiC PVT Processes through Advanced Machine Learning Models, My Notes, Summary / Abstract

### Community 154 - "Funding Innovation for Future-Ready Healthcare Systems"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Funding Innovation for Future-Ready Healthcare Systems, My Notes, Summary / Abstract

### Community 155 - "Google DeepMind Unveils Gemini Robotics 2: An AI Brain for Full-Body Humanoid Control"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Google DeepMind Unveils Gemini Robotics 2: An AI Brain for Full-Body Humanoid Control, My Notes, Summary / Abstract

### Community 156 - "L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition"
Cohesion: 0.40
Nodes (4): Curator Reasoning, L’innovation locale et sa contribution au développement durable : pour une taxonomie du système local de transition, My Notes, Summary / Abstract

### Community 157 - "Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Management of healthcare risk waste and non-hazardous healthcare waste: the case of a public hospital in western France, My Notes, Summary / Abstract

### Community 158 - "Mechs"
Cohesion: 0.40
Nodes (4): Curator Reasoning, Mechs, My Notes, Summary / Abstract

### Community 159 - "MODELING HOSPITALITY AND TOURISM STRATEGIES"
Cohesion: 0.40
Nodes (4): Curator Reasoning, MODELING HOSPITALITY AND TOURISM STRATEGIES, My Notes, Summary / Abstract

### Community 160 - "On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, On the Analysis of Potential Games: From Constraints, Price of Anarchy and Reinforcement Learning to Contrastive Learning, Summary / Abstract

### Community 161 - "Places and Non-Places for Language"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Places and Non-Places for Language, Summary / Abstract

### Community 162 - "Progress of major emitters towards climate targets: 2025 Update"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Progress of major emitters towards climate targets: 2025 Update, Summary / Abstract

### Community 163 - "Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Specialeafhandling: Scaling AI in Organisations: An Empirical Study of Organisational Conditions Differentiating Enterprise Adoption from the Pilot Trap, Summary / Abstract

### Community 164 - "Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)"
Cohesion: 0.40
Nodes (4): Curator Reasoning, My Notes, Summary / Abstract, Tuning of Magnetic Frustration Through Doping in a Group of Magnetic Semiconductors with the Chemical Formula CaMn2X2 (X = Pnictogen)

### Community 165 - "Vault Index"
Cohesion: 0.40
Nodes (4): Audits, Raw Signals, Themes, Vault Index

### Community 166 - "TradingSystem"
Cohesion: 0.24
Nodes (7): DataFrame, TradingSystem, run_test(), Assert no references to ofi_active_orders.json or close_ofi_positions remain…, Assert 'deep_ofi' is not present in the EnsembleAgent agent_names list…, test_deep_ofi_not_in_ensemble_agent_names(), test_no_ofi_references_in_main_py()

## Knowledge Gaps
- **217 isolated node(s):** `name`, `version`, `description`, `type`, `antigravity-bridge` (+212 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **50 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AlpacaDataFetcher` connect `engine.py` to `.fetch_historical_data`, `SECForm4Parser`, `trading_system/main.py`, `TradingSystem`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **Why does `BacktestEngine` connect `BacktestEngine` to `PortfolioRanker`, `ChronosInference`, `GovernanceEngine`, `RegimeDetector`, `engine.py`, `VolatilityGuard`, `test_leakage.py`, `trading_system/main.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `init_db()` connect `init_db` to `get_db_connection`, `run_daemon.py`, `run_director_step`, `export_to_obsidian.py`, `test_log_trade.py`, `test_run_daemon.py`, `scan.py`, `test_export_to_obsidian.py`, `test_thesis_ledger.py`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Are the 7 inferred relationships involving `datetime` (e.g. with `test_fresh_timestamps_produce_no_alert()` and `test_missing_key_treated_as_stale()`) actually correct?**
  _`datetime` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `BacktestEngine` (e.g. with `DeepOrthogonalizer` and `EnsembleAgent`) actually correct?**
  _`BacktestEngine` has 11 INFERRED edges - model-reasoned connections that need verification._
- **What connects `name`, `version`, `description` to the rest of the system?**
  _217 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `BacktestEngine` be split into smaller, more focused modules?**
  _Cohesion score 0.13333333333333333 - nodes in this community are weakly interconnected._