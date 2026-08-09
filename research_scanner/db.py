"""
Database storage module for research_scanner using SQLite.
Stores fetched items (deduplicated by item_hash) and candidate items scoring above threshold.
"""

import hashlib
import sqlite3
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger("research_scanner.db")


def compute_item_hash(source: str, external_id: str) -> str:
    """
    Computes a deterministic SHA256 hash for deduplication given a source and external_id.
    """
    raw_str = f"{source.strip().lower()}:{str(external_id).strip()}"
    return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """
    Creates and returns a SQLite connection with row factory set to sqlite3.Row.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    """
    Initializes the SQLite database schema if tables do not exist.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS fetched_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_hash TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT,
                    summary TEXT,
                    consumed_by_curator INTEGER DEFAULT 0,
                    curator_decision TEXT,
                    request_id INTEGER,
                    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_fetched_items_hash ON fetched_items(item_hash);
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS candidates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fetched_item_hash TEXT UNIQUE NOT NULL,
                    source TEXT NOT NULL,
                    external_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT,
                    summary TEXT,
                    score REAL NOT NULL,
                    reason TEXT NOT NULL,
                    category TEXT NOT NULL,
                    reviewed INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (fetched_item_hash) REFERENCES fetched_items(item_hash)
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_candidates_hash ON candidates(fetched_item_hash);
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS director_requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL,
                    source_hint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS thesis_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_hash TEXT UNIQUE NOT NULL,
                    ticker TEXT NOT NULL,
                    audit_date TEXT NOT NULL,
                    confidence_level TEXT NOT NULL,
                    fact_check_verdict TEXT NOT NULL,
                    theme_note TEXT NOT NULL,
                    vault_note_path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_thesis_ledger_hash ON thesis_ledger(ledger_hash);
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS thesis_scores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ledger_id INTEGER NOT NULL,
                    horizon_days INTEGER NOT NULL,
                    ticker TEXT NOT NULL,
                    entry_date TEXT NOT NULL,
                    exit_date TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    gross_return REAL NOT NULL,
                    net_return REAL NOT NULL,
                    baseline_ticker TEXT NOT NULL,
                    baseline_net_return REAL NOT NULL,
                    price_source TEXT,
                    baseline_price_source TEXT,
                    scored_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (ledger_id) REFERENCES thesis_ledger(id),
                    UNIQUE(ledger_id, horizon_days)
                );
            """)

            # Auto-migration: ensure 'reviewed' column exists if table was created in earlier schema
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(candidates);")
            columns = [col[1] for col in cursor.fetchall()]
            if "reviewed" not in columns:
                conn.execute("ALTER TABLE candidates ADD COLUMN reviewed INTEGER DEFAULT 0;")

            # Auto-migration: ensure 'consumed_by_curator', 'curator_decision', and 'request_id' columns exist
            cursor.execute("PRAGMA table_info(fetched_items);")
            fetched_cols = [col[1] for col in cursor.fetchall()]
            if "consumed_by_curator" not in fetched_cols:
                conn.execute("ALTER TABLE fetched_items ADD COLUMN consumed_by_curator INTEGER DEFAULT 0;")
            if "curator_decision" not in fetched_cols:
                conn.execute("ALTER TABLE fetched_items ADD COLUMN curator_decision TEXT;")
            if "request_id" not in fetched_cols:
                conn.execute("ALTER TABLE fetched_items ADD COLUMN request_id INTEGER;")

            # Auto-migration: ensure 'price_source' and 'baseline_price_source' columns exist in thesis_scores
            cursor.execute("PRAGMA table_info(thesis_scores);")
            score_cols = [col[1] for col in cursor.fetchall()]
            if "price_source" not in score_cols:
                conn.execute("ALTER TABLE thesis_scores ADD COLUMN price_source TEXT;")
            if "baseline_price_source" not in score_cols:
                conn.execute("ALTER TABLE thesis_scores ADD COLUMN baseline_price_source TEXT;")

        logger.info("Database initialized at %s", db_path)
    finally:
        conn.close()


def is_item_fetched(db_path: str, item_hash: str) -> bool:
    """
    Checks whether an item with the given hash has already been stored in fetched_items.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM fetched_items WHERE item_hash = ?", (item_hash,))
        return cursor.fetchone() is not None
    finally:
        conn.close()


def save_fetched_item(db_path: str, item: Dict[str, Any]) -> bool:
    """
    Saves a newly fetched item into the fetched_items table.
    Returns True if inserted, False if item_hash already existed.
    """
    item_hash = item.get("item_hash") or compute_item_hash(item["source"], item["external_id"])
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO fetched_items (item_hash, source, external_id, title, url, summary, request_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_hash,
                    item["source"],
                    str(item["external_id"]),
                    item.get("title", ""),
                    item.get("url", ""),
                    item.get("summary", ""),
                    item.get("request_id"),
                ),
            )
        return True
    except sqlite3.IntegrityError:
        logger.debug("Item hash %s already exists in database.", item_hash)
        return False
    finally:
        conn.close()


def save_candidate(db_path: str, candidate: Dict[str, Any]) -> bool:
    """
    Saves a candidate item scoring above threshold into the candidates table.
    Returns True if inserted, False if candidate already existed.
    """
    item_hash = candidate.get("item_hash") or compute_item_hash(candidate["source"], candidate["external_id"])
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO candidates (fetched_item_hash, source, external_id, title, url, summary, score, reason, category, reviewed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item_hash,
                    candidate["source"],
                    str(candidate["external_id"]),
                    candidate.get("title", ""),
                    candidate.get("url", ""),
                    candidate.get("summary", ""),
                    float(candidate["score"]),
                    candidate.get("reason", ""),
                    candidate.get("category", ""),
                    int(candidate.get("reviewed", 0)),
                ),
            )
        logger.info("Saved candidate [%s] score=%.1f: %s", candidate["source"], candidate["score"], candidate.get("title"))
        return True
    except sqlite3.IntegrityError:
        logger.debug("Candidate hash %s already exists in candidates table.", item_hash)
        return False
    finally:
        conn.close()


def get_all_candidates(db_path: str) -> List[Dict[str, Any]]:
    """
    Retrieves all records from candidates table as a list of dicts.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM candidates ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_unreviewed_candidates(db_path: str, min_score: float = 0.0) -> List[Dict[str, Any]]:
    """
    Retrieves all unreviewed candidates (reviewed = 0 or NULL) scoring at or above min_score,
    sorted by score descending, then created_at descending.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM candidates
            WHERE (reviewed IS NULL OR reviewed = 0) AND score >= ?
            ORDER BY score DESC, created_at DESC
            """,
            (float(min_score),),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def mark_candidate_reviewed(db_path: str, candidate_id: int) -> bool:
    """
    Marks a candidate as reviewed (reviewed = 1) given its database ID.
    Returns True if row was updated.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE candidates SET reviewed = 1 WHERE id = ?",
                (candidate_id,),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_unconsumed_items(db_path: str) -> List[Dict[str, Any]]:
    """
    Retrieves all fetched items that have not yet been consumed by the curator.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT * FROM fetched_items
            WHERE (consumed_by_curator IS NULL OR consumed_by_curator = 0)
            ORDER BY fetched_at DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_fetched_item_by_id(db_path: str, item_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieves a fetched item by its database ID.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM fetched_items WHERE id = ?", (item_id,))
        row = cursor.fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def mark_item_consumed(db_path: str, item_id: int, decision: str = "promoted") -> bool:
    """
    Marks a fetched item as consumed (consumed_by_curator = 1) given its database ID.
    Sets curator_decision to decision (default: "promoted").
    Returns True if row was updated.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE fetched_items SET consumed_by_curator = 1, curator_decision = ? WHERE id = ?",
                (decision, item_id),
            )
            return cursor.rowcount > 0
    finally:
        conn.close()


def mark_items_reviewed(db_path: str, item_ids: List[int], decision: str = "reviewed_not_promoted") -> int:
    """
    Marks fetched items as reviewed (consumed_by_curator = 1, curator_decision = decision)
    for a list of item IDs without requiring a note to be written.
    Returns the number of rows updated.
    """
    if not item_ids:
        return 0
    init_db(db_path)
    conn = get_db_connection(db_path)
    try:
        with conn:
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in item_ids)
            cursor.execute(
                f"UPDATE fetched_items SET consumed_by_curator = 1, curator_decision = ? WHERE id IN ({placeholders})",
                (decision, *item_ids),
            )
            return cursor.rowcount
    finally:
        conn.close()


def save_thesis_ledger_entry(db_path: str, entry: Dict[str, Any]) -> bool:
    """
    Saves an immutable audit thesis record into thesis_ledger.
    Returns True if saved, False if ledger_hash already existed.
    Once written, a ledger row is NEVER edited or deleted.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO thesis_ledger (
                    ledger_hash, ticker, audit_date, confidence_level,
                    fact_check_verdict, theme_note, vault_note_path
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entry["ledger_hash"],
                    entry["ticker"].strip().upper(),
                    entry["audit_date"].strip(),
                    entry["confidence_level"].strip(),
                    entry["fact_check_verdict"].strip(),
                    entry["theme_note"].strip(),
                    entry["vault_note_path"].strip(),
                ),
            )
        logger.info(
            "Saved immutable thesis ledger entry [%s] ticker=%s verdict=%s",
            entry["ledger_hash"][:10],
            entry["ticker"],
            entry["fact_check_verdict"],
        )
        return True
    except sqlite3.IntegrityError:
        logger.debug("Thesis ledger hash %s already exists in database.", entry.get("ledger_hash"))
        return False
    finally:
        conn.close()


def get_all_ledger_entries(db_path: str) -> List[Dict[str, Any]]:
    """
    Retrieves all thesis_ledger records sorted by id DESC.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM thesis_ledger ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_unscored_ledger_entries(db_path: str, horizon_days: int) -> List[Dict[str, Any]]:
    """
    Retrieves all thesis_ledger entries that have NOT yet been scored for the given horizon_days.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT l.* FROM thesis_ledger l
            LEFT JOIN thesis_scores s ON l.id = s.ledger_id AND s.horizon_days = ?
            WHERE s.id IS NULL
            ORDER BY l.id ASC
            """,
            (horizon_days,),
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def save_thesis_score(db_path: str, score_record: Dict[str, Any]) -> bool:
    """
    Saves a scored thesis evaluation record into thesis_scores.
    """
    conn = get_db_connection(db_path)
    try:
        with conn:
            conn.execute(
                """
                INSERT INTO thesis_scores (
                    ledger_id, horizon_days, ticker, entry_date, exit_date,
                    entry_price, exit_price, gross_return, net_return,
                    baseline_ticker, baseline_net_return, price_source, baseline_price_source
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    score_record["ledger_id"],
                    score_record["horizon_days"],
                    score_record["ticker"],
                    score_record["entry_date"],
                    score_record["exit_date"],
                    float(score_record["entry_price"]),
                    float(score_record["exit_price"]),
                    float(score_record["gross_return"]),
                    float(score_record["net_return"]),
                    score_record["baseline_ticker"],
                    float(score_record["baseline_net_return"]),
                    score_record.get("price_source"),
                    score_record.get("baseline_price_source"),
                ),
            )
        logger.info(
            "Saved thesis score ledger_id=%d horizon=%dD net_ret=%.4f (baseline=%.4f)",
            score_record["ledger_id"],
            score_record["horizon_days"],
            score_record["net_return"],
            score_record["baseline_net_return"],
        )
        return True
    except sqlite3.IntegrityError:
        logger.debug(
            "Thesis score already exists for ledger_id=%s horizon=%s",
            score_record.get("ledger_id"),
            score_record.get("horizon_days"),
        )
        return False
    finally:
        conn.close()


def get_all_thesis_scores(db_path: str) -> List[Dict[str, Any]]:
    """
    Retrieves all records from thesis_scores JOINed with thesis_ledger metadata.
    """
    conn = get_db_connection(db_path)
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT s.*, l.confidence_level, l.fact_check_verdict, l.theme_note, l.audit_date
            FROM thesis_scores s
            JOIN thesis_ledger l ON s.ledger_id = l.id
            ORDER BY s.id DESC
            """
        )
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


