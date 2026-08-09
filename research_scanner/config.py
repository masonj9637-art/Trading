"""
Configuration settings for research_scanner.

All settings (score threshold, Gemma model tag, arXiv categories, patent CPC codes,
news keywords, Ollama host, API keys, Discord credentials) live here and can be
overridden via environment variables.
"""

import os

# Load credentials_backup.md or .env if environment variables are not already set
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _env_file in [os.path.join(_repo_root, ".env"), os.path.join(_repo_root, "credentials_backup.md")]:
    if os.path.isfile(_env_file):
        with open(_env_file, "r") as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and not _line.startswith("#") and "=" in _line:
                    _k, _v = _line.split("=", 1)
                    os.environ.setdefault(_k.strip(), _v.strip())

# Database & Storage Settings
DB_PATH = os.getenv("DB_PATH", "research_scanner.db")
OBSIDIAN_VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "obsidian_vault")
CONTEXT_FOLDER_PATH = os.getenv("CONTEXT_FOLDER_PATH", "context")
LAST_SUCCESS_PATH = os.getenv(
    "LAST_SUCCESS_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "last_success.json"),
)


# Alpaca Market Data Credentials
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")

# Scoring & Risk Parameters
MIN_SAMPLE_SIZE_FLOOR = int(os.getenv("MIN_SAMPLE_SIZE_FLOOR", "30"))
TRANSACTION_COST_BPS = float(os.getenv("TRANSACTION_COST_BPS", "10"))  # 10 bps round-trip cost (0.0010)

# Triage Filter Settings (Ollama + Gemma)
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
GEMMA_MODEL = os.getenv("GEMMA_MODEL", "gemma4:e2b-it-qat")
SCORE_THRESHOLD = float(os.getenv("SCORE_THRESHOLD", "7.0"))

# Source Fetching Configuration
ARXIV_CATEGORIES = [
    "quant-ph",
    "cs.AI",
    "cs.LG",
    "cs.RO",
]

# USPTO CPC (Cooperative Patent Classification) codes for target industries
PATENT_CPC_CODES = [
    "G06N",  # Computer systems based on specific computational models (Quantum/AI)
    "B25J",  # Manipulators; Robots
    "H01L",  # Semiconductor devices
]

# Currents API News search keywords
NEWS_KEYWORDS = [
    "quantum computing",
    "artificial intelligence",
    "robotics",
    "semiconductor",
]

# API Keys & Third-Party Service Credentials (loaded from environment)
CURRENTS_API_KEY = os.getenv("CURRENTS_API_KEY", "")
USPTO_API_KEY = os.getenv("USPTO_API_KEY", "")

# Discord Notification Credentials
DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_ID = os.getenv("DISCORD_CHANNEL_ID", "1471336629321994353")
