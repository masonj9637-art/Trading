# Graph Report - Trading  (2026-08-02)

## Corpus Check
- 206 files · ~625,792 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 839 nodes · 1251 edges · 133 communities (116 shown, 17 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8e47d6e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- bootstrap_model.py
- DeepOFIAgent
- SECForm4Parser
- scoring.py
- fetch_uspto_items
- trading_system/main.py
- PortfolioRanker
- ChronosInference
- **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**
- EnsembleAgent
- GovernanceEngine
- BacktestEngine
- db.py
- TradingSystem
- engine.py
- ThompsonSampler
- verified_45_pipeline.py
- pead_strategy_backtest.py
- init_db
- get_db_connection
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
- test_dashboard.py
- config.py
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
- .__init__
- AI Arbitrage Backtest 2024 - Backtest Report
- AI Arbitrage Backtest 2025 - Backtest Report
- orchestrate_bootstrap.py
- fetch_and_build_report.py
- scan_fintech.py
- scan_mining.py
- sec_scanner.py
- Research Scanner - Agent Task Prompts
- .fetch_historical_data
- test_export_to_obsidian.py
- start.sh
- Rules for Backtesting, Model Training, and Risk Parameters
- rules/graphify.md
- workflows/graphify.md
- research_scanner
- AI Hardware Accelerators
- research_scanner/__init__.py
- research_scanner/tests/__init__.py
- test_bootstrap.py

## God Nodes (most connected - your core abstractions)
1. `init_db()` - 29 edges
2. `BacktestEngine` - 28 edges
3. `get_db_connection()` - 26 edges
4. `TradingSystem` - 22 edges
5. `AlpacaDataFetcher` - 21 edges
6. `save_fetched_item()` - 20 edges
7. `SECForm4Parser` - 19 edges
8. `OrderManager` - 17 edges
9. `score_unscored_theses()` - 16 edges
10. `PortfolioRanker` - 16 edges

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

## Communities (133 total, 17 thin omitted)

### Community 0 - "bootstrap_model.py"
Cohesion: 0.14
Nodes (10): ndarray, bootstrap(), ConditionalAutoencoder, DeepOrthogonalizer, DataFrame, Orthogonalizes returns using a Conditional Autoencoder in a strictly CAUSAL roll, Deep neural network that learns complex, non-linear market beta conditioned on f, EMASmoother (+2 more)

### Community 1 - "DeepOFIAgent"
Cohesion: 0.25
Nodes (5): DeepOFIAgent, DataFrame, Series, DEPRECATED / UNUSED MODULE  This agent uses a Volume-Weighted Return proxy to es, Since real L2 Limit Order Book data isn't available, we use a         Volume-Wei

### Community 2 - "SECForm4Parser"
Cohesion: 0.06
Nodes (29): InsiderClusterBacktester, Fetches historical daily bars for all symbols in a single batch call from Alpaca, Fetches Form 4 filings for a ticker via SEC Submissions API., Groups qualifying buys into cluster events (>= min_distinct_insiders distinct in, Downloads or loads SEC CIK-to-Ticker mapping from data.sec.gov.         Returns, Fetches small-cap universe ($50M-$500M market cap)., Parses Form 4 XML string. Extracts qualifying open-market purchases (Code "P"),, SECForm4Parser (+21 more)

### Community 3 - "scoring.py"
Cohesion: 0.12
Nodes (29): get_all_thesis_scores(), get_unscored_ledger_entries(), Saves an immutable audit thesis record into thesis_ledger.     Returns True if s, Retrieves all thesis_ledger entries that have NOT yet been scored for the given, Saves a scored thesis evaluation record into thesis_scores., Retrieves all records from thesis_scores JOINed with thesis_ledger metadata., save_thesis_ledger_entry(), save_thesis_score() (+21 more)

### Community 4 - "fetch_uspto_items"
Cohesion: 0.11
Nodes (21): fetch_arxiv_items(), Any, arXiv API data fetcher using feedparser., Fetches recent papers from arXiv API for specified categories using feedparser., fetch_currents_items(), Any, Currents API news data fetcher., Fetches tech & industry news items from Currents API matching keywords.      :pa (+13 more)

### Community 5 - "trading_system/main.py"
Cohesion: 0.05
Nodes (21): LimitOrderRequest, TimeInForce, AlpacaTradingClient, Retrieves current account equity for sizing limits., Retrieves the current market clock., Retrieves all currently open positions., Cancels all pending or open orders to prevent conflicting executions., Closes all open positions on Alpaca. (+13 more)

### Community 6 - "PortfolioRanker"
Cohesion: 0.13
Nodes (12): MeanReversionAgent, DataFrame, Series, Generates portfolio weights based on statistical mean reversion.         Assets, MomentumAgent, DataFrame, Series, Generates portfolio weights based on cross-sectional momentum.         close_dat (+4 more)

### Community 7 - "ChronosInference"
Cohesion: 0.17
Nodes (10): BaseModel, on_event, post, TimeSeriesDataFrame, forecast(), ForecastRequest, startup_event(), ChronosInference (+2 more)

### Community 8 - "**Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**"
Cohesion: 0.10
Nodes (19): **Addressing Non-Stationarity with CADTS**, **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**, **AlphaEval Metrics: Information Coefficient (IC)**, **Average True Range (ATR) Dynamics**, **Conclusion**, **Continuous Adaptive Pipelines**, **Econometric Variance Forecasting: The GARCH Family**, **Institutional Decoupling of Alpha and Execution** (+11 more)

### Community 9 - "EnsembleAgent"
Cohesion: 0.18
Nodes (4): DataFrame, EnsembleAgent, Executes Mean-Variance Thompson Sampling (MVTS) with Combinatorial Adaptive Disc, Updates the MVTS priors using CADTS geometric discounting based on continuous re

### Community 10 - "GovernanceEngine"
Cohesion: 0.16
Nodes (11): AuditLogger, Commits blocked or modified trade rationales to an immutable log., GovernanceEngine, DataFrame, Series, Applies agent-specific rules before blending, followed by global portfolio const, Assert that instantiating GovernanceEngine() with no arguments produces the new, Test drawdown circuit breaker edge cases: account_nav exactly at the drawdown th (+3 more)

### Community 11 - "BacktestEngine"
Cohesion: 0.22
Nodes (10): BacktestEngine, load_data(), main(), run_backtest(), run_backtest(), run_backtest(), AlpacaDataFetcher, Fetches the latest trade prices for the given symbols.         Returns a diction (+2 more)

### Community 12 - "db.py"
Cohesion: 0.19
Nodes (18): compute_item_hash(), get_all_candidates(), get_all_ledger_entries(), get_unconsumed_items(), Any, Database storage module for research_scanner using SQLite. Stores fetched items, Computes a deterministic SHA256 hash for deduplication given a source and extern, Saves a newly fetched item into the fetched_items table.     Returns True if ins (+10 more)

### Community 13 - "TradingSystem"
Cohesion: 0.11
Nodes (14): DataFrame, Classifies market structure into distinct regimes.         market_returns: df wh, RegimeDetector, DataFrame, Resolves the peak NAV using Redis with a disk-backed fallback., resolve_peak_nav(), TradingSystem, run_test() (+6 more)

### Community 15 - "engine.py"
Cohesion: 0.18
Nodes (6): AlphaIsolator, DataFrame, Strips out the autoregressive momentum component to calculate the adjusted predi, DataFrame, Classifies the market regime using the benchmark symbol (e.g. SPY).         mark, RegimeDetector

### Community 16 - "ThompsonSampler"
Cohesion: 0.31
Nodes (3): Samples from the Beta distribution for each agent to determine dynamic trust wei, Update Beta priors based on binary trade outcomes.         profit_outcome: True, ThompsonSampler

### Community 17 - "verified_45_pipeline.py"
Cohesion: 0.20
Nodes (7): fetch_8k_filings(), fetch_filing_text(), get_cik(), End-to-end pipeline for the verified 45-ticker dataset:   1. For each ticker, fe, Fetch full text of an 8-K filing., Lookup CIK from EDGAR company tickers JSON., Fetch recent 8-K filings from EDGAR for a given CIK.

### Community 18 - "pead_strategy_backtest.py"
Cohesion: 0.53
Nodes (7): compute_events_dataset(), find_effective_trading_date(), generate_random_baseline(), get_trading_days(), load_data(), run_pead_backtest(), test_pead_pipeline_integrity()

### Community 19 - "init_db"
Cohesion: 0.14
Nodes (17): init_db(), is_item_fetched(), Checks whether an item with the given hash has already been stored in fetched_it, Initializes the SQLite database schema if tables do not exist., Entrypoint to process director requests. Polls the director_requests table and e, run_process_requests(), Main scan entrypoint for research_scanner. Runs one full fetch -> deduplicate ->, Executes one full fetch + triage cycle across all configured data sources. (+9 more)

### Community 20 - "get_db_connection"
Cohesion: 0.18
Nodes (14): Connection, get_db_connection(), get_unreviewed_candidates(), mark_candidate_reviewed(), Creates and returns a SQLite connection with row factory set to sqlite3.Row., Retrieves all unreviewed candidates (reviewed = 0 or NULL) scoring at or above m, Marks a candidate as reviewed (reviewed = 1) given its database ID.     Returns, export_unreviewed_candidates() (+6 more)

### Community 21 - "VolatilityGuard"
Cohesion: 0.32
Nodes (4): Series, Fits a GJR-GARCH(1,1,1) model to the returns and predicts the next day's volatil, Returns (take_profit, stop_loss) based on asymmetric GJR-GARCH volatility foreca, VolatilityGuard

### Community 22 - "test_leakage.py"
Cohesion: 0.29
Nodes (7): asyncio, Assert that the final out-of-sample evaluation window used to report Sharpe/CAGR, Assert that the date range bootstrap_model.py passes into ChronosInference.train, Assert that optimize_optuna.py's training window and test window are chronologic, test_bootstrap_model_train_window_leakage(), test_final_eval_window_no_overlap_with_finetune_window(), test_optuna_train_test_split_and_objective()

### Community 23 - "SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)"
Cohesion: 0.29
Nodes (6): 1. Dataset & Bar Window Coverage Summary, 2. Direct Comparison Results, 3. Industry-Level Breakdown, 4. Key Findings & Strategic Conclusion, Executive Summary, SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)

### Community 24 - "check_unprotected_positions"
Cohesion: 0.38
Nodes (6): check_unprotected_positions(), Simulate a position existing in get_open_positions() with no matching open OCO o, Replicates the unprotected position verification routine in main.py, Simulate a position existing in get_open_positions() WITH a matching open OCO or, test_protected_position_no_alert(), test_unprotected_position_alerting_path()

### Community 25 - "test_thesis_ledger.py"
Cohesion: 0.13
Nodes (23): parametrize, fixture, Unit and integration tests for research_scanner.thesis_ledger module., temp_db(), temp_vault(), test_compute_ledger_hash(), test_parse_fact_check_note_confidence_regex_patterns(), test_parse_fact_check_note_full_frontmatter() (+15 more)

### Community 26 - "AnalyticsEngine"
Cohesion: 0.33
Nodes (3): AnalyticsEngine, DataFrame, Takes the history dataframe from BacktestEngine and generates a quantstats HTML

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

### Community 33 - "test_dashboard.py"
Cohesion: 0.25
Nodes (9): main(), Terminal CLI dashboard for research_scanner. Lists unreviewed candidate items fr, Fetches and displays unreviewed candidates from the database in a terminal-frien, render_dashboard(), fixture, Unit tests for research_scanner.dashboard module., temp_db_with_candidates(), test_render_dashboard_min_score_filter() (+1 more)

### Community 34 - "config.py"
Cohesion: 0.29
Nodes (7): Configuration settings for research_scanner.  All settings (score threshold, Gem, main(), director_apply.py  Applies Director's JSON output deterministically., setup_logging(), Discord REST notification dispatcher for research_scanner., Sends a plain string message to Discord via REST POST.      :param content: The, send_discord_message()

### Community 35 - "send_discord_notification"
Cohesion: 0.36
Nodes (7): Any, Sends a Discord notification via direct REST POST to the specified channel., send_discord_notification(), Unit tests for research_scanner.notifier module., test_send_discord_notification_failure(), test_send_discord_notification_missing_credentials(), test_send_discord_notification_success()

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

### Community 60 - ".__init__"
Cohesion: 0.14
Nodes (7): AdaptiveKalmanAgent, DataFrame, Series, Calculates zero-lag momentum using an Adaptive Kalman Filter state-space model., PCAOrthogonalizer, DataFrame, Takes a DataFrame of returns (dates as index, assets as columns).         Extrac

### Community 72 - "Research Scanner - Agent Task Prompts"
Cohesion: 0.33
Nodes (5): Research Scanner - Agent Task Prompts, Task A: Curator, Task B: Director, Task C: Analyst, Task D: Skeptic

### Community 73 - ".fetch_historical_data"
Cohesion: 0.40
Nodes (3): DataFrame, Fetches daily bars for the given symbols from Alpaca.         Returns a wide-for, Fetches macroeconomic covariates (^VIX, ^TNX) from Yahoo Finance.         Return

### Community 75 - "test_export_to_obsidian.py"
Cohesion: 0.10
Nodes (34): get_fetched_item_by_id(), mark_item_consumed(), Retrieves a fetched item by its database ID., Marks a fetched item as consumed (consumed_by_curator = 1) given its database ID, ensure_theme_note_exists(), export_candidate_to_vault(), export_from_curator_decisions(), format_theme_title() (+26 more)

### Community 111 - "research_scanner"
Cohesion: 0.12
Nodes (16): 1. Install Ollama & Pull Gemma Model, 1. Running the Fetch & Triage Scanner, 2. Install Python Dependencies, 2. Terminal CLI Dashboard (`dashboard.py`), 3. Environment & Credentials Configuration, 3. Exporting to Obsidian (`export_to_obsidian.py`), 4. Vault Thesis Ledger Scan (`thesis_ledger.py`), 5. Forward Performance Scoring & Statistical Report (`scoring.py`) (+8 more)

### Community 116 - "AI Hardware Accelerators"
Cohesion: 0.50
Nodes (3): AI Hardware Accelerators, Investment Thesis Audits, Sub-topics & Architecture

## Knowledge Gaps
- **81 isolated node(s):** `start.sh script`, `graphify`, `Workflow: graphify`, `graphify`, `1. Thesis Summary` (+76 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AlpacaDataFetcher` connect `BacktestEngine` to `bootstrap_model.py`, `SECForm4Parser`, `trading_system/main.py`, `.fetch_historical_data`, `TradingSystem`, `.__init__`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `TradingSystem` connect `TradingSystem` to `bootstrap_model.py`, `trading_system/main.py`, `PortfolioRanker`, `EnsembleAgent`, `GovernanceEngine`, `BacktestEngine`, `engine.py`, `VolatilityGuard`, `.__init__`?**
  _High betweenness centrality (0.023) - this node is a cross-community bridge._
- **Why does `init_db()` connect `init_db` to `test_dashboard.py`, `config.py`, `scoring.py`, `test_export_to_obsidian.py`, `db.py`, `get_db_connection`, `test_thesis_ledger.py`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BacktestEngine` (e.g. with `DeepOrthogonalizer` and `EnsembleAgent`) actually correct?**
  _`BacktestEngine` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `TradingSystem` (e.g. with `EnsembleAgent` and `RegimeDetector`) actually correct?**
  _`TradingSystem` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `AlpacaDataFetcher` (e.g. with `InsiderClusterBacktester` and `TradingSystem`) actually correct?**
  _`AlpacaDataFetcher` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `start.sh script`, `graphify`, `Workflow: graphify` to the rest of the system?**
  _81 weakly-connected nodes found - possible documentation gaps or missing edges._