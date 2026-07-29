# research_scanner

`research_scanner` is an automated, locally-running technology and research triage pipeline. It continuously monitors paper preprints, patent filings, and industry news, deduplicates items in a local SQLite database, passes new items to a local Gemma LLM (via Ollama) for 1-10 scoring, stores high-scoring candidates, dispatches real-time alerts to Discord, provides a terminal CLI dashboard, exports triaged candidates directly into an Obsidian vault, logs completed audit research into an immutable SQLite ledger, and tracks forward 20/60/120 trading-day cost-adjusted performance against random baseline benchmarks.

---

## Features

- **3 Free Data Sources**:
  - **arXiv API**: Category filtering (`quant-ph`, `cs.AI`, `cs.LG`, `cs.RO`) via `feedparser`.
  - **USPTO Open Data Portal (ODP)**: Patent application filtering via CPC classification codes (`G06N`, `B25J`, `H01L`) using the updated `api.uspto.gov` endpoint with `X-API-KEY`.
  - **Currents API**: Free-tier tech & industry news filtered by configurable keywords.
- **Deduplication Engine**: Uses SQLite and SHA256 hashes of `(source, external_id)` so no item is ever processed twice.
- **Local Ollama LLM Triage**: Scores new items on a 1-10 scale for industry/technology shift impact using Gemma (`gemma2:2b`). Prompts include 2-3 calibration examples and output clean JSON with consistent category tags.
- **Candidate Storage**: Persists items scoring above a configurable threshold (default `7.0`) to a `candidates` table.
- **Discord REST Notifications**: Dispatches candidate alerts and scored thesis updates directly to Discord channels via REST POST (no gateway client overhead).
- **Terminal CLI Dashboard (`dashboard.py`)**: Displays unreviewed candidates from SQLite sorted by score with filtering by minimum score.
- **Obsidian Vault Export (`export_to_obsidian.py`)**: Exports candidates as formatted Markdown notes into an Obsidian vault organized by source (`raw-signals/arxiv/`, `raw-signals/patents/`, `raw-signals/news/`), complete with YAML frontmatter (`status: triaged`), Gemma score & reason, original URL link, empty `## My Notes` section, and Obsidian `[[wikilinks]]` to auto-created theme notes.
- **Immutable Thesis Ledger (`thesis_ledger.py`)**: Scans Obsidian vault for notes containing completed `## Independent Fact-Check` sections and logs immutable audit records (`ticker`, `audit_date`, `confidence_level`, `fact_check_verdict`, `theme_note`) into the `thesis_ledger` SQLite table. Once logged, records are never edited or deleted.
- **Prospective Forward Performance Scoring (`scoring.py`)**: Evaluates thesis performance at 20, 60, and 120 trading days using Alpaca market data, applies 10bps round-trip transaction costs (`(exit/entry) * 0.999 - 1.0`), compares against paired random non-candidate baselines, sends Discord notifications, and generates aggregate statistical reports.
- **Sample Size Floor Enforcement ($N \ge 30$)**: The statistical reporting tool (`scoring.py --report`) explicitly refuses to state directional conclusions or claim predictive validity below $N = 30$ scored theses per horizon, labeling small samples as underpowered.

---

## Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running locally on `http://localhost:11434`
3. Free & Market Data API Keys:
   - **USPTO Open Data Portal**: Register at [data.uspto.gov](https://data.uspto.gov) and generate an API key.
   - **Currents API**: Register at [currentsapi.services](https://currentsapi.services/en) for a free API key.
   - **Discord Bot**: Create a Discord bot in the Discord Developer Portal and obtain a bot token and channel ID.
   - **Alpaca API**: Optional key/secret for pulling market prices for thesis scoring.

---

## Installation & Setup

### 1. Install Ollama & Pull Gemma Model

```bash
# Start Ollama service if not already running
ollama serve

# Pull the Gemma 2 2B model
ollama pull gemma2:2b
```

### 2. Install Python Dependencies

```bash
pip install feedparser requests pytest
```

### 3. Environment & Credentials Configuration

Configure in `research_scanner/config.py` or via environment variables:

```bash
export CURRENTS_API_KEY="your_currents_api_key"
export USPTO_API_KEY="your_uspto_api_key"
export DISCORD_BOT_TOKEN="your_discord_bot_token"
export DISCORD_CHANNEL_ID="your_discord_channel_id"

# Optional overrides
export SCORE_THRESHOLD="7.0"
export GEMMA_MODEL="gemma2:2b"
export OLLAMA_HOST="http://localhost:11434"
export DB_PATH="research_scanner.db"
export OBSIDIAN_VAULT_PATH="/path/to/your/ObsidianVault"
export ALPACA_API_KEY="your_alpaca_key"
export ALPACA_SECRET_KEY="your_alpaca_secret"
```

---

## Usage Guide

### 1. Running the Fetch & Triage Scanner

```bash
python3 research_scanner/scan.py
```

### 2. Terminal CLI Dashboard (`dashboard.py`)

```bash
python3 research_scanner/dashboard.py --min-score 7.5
```

### 3. Exporting to Obsidian (`export_to_obsidian.py`)

```bash
python3 research_scanner/export_to_obsidian.py --min-score 7.0 --vault /path/to/ObsidianVault
```

### 4. Vault Thesis Ledger Scan (`thesis_ledger.py`)

Scan vault notes for completed `## Independent Fact-Check` sections and update the immutable ledger:

```bash
python3 research_scanner/thesis_ledger.py --vault /path/to/ObsidianVault
```

### 5. Forward Performance Scoring & Statistical Report (`scoring.py`)

Score eligible theses (20, 60, 120 trading days post-audit) and send Discord alerts:

```bash
# Score eligible ledger entries
python3 research_scanner/scoring.py

# Print aggregate statistical performance report (with N >= 30 floor check)
python3 research_scanner/scoring.py --report
```

---

## Running Automated via Cron

To run `research_scanner` automatically every hour, add a cron job:

```bash
crontab -e
```

Example cron schedule:

```cron
0 * * * * cd /home/mason/Trading && CURRENTS_API_KEY="your_key" USPTO_API_KEY="your_key" DISCORD_BOT_TOKEN="your_token" DISCORD_CHANNEL_ID="your_id" /usr/bin/python3 research_scanner/scan.py >> /home/mason/Trading/scan.log 2>&1
0 18 * * 1-5 cd /home/mason/Trading && /usr/bin/python3 research_scanner/thesis_ledger.py && /usr/bin/python3 research_scanner/scoring.py >> /home/mason/Trading/scoring.log 2>&1
```

---

## Running Tests

Execute the automated test suite with `pytest`:

```bash
python3 -m pytest research_scanner/tests/ -v
```

---

## Project Structure

```
research_scanner/
├── __init__.py
├── config.py                 # Configuration defaults & env variable loading
├── db.py                     # SQLite schema, hash calculation, deduplication, thesis_ledger, thesis_scores
├── sources/                  # Data source modules
│   ├── __init__.py
│   ├── arxiv.py              # arXiv API fetcher via feedparser
│   ├── uspto.py              # USPTO Open Data Portal API fetcher
│   └── currents.py           # Currents API news fetcher
├── triage.py                 # Ollama / Gemma LLM triage filter & prompt formatting
├── notifier.py               # Discord REST POST alert dispatcher
├── scan.py                   # Main entrypoint script for cron execution
├── dashboard.py              # Terminal CLI candidate dashboard
├── export_to_obsidian.py     # Obsidian Markdown vault exporter
├── thesis_ledger.py          # Vault scanner & immutable thesis logger
├── scoring.py                # Prospective forward performance evaluator & statistical report
├── README.md                 # Setup and usage guide
└── tests/                    # Unit and integration test suite
    ├── test_db.py
    ├── test_sources.py
    ├── test_triage.py
    ├── test_notifier.py
    ├── test_scan.py
    ├── test_dashboard.py
    ├── test_export_to_obsidian.py
    ├── test_thesis_ledger.py
    └── test_scoring.py
```
