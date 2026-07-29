# Graph Report - Trading  (2026-07-27)

## Corpus Check
- 148 files · ~459,366 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 527 nodes · 642 edges · 95 communities (82 shown, 13 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 31 edges (avg confidence: 0.52)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- main.py
- EnsembleAgent
- engine.py
- ConditionalAutoencoder
- TradingSystem
- PortfolioRanker
- GovernanceEngine
- .predict
- ThompsonSampler
- AnalyticsEngine
- check_unprotected_positions
- orchestrate_daily.py
- Model Card for Model ID
- health_monitor.py
- scan_biotech.py
- orchestrate_bootstrap.py
- fetch_and_build_report.py
- scan_fintech.py
- scan_mining.py
- sec_scanner.py
- start.sh
- Model Card for Model ID
- **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**
- .create_oco_order
- TemporalAligner
- SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)
- SEC Filings & Market Data Reactions
- .fetch_historical_data
- Filtered SEC Filings Subset
- Baseline Price-Reaction Classification (Random Dates)
- SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors
- AI Statistical Arbitrage Backtest - Backtest Report
- Deep OFI Agent Only (2020-2022) - Backtest Report
- SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies
- SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies
- Rules for Backtesting, Model Training, and Risk Parameters
- AI Arbitrage Backtest 2024 - Backtest Report
- AI Arbitrage Backtest 2025 - Backtest Report
- .isolate
- rules/graphify.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `BacktestEngine` - 28 edges
2. `TradingSystem` - 22 edges
3. `AlpacaDataFetcher` - 18 edges
4. `OrderManager` - 17 edges
5. `PortfolioRanker` - 16 edges
6. `Model Card for Model ID` - 15 edges
7. `Model Card for Model ID` - 15 edges
8. `AlpacaTradingClient` - 14 edges
9. `GovernanceEngine` - 14 edges
10. `ChronosInference` - 12 edges

## Surprising Connections (you probably didn't know these)
- `BacktestEngine` --uses--> `EnsembleAgent`  [INFERRED]
  backtest/engine.py → core/ensemble_agent.py
- `BacktestEngine` --uses--> `RegimeDetector`  [INFERRED]
  backtest/engine.py → core/regime_detector.py
- `BacktestEngine` --uses--> `GovernanceEngine`  [INFERRED]
  backtest/engine.py → governance/firewall.py
- `BacktestEngine` --uses--> `AdaptiveKalmanAgent`  [INFERRED]
  backtest/engine.py → signals/kalman_agent.py
- `BacktestEngine` --uses--> `PortfolioRanker`  [INFERRED]
  backtest/engine.py → signals/ranking.py

## Import Cycles
- None detected.

## Communities (95 total, 13 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (23): AlpacaTradingClient, Retrieves current account equity for sizing limits., Retrieves the current market clock., Retrieves all currently open positions., Cancels all pending or open orders to prevent conflicting executions., Closes all open positions on Alpaca., Cancels all pending/open orders and blocks until Alpaca confirms they are fully, OrderManager (+15 more)

### Community 1 - "EnsembleAgent"
Cohesion: 0.29
Nodes (3): EnsembleAgent, Executes Mean-Variance Thompson Sampling (MVTS) with Combinatorial Adaptive Disc, Updates the MVTS priors using CADTS geometric discounting based on continuous re

### Community 2 - "engine.py"
Cohesion: 0.06
Nodes (38): BacktestEngine, DataFrame, load_data(), main(), run_backtest(), run_backtest(), run_backtest(), BaseModel (+30 more)

### Community 3 - "ConditionalAutoencoder"
Cohesion: 0.22
Nodes (5): ConditionalAutoencoder, DataFrame, Orthogonalizes returns using a Conditional Autoencoder in a strictly CAUSAL roll, Deep neural network that learns complex, non-linear market beta conditioned on f, ndarray

### Community 4 - "TradingSystem"
Cohesion: 0.08
Nodes (18): DataFrame, Classifies market structure into distinct regimes.         market_returns: df wh, RegimeDetector, DataFrame, Resolves the peak NAV using Redis with a disk-backed fallback., resolve_peak_nav(), TradingSystem, run_test() (+10 more)

### Community 5 - "PortfolioRanker"
Cohesion: 0.13
Nodes (12): MeanReversionAgent, DataFrame, Series, Generates portfolio weights based on statistical mean reversion.         Assets, MomentumAgent, DataFrame, Series, Generates portfolio weights based on cross-sectional momentum.         close_dat (+4 more)

### Community 6 - "GovernanceEngine"
Cohesion: 0.16
Nodes (11): AuditLogger, Commits blocked or modified trade rationales to an immutable log., GovernanceEngine, DataFrame, Series, Applies agent-specific rules before blending, followed by global portfolio const, Assert that instantiating GovernanceEngine() with no arguments produces the new, Test drawdown circuit breaker edge cases: account_nav exactly at the drawdown th (+3 more)

### Community 7 - ".predict"
Cohesion: 0.33
Nodes (3): AutoGluon Integration: Initialize the training loop using autogluon.timeseries w, Given the 100-day padded context, predicts the next step expecting quantiles 0.1, TimeSeriesDataFrame

### Community 8 - "ThompsonSampler"
Cohesion: 0.31
Nodes (3): Samples from the Beta distribution for each agent to determine dynamic trust wei, Update Beta priors based on binary trade outcomes.         profit_outcome: True, ThompsonSampler

### Community 9 - "AnalyticsEngine"
Cohesion: 0.33
Nodes (3): AnalyticsEngine, DataFrame, Takes the history dataframe from BacktestEngine and generates a quantstats HTML

### Community 10 - "check_unprotected_positions"
Cohesion: 0.38
Nodes (6): check_unprotected_positions(), Simulate a position existing in get_open_positions() with no matching open OCO o, Replicates the unprotected position verification routine in main.py, Simulate a position existing in get_open_positions() WITH a matching open OCO or, test_protected_position_no_alert(), test_unprotected_position_alerting_path()

### Community 11 - "orchestrate_daily.py"
Cohesion: 0.70
Nodes (4): get_run_state(), main(), run_command(), save_run_state()

### Community 12 - "Model Card for Model ID"
Cohesion: 0.05
Nodes (37): Bias, Risks, and Limitations, Citation [optional], Compute Infrastructure, Direct Use, Downstream Use [optional], Environmental Impact, Evaluation, Factors (+29 more)

### Community 13 - "health_monitor.py"
Cohesion: 0.83
Nodes (3): check_health(), log_state(), run_cmd()

### Community 73 - "Model Card for Model ID"
Cohesion: 0.05
Nodes (37): Bias, Risks, and Limitations, Citation [optional], Compute Infrastructure, Direct Use, Downstream Use [optional], Environmental Impact, Evaluation, Factors (+29 more)

### Community 74 - "**Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**"
Cohesion: 0.10
Nodes (19): **Addressing Non-Stationarity with CADTS**, **Advanced Methodologies for Decoupled Risk Management in Multi-Agent Algorithmic Trading Systems**, **AlphaEval Metrics: Information Coefficient (IC)**, **Average True Range (ATR) Dynamics**, **Conclusion**, **Continuous Adaptive Pipelines**, **Econometric Variance Forecasting: The GARCH Family**, **Institutional Decoupling of Alpha and Execution** (+11 more)

### Community 75 - ".create_oco_order"
Cohesion: 0.25
Nodes (4): LimitOrderRequest, test_oco(), AdvancedLimitOrderRequest, TimeInForce

### Community 76 - "TemporalAligner"
Cohesion: 0.32
Nodes (4): DataFrame, Aligns a long-format DataFrame to a continuous time index, padding missing dates, TemporalAligner, test_temporal_alignment()

### Community 77 - "SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)"
Cohesion: 0.29
Nodes (6): 1. Dataset & Bar Window Coverage Summary, 2. Direct Comparison Results, 3. Industry-Level Breakdown, 4. Key Findings & Strategic Conclusion, Executive Summary, SEC 8-K Price & Volume Reaction Comparison: "Yes" (Agent Flagged) vs. "No" (Random Matched Baseline)

### Community 78 - "SEC Filings & Market Data Reactions"
Cohesion: 0.33
Nodes (5): Market Data Price & Volume Reactions, Notes on Insufficient Data Filings, SEC Filings Disclosure List, SEC Filings & Market Data Reactions, Summary

### Community 79 - ".fetch_historical_data"
Cohesion: 0.40
Nodes (3): DataFrame, Fetches daily bars for the given symbols from Alpaca.         Returns a wide-for, Fetches macroeconomic covariates (^VIX, ^TNX) from Yahoo Finance.         Return

### Community 80 - "Filtered SEC Filings Subset"
Cohesion: 0.40
Nodes (4): Filtered Market Data Price & Volume Reactions, Filtered SEC Filings Subset, Filtering Funnel & Breakdown, Summary

### Community 81 - "Baseline Price-Reaction Classification (Random Dates)"
Cohesion: 0.40
Nodes (4): Baseline Price-Reaction Classification (Random Dates), Direct Comparison: Filing-Linked vs. Random Baseline Data, Key Takeaways, Random Baseline Market Data Reactions Table

### Community 82 - "SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors"
Cohesion: 0.40
Nodes (4): 1. Specialty Finance & Fintech Companies (15 Filings), 2. Mining & Exploration Companies (15 Filings), 3. Biotech & Pharma Companies (15 Filings), SEC Form 8-K Filings Master Review: 45 Small-Cap Companies across Specialty Finance, Mining, and Biotech Sectors

### Community 83 - "AI Statistical Arbitrage Backtest - Backtest Report"
Cohesion: 0.50
Nodes (3): Agent Performance Summary, AI Statistical Arbitrage Backtest - Backtest Report, Summary Metrics

### Community 84 - "Deep OFI Agent Only (2020-2022) - Backtest Report"
Cohesion: 0.50
Nodes (3): Agent Performance Summary, Deep OFI Agent Only (2020-2022) - Backtest Report, Summary Metrics

### Community 85 - "SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies"
Cohesion: 0.50
Nodes (3): Detailed SEC 8-K Filings Analysis, Executive Summary, SEC 8-K Filings Review: Small-Cap Biotech & Pharma Companies

### Community 86 - "SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies"
Cohesion: 0.50
Nodes (3): Detailed SEC 8-K Filings Analysis, Executive Summary, SEC 8-K Filings Review: Small-Cap Specialty Finance & Fintech Companies

## Knowledge Gaps
- **93 isolated node(s):** `start.sh script`, `graphify`, `Workflow: graphify`, `graphify`, `Summary Metrics` (+88 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `TradingSystem` connect `TradingSystem` to `main.py`, `EnsembleAgent`, `engine.py`, `PortfolioRanker`, `GovernanceEngine`, `TemporalAligner`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **Why does `BacktestEngine` connect `engine.py` to `main.py`, `EnsembleAgent`, `TradingSystem`, `PortfolioRanker`, `GovernanceEngine`?**
  _High betweenness centrality (0.034) - this node is a cross-community bridge._
- **Why does `PortfolioRanker` connect `PortfolioRanker` to `main.py`, `engine.py`, `TradingSystem`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 11 inferred relationships involving `BacktestEngine` (e.g. with `DeepOrthogonalizer` and `EnsembleAgent`) actually correct?**
  _`BacktestEngine` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 13 inferred relationships involving `TradingSystem` (e.g. with `EnsembleAgent` and `RegimeDetector`) actually correct?**
  _`TradingSystem` has 13 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `OrderManager` (e.g. with `TradingSystem` and `TestOrderManager`) actually correct?**
  _`OrderManager` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `PortfolioRanker` (e.g. with `BacktestEngine` and `TradingSystem`) actually correct?**
  _`PortfolioRanker` has 4 INFERRED edges - model-reasoned connections that need verification._