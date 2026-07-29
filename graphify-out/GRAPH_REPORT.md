# Graph Report - Trading  (2026-07-28)

## Corpus Check
- 207 files · ~625,229 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 879 nodes · 1253 edges · 134 communities (117 shown, 17 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Model Card for Model ID
- Model Card for Model ID
- SECForm4Parser
- scoring.py
- test_sources.py
- AlpacaTradingClient
- PortfolioRanker
- ChronosInference
- **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**
- engine.py
- GovernanceEngine
- BacktestEngine
- config.py
- TradingSystem
- bootstrap_model.py
- trading_system/main.py
- ThompsonSampler
- verified_45_pipeline.py
- pead_strategy_backtest.py
- db.py
- TemporalAligner
- .__init__
- test_leakage.py
- SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)
- check_unprotected_positions
- init_db
- AnalyticsEngine
- test_dashboard.py
- SEC Filings & Market Data Reactions
- Insider Cluster Buying Backtest & Walk-Forward Evaluation Results
- pead_fast_universe_builder_v3.py
- pead_fast_universe_builder_v5.py
- pead_fast_universe_builder_v7.py
- OrderManager
- LimitOrderRequest
- order_manager.py
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
- .generate_signal
- AI Arbitrage Backtest 2024 - Backtest Report
- AI Arbitrage Backtest 2025 - Backtest Report
- orchestrate_bootstrap.py
- fetch_and_build_report.py
- scan_fintech.py
- scan_mining.py
- sec_scanner.py
- RegimeDetector
- .fetch_historical_data
- resolve_peak_nav
- test_export_to_obsidian.py
- start.sh
- Rules for Backtesting, Model Training, and Risk Parameters
- rules/graphify.md
- workflows/graphify.md
- triage_item
- research_scanner
- AI Hardware Accelerators
- research_scanner/__init__.py
- research_scanner/tests/__init__.py
- .generate_signal
- .generate_signal

## God Nodes (most connected - your core abstractions)
1. `BacktestEngine` - 28 edges
2. `init_db()` - 24 edges
3. `TradingSystem` - 22 edges
4. `AlpacaDataFetcher` - 21 edges
5. `SECForm4Parser` - 19 edges
6. `OrderManager` - 17 edges
7. `PortfolioRanker` - 16 edges
8. `get_db_connection()` - 15 edges
9. `Model Card for Model ID` - 15 edges
10. `Model Card for Model ID` - 15 edges

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

## Communities (134 total, 17 thin omitted)

### Community 0 - "Model Card for Model ID"
Cohesion: 0.05
Nodes (37): Bias, Risks, and Limitations, Citation [optional], Compute Infrastructure, Direct Use, Downstream Use [optional], Environmental Impact, Evaluation, Factors (+29 more)

### Community 1 - "Model Card for Model ID"
Cohesion: 0.05
Nodes (37): Bias, Risks, and Limitations, Citation [optional], Compute Infrastructure, Direct Use, Downstream Use [optional], Environmental Impact, Evaluation, Factors (+29 more)

### Community 2 - "SECForm4Parser"
Cohesion: 0.06
Nodes (29): InsiderClusterBacktester, Fetches historical daily bars for all symbols in a single batch call from Alpaca, Fetches Form 4 filings for a ticker via SEC Submissions API., Groups qualifying buys into cluster events (>= min_distinct_insiders distinct in, Downloads or loads SEC CIK-to-Ticker mapping from data.sec.gov.         Returns, Fetches small-cap universe ($50M-$500M market cap)., Parses Form 4 XML string. Extracts qualifying open-market purchases (Code "P"),, SECForm4Parser (+21 more)

### Community 3 - "scoring.py"
Cohesion: 0.12
Nodes (29): get_all_thesis_scores(), get_unscored_ledger_entries(), Any, Saves an immutable audit thesis record into thesis_ledger.     Returns True if s, Retrieves all thesis_ledger entries that have NOT yet been scored for the given, Saves a scored thesis evaluation record into thesis_scores., Retrieves all records from thesis_scores JOINed with thesis_ledger metadata., save_thesis_ledger_entry() (+21 more)

### Community 4 - "test_sources.py"
Cohesion: 0.11
Nodes (21): fetch_arxiv_items(), Any, arXiv API data fetcher using feedparser., Fetches recent papers from arXiv API for specified categories using feedparser., fetch_currents_items(), Any, Currents API news data fetcher., Fetches tech & industry news items from Currents API matching keywords.      :pa (+13 more)

### Community 5 - "AlpacaTradingClient"
Cohesion: 0.14
Nodes (8): AlpacaTradingClient, Retrieves current account equity for sizing limits., Retrieves the current market clock., Retrieves all currently open positions., Cancels all pending or open orders to prevent conflicting executions., Closes all open positions on Alpaca., Cancels all pending/open orders and blocks until Alpaca confirms they are fully, main()

### Community 6 - "PortfolioRanker"
Cohesion: 0.26
Nodes (6): MeanReversionAgent, MomentumAgent, PortfolioRanker, DataFrame, Translates alpha signals into a dollar-neutral Long/Short portfolio by ranking a, test_ranking_leverage_constraint()

### Community 7 - "ChronosInference"
Cohesion: 0.17
Nodes (10): BaseModel, on_event, post, TimeSeriesDataFrame, forecast(), ForecastRequest, startup_event(), ChronosInference (+2 more)

### Community 8 - "**Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**"
Cohesion: 0.10
Nodes (19): **Addressing Non-Stationarity with CADTS**, **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**, **AlphaEval Metrics: Information Coefficient (IC)**, **Average True Range (ATR) Dynamics**, **Conclusion**, **Continuous Adaptive Pipelines**, **Econometric Variance Forecasting: The GARCH Family**, **Institutional Decoupling of Alpha and Execution** (+11 more)

### Community 9 - "engine.py"
Cohesion: 0.16
Nodes (6): EnsembleAgent, Executes Mean-Variance Thompson Sampling (MVTS) with Combinatorial Adaptive Disc, Updates the MVTS priors using CADTS geometric discounting based on continuous re, DataFrame, Classifies the market regime using the benchmark symbol (e.g. SPY).         mark, RegimeDetector

### Community 10 - "GovernanceEngine"
Cohesion: 0.16
Nodes (11): AuditLogger, Commits blocked or modified trade rationales to an immutable log., GovernanceEngine, DataFrame, Series, Applies agent-specific rules before blending, followed by global portfolio const, Assert that instantiating GovernanceEngine() with no arguments produces the new, Test drawdown circuit breaker edge cases: account_nav exactly at the drawdown th (+3 more)

### Community 11 - "BacktestEngine"
Cohesion: 0.17
Nodes (11): BacktestEngine, DataFrame, load_data(), main(), run_backtest(), run_backtest(), run_backtest(), AlpacaDataFetcher (+3 more)

### Community 12 - "config.py"
Cohesion: 0.23
Nodes (9): Configuration settings for research_scanner.  All settings (score threshold, Gem, Any, Discord REST notification dispatcher for research_scanner., Sends a Discord notification via direct REST POST to the specified channel., send_discord_notification(), Unit tests for research_scanner.notifier module., test_send_discord_notification_failure(), test_send_discord_notification_missing_credentials() (+1 more)

### Community 13 - "TradingSystem"
Cohesion: 0.24
Nodes (7): DataFrame, TradingSystem, run_test(), Assert no references to ofi_active_orders.json or close_ofi_positions remain any, Assert 'deep_ofi' is not present in the EnsembleAgent agent_names list construct, test_deep_ofi_not_in_ensemble_agent_names(), test_no_ofi_references_in_main_py()

### Community 14 - "bootstrap_model.py"
Cohesion: 0.12
Nodes (12): ndarray, bootstrap(), ConditionalAutoencoder, DeepOrthogonalizer, DataFrame, Orthogonalizes returns using a Conditional Autoencoder in a strictly CAUSAL roll, Deep neural network that learns complex, non-linear market beta conditioned on f, EMASmoother (+4 more)

### Community 15 - "trading_system/main.py"
Cohesion: 0.15
Nodes (7): AlphaIsolator, DataFrame, Strips out the autoregressive momentum component to calculate the adjusted predi, AdaptiveKalmanAgent, PCAOrthogonalizer, DataFrame, Takes a DataFrame of returns (dates as index, assets as columns).         Extrac

### Community 16 - "ThompsonSampler"
Cohesion: 0.31
Nodes (3): Samples from the Beta distribution for each agent to determine dynamic trust wei, Update Beta priors based on binary trade outcomes.         profit_outcome: True, ThompsonSampler

### Community 17 - "verified_45_pipeline.py"
Cohesion: 0.20
Nodes (7): fetch_8k_filings(), fetch_filing_text(), get_cik(), End-to-end pipeline for the verified 45-ticker dataset:   1. For each ticker, fe, Fetch full text of an 8-K filing., Lookup CIK from EDGAR company tickers JSON., Fetch recent 8-K filings from EDGAR for a given CIK.

### Community 18 - "pead_strategy_backtest.py"
Cohesion: 0.53
Nodes (7): compute_events_dataset(), find_effective_trading_date(), generate_random_baseline(), get_trading_days(), load_data(), run_pead_backtest(), test_pead_pipeline_integrity()

### Community 19 - "db.py"
Cohesion: 0.15
Nodes (25): Connection, compute_item_hash(), get_all_candidates(), get_db_connection(), is_item_fetched(), Database storage module for research_scanner using SQLite. Stores fetched items, Checks whether an item with the given hash has already been stored in fetched_it, Saves a newly fetched item into the fetched_items table.     Returns True if ins (+17 more)

### Community 20 - "TemporalAligner"
Cohesion: 0.32
Nodes (4): DataFrame, Aligns a long-format DataFrame to a continuous time index, padding missing dates, TemporalAligner, test_temporal_alignment()

### Community 21 - ".__init__"
Cohesion: 0.13
Nodes (9): DeepOFIAgent, DataFrame, Series, DEPRECATED / UNUSED MODULE  This agent uses a Volume-Weighted Return proxy to es, Since real L2 Limit Order Book data isn't available, we use a         Volume-Wei, Series, Fits a GJR-GARCH(1,1,1) model to the returns and predicts the next day's volatil, Returns (take_profit, stop_loss) based on asymmetric GJR-GARCH volatility foreca (+1 more)

### Community 22 - "test_leakage.py"
Cohesion: 0.29
Nodes (7): asyncio, Assert that the final out-of-sample evaluation window used to report Sharpe/CAGR, Assert that the date range bootstrap_model.py passes into ChronosInference.train, Assert that optimize_optuna.py's training window and test window are chronologic, test_bootstrap_model_train_window_leakage(), test_final_eval_window_no_overlap_with_finetune_window(), test_optuna_train_test_split_and_objective()

### Community 23 - "SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)"
Cohesion: 0.29
Nodes (6): 1. Dataset & Bar Window Coverage Summary, 2. Direct Comparison Results, 3. Industry-Level Breakdown, 4. Key Findings & Strategic Conclusion, Executive Summary, SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)

### Community 24 - "check_unprotected_positions"
Cohesion: 0.38
Nodes (6): check_unprotected_positions(), Simulate a position existing in get_open_positions() with no matching open OCO o, Replicates the unprotected position verification routine in main.py, Simulate a position existing in get_open_positions() WITH a matching open OCO or, test_protected_position_no_alert(), test_unprotected_position_alerting_path()

### Community 25 - "init_db"
Cohesion: 0.11
Nodes (27): get_all_ledger_entries(), init_db(), Retrieves all thesis_ledger records sorted by id DESC., Initializes the SQLite database schema if tables do not exist., fixture, temp_db(), fixture, temp_db() (+19 more)

### Community 26 - "AnalyticsEngine"
Cohesion: 0.33
Nodes (3): AnalyticsEngine, DataFrame, Takes the history dataframe from BacktestEngine and generates a quantstats HTML

### Community 27 - "test_dashboard.py"
Cohesion: 0.25
Nodes (9): main(), Terminal CLI dashboard for research_scanner. Lists unreviewed candidate items fr, Fetches and displays unreviewed candidates from the database in a terminal-frien, render_dashboard(), fixture, Unit tests for research_scanner.dashboard module., temp_db_with_candidates(), test_render_dashboard_min_score_filter() (+1 more)

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

### Community 33 - "OrderManager"
Cohesion: 0.25
Nodes (4): OrderManager, Formulates a standard market order for delta-based execution.         action: 'B, Routes the bracket order to Alpaca., TestOrderManager

### Community 34 - "LimitOrderRequest"
Cohesion: 0.25
Nodes (4): LimitOrderRequest, TimeInForce, test_oco(), AdvancedLimitOrderRequest

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

### Community 60 - ".generate_signal"
Cohesion: 0.50
Nodes (3): DataFrame, Series, Calculates zero-lag momentum using an Adaptive Kalman Filter state-space model.

### Community 72 - "RegimeDetector"
Cohesion: 0.33
Nodes (3): DataFrame, Classifies market structure into distinct regimes.         market_returns: df wh, RegimeDetector

### Community 73 - ".fetch_historical_data"
Cohesion: 0.40
Nodes (3): DataFrame, Fetches daily bars for the given symbols from Alpaca.         Returns a wide-for, Fetches macroeconomic covariates (^VIX, ^TNX) from Yahoo Finance.         Return

### Community 74 - "resolve_peak_nav"
Cohesion: 0.50
Nodes (4): Resolves the peak NAV using Redis with a disk-backed fallback., resolve_peak_nav(), Simulate Redis being unavailable (None or throwing exception) or returning no st, test_drawdown_persistence_redis_unavailable_disk_fallback()

### Community 75 - "test_export_to_obsidian.py"
Cohesion: 0.11
Nodes (31): get_unreviewed_candidates(), mark_candidate_reviewed(), Retrieves all unreviewed candidates (reviewed = 0 or NULL) scoring at or above m, Marks a candidate as reviewed (reviewed = 1) given its database ID.     Returns, ensure_theme_note_exists(), export_candidate_to_vault(), export_unreviewed_candidates(), format_theme_title() (+23 more)

### Community 108 - "triage_item"
Cohesion: 0.23
Nodes (14): Unit tests for research_scanner.triage module., test_build_triage_prompt(), test_extract_json_payload(), test_triage_item_malformed_json(), test_triage_item_ollama_down(), test_triage_item_success(), build_triage_prompt(), extract_json_payload() (+6 more)

### Community 111 - "research_scanner"
Cohesion: 0.12
Nodes (16): 1. Install Ollama & Pull Gemma Model, 1. Running the Fetch & Triage Scanner, 2. Install Python Dependencies, 2. Terminal CLI Dashboard (`dashboard.py`), 3. Environment & Credentials Configuration, 3. Exporting to Obsidian (`export_to_obsidian.py`), 4. Vault Thesis Ledger Scan (`thesis_ledger.py`), 5. Forward Performance Scoring & Statistical Report (`scoring.py`) (+8 more)

### Community 116 - "AI Hardware Accelerators"
Cohesion: 0.50
Nodes (3): AI Hardware Accelerators, Investment Thesis Audits, Sub-topics & Architecture

### Community 132 - ".generate_signal"
Cohesion: 0.50
Nodes (3): DataFrame, Series, Generates portfolio weights based on statistical mean reversion.         Assets

### Community 133 - ".generate_signal"
Cohesion: 0.50
Nodes (3): DataFrame, Series, Generates portfolio weights based on cross-sectional momentum.         close_dat

## Knowledge Gaps
- **117 isolated node(s):** `start.sh script`, `graphify`, `Workflow: graphify`, `graphify`, `1. Thesis Summary` (+112 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AlpacaDataFetcher` connect `BacktestEngine` to `SECForm4Parser`, `.fetch_historical_data`, `TradingSystem`, `bootstrap_model.py`, `trading_system/main.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Why does `TradingSystem` connect `TradingSystem` to `OrderManager`, `AlpacaTradingClient`, `PortfolioRanker`, `RegimeDetector`, `engine.py`, `GovernanceEngine`, `BacktestEngine`, `bootstrap_model.py`, `trading_system/main.py`, `TemporalAligner`, `.__init__`?**
  _High betweenness centrality (0.021) - this node is a cross-community bridge._
- **Why does `InsiderClusterBacktester` connect `SECForm4Parser` to `BacktestEngine`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BacktestEngine` (e.g. with `DeepOrthogonalizer` and `EnsembleAgent`) actually correct?**
  _`BacktestEngine` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `TradingSystem` (e.g. with `EnsembleAgent` and `RegimeDetector`) actually correct?**
  _`TradingSystem` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `AlpacaDataFetcher` (e.g. with `InsiderClusterBacktester` and `TradingSystem`) actually correct?**
  _`AlpacaDataFetcher` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `start.sh script`, `graphify`, `Workflow: graphify` to the rest of the system?**
  _117 weakly-connected nodes found - possible documentation gaps or missing edges._