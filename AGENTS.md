# Rules for Backtesting, Model Training, and Risk Parameters

1. No backtest or strategy evaluation may ever run with transaction costs set to zero.
2. No hyperparameter search, model training, or parameter tuning may ever be scored on the same data it was fit or searched on. Every result must report both an in-sample and a genuinely held-out out-of-sample number, clearly labeled as such.
3. Any result that looks unusually strong (e.g. a Sharpe ratio above roughly 3, which no real-world trading strategy sustains) must be treated as a likely bug or data leakage, not a success, until independently reproduced on fresh data the model/parameters have never seen.
4. A test suite claiming to verify a bug fix is not trustworthy until it has been shown to fail when the original bug is deliberately reintroduced. A passing test suite alone is not sufficient evidence a fix works.
5. No leverage increase, new capital commitment, or live-configuration change may ever be justified using backtest results that haven't gone through rules 1-4.
6. A test must import and exercise the actual production function or module it claims to verify. A test that reimplements the logic under test inside the test file itself (rather than calling the real code) provides no real verification and must be rewritten to import from the production module directly.

## graphify

This project has a graphify knowledge graph at `graphify-out/`.

Rules:
- For codebase or architecture questions, when `graphify-out/graph.json` exists, first run `graphify query "<question>"` (CLI) or `query_graph` (MCP). Use `graphify path "<A>" "<B>"` / `shortest_path` for relationships and `graphify explain "<concept>"` / `get_node` for focused concepts.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw files.
- Read `graphify-out/GRAPH_REPORT.md` for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code files in a session, run `graphify update .` to keep the graph current (AST-only, no API cost).
