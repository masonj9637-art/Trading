"""
Ollama / Gemma local triage engine for scoring research items.
"""

import json
import logging
import re
from typing import Dict, Any, Optional
import requests

from research_scanner import config

logger = logging.getLogger("research_scanner.triage")

CALIBRATION_PROMPT = """You are a rapid technology research triage system. Your job is to perform a quick initial filter on newly published papers, patents, and news items.

Task:
Evaluate the item below and score it on a 1-10 scale based strictly on:
"Does this represent a notable shift in an industry or technology?"

Keep your job narrow: you are a triage filter, NOT an analyst or financial advisor. Do not provide investment advice or market predictions. Just flag items worth closer investigation.

Category Tagging Rules:
Select a short, consistent, standardized category tag for the item. Keep the tag vocabulary reasonably small and canonical (e.g. "quantum computing", "ai & machine learning", "robotics", "biotech", "semiconductors", "energy & materials", "other") to link related items downstream.

Calibration Examples:

Example 1 (Low Notability - Score ~2):
Title: "Minor performance tweaks and hyperparameter tuning for ResNet-18 on small benchmark dataset"
JSON Response: {{"score": 2, "reason": "Incremental optimization of existing model with minimal industry impact.", "category": "ai & machine learning"}}

Example 2 (High Notability - Score ~9):
Title: "Fault-tolerant room-temperature 10,000-qubit quantum processor architecture demonstration"
JSON Response: {{"score": 9, "reason": "Major engineering breakthrough overcoming core scalability bottleneck in quantum hardware.", "category": "quantum computing"}}

Item to Evaluate:
Source: {source}
Title: {title}
Summary/Abstract: {summary}

Respond ONLY with a single JSON object containing keys:
- "score": integer 1-10
- "reason": short string (1-2 sentences explaining score)
- "category": short standard category tag
"""


def build_triage_prompt(item: Dict[str, Any]) -> str:
    """
    Constructs the prompt for Gemma including instructions, calibration examples, and item details.
    """
    return CALIBRATION_PROMPT.format(
        source=item.get("source", "unknown"),
        title=item.get("title", "").strip(),
        summary=item.get("summary", "").strip() or "No summary provided.",
    )


def extract_json_payload(raw_response: str) -> Dict[str, Any]:
    """
    Extracts and parses JSON object from LLM response text, handling potential Markdown formatting.
    """
    cleaned = raw_response.strip()
    # Strip markdown block delimiters if present
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        cleaned = cleaned.strip()

    # Locate first { and last }
    start_idx = cleaned.find("{")
    end_idx = cleaned.rfind("}")
    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        cleaned = cleaned[start_idx : end_idx + 1]

    return json.loads(cleaned)


def triage_item(
    item: Dict[str, Any],
    ollama_host: Optional[str] = None,
    model_name: Optional[str] = None,
    timeout: int = 30,
) -> Optional[Dict[str, Any]]:
    """
    Sends an item to the local Ollama API running Gemma to evaluate its industry/technology shift score.

    :param item: Item dict with source, title, summary, etc.
    :param ollama_host: Ollama API host URL (defaults to config.OLLAMA_HOST)
    :param model_name: Ollama model tag (defaults to config.GEMMA_MODEL)
    :param timeout: HTTP request timeout in seconds
    :return: Dict with score, reason, category, or None if triage failed
    """
    host = ollama_host or config.OLLAMA_HOST
    model = model_name or config.GEMMA_MODEL
    url = f"{host.rstrip('/')}/api/generate"

    prompt = build_triage_prompt(item)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
    }

    try:
        logger.info("Sending item [%s] '%s' to Ollama model '%s'", item.get("source"), item.get("title"), model)
        response = requests.post(url, json=payload, timeout=timeout)

        if response.status_code != 200:
            logger.warning("Ollama API error (%d): %s", response.status_code, response.text[:200])
            return None

        res_data = response.json()
        raw_output = res_data.get("response", "")
        if not raw_output:
            logger.warning("Ollama API returned empty response string.")
            return None

        result_json = extract_json_payload(raw_output)

        score_raw = result_json.get("score")
        reason = str(result_json.get("reason", "")).strip()
        category = str(result_json.get("category", "")).strip().lower()

        if score_raw is None:
            logger.warning("Parsed JSON missing 'score' field: %s", result_json)
            return None

        score = float(score_raw)
        score = max(1.0, min(10.0, score))  # Clamp to [1, 10]

        logger.info("Triage result for '%s': score=%.1f category='%s'", item.get("title"), score, category)
        return {
            "score": score,
            "reason": reason or "No reason provided.",
            "category": category or "uncategorized",
        }

    except requests.RequestException as e:
        logger.error("Failed to communicate with Ollama at %s: %s", url, e)
        return None
    except (json.JSONDecodeError, ValueError) as e:
        logger.error("Failed to parse JSON response from Ollama: %s", e)
        return None
    except Exception as e:
        logger.error("Unexpected error during triage: %s", e, exc_info=True)
        return None
