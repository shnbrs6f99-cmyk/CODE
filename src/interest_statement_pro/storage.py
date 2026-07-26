from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

from platformdirs import user_data_path

from .domain import InterestRules


class Database:
    def __init__(self, path: Path | None = None) -> None:
        if path is None:
            base = user_data_path("InterestStatementGeneratorPro", "Jinesh")
            self.path = base / "app.db"
        else:
            self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.migrate()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        conn.execute("PRAGMA journal_mode=WAL")
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def migrate(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS schema_version(version INTEGER NOT NULL);
                INSERT INTO schema_version(version)
                SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM schema_version);
                CREATE TABLE IF NOT EXISTS customers(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                    email TEXT NOT NULL DEFAULT '',
                    phone TEXT NOT NULL DEFAULT '',
                    gstin TEXT NOT NULL DEFAULT '',
                    interest_rate TEXT NOT NULL DEFAULT '18',
                    credit_period_days INTEGER NOT NULL DEFAULT 30,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS settings(
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS processing_history(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_path TEXT NOT NULL,
                    source_hash TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    output_path TEXT,
                    message TEXT NOT NULL DEFAULT '',
                    processed_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_history_hash ON processing_history(source_hash);
                CREATE INDEX IF NOT EXISTS idx_history_customer ON processing_history(customer_name);
                """
            )

    @staticmethod
    def _utc_now() -> str:
        return datetime.now(UTC).isoformat(timespec="seconds")

    def upsert_customer(
        self,
        name: str,
        email: str = "",
        phone: str = "",
        gstin: str = "",
        rate: str = "18",
        credit_days: int = 30,
    ) -> None:
        now = self._utc_now()
        with self.connect() as db:
            db.execute(
                """INSERT INTO customers(
                    name,email,phone,gstin,interest_rate,credit_period_days,created_at,updated_at
                ) VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(name) DO UPDATE SET email=excluded.email, phone=excluded.phone,
                gstin=excluded.gstin, interest_rate=excluded.interest_rate,
                credit_period_days=excluded.credit_period_days,
                updated_at=excluded.updated_at""",
                (name.strip(), email.strip(), phone.strip(), gstin.strip(), rate, credit_days, now, now),
            )

    def customers(self) -> list[sqlite3.Row]:
        with self.connect() as db:
            return list(db.execute("SELECT * FROM customers ORDER BY name"))

    def save_setting(self, key: str, value: object) -> None:
        payload = json.dumps(value)
        with self.connect() as db:
            db.execute(
                """INSERT INTO settings(key,value,updated_at) VALUES(?,?,?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    updated_at=excluded.updated_at""",
                (key, payload, self._utc_now()),
            )

    def load_setting(self, key: str, default: object = None) -> object:
        with self.connect() as db:
            row = db.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row["value"]) if row else default

    def save_rules(self, rules: InterestRules) -> None:
        data = asdict(rules)
        data["annual_rate"] = str(rules.annual_rate)
        data["minimum_interest"] = str(rules.minimum_interest)
        data["calculate_through"] = (
            rules.calculate_through.isoformat() if rules.calculate_through else None
        )
        self.save_setting("interest_rules", data)

    def add_history(
        self,
        source: Path,
        source_hash: str,
        customer: str,
        status: str,
        output: Path | None,
        message: str = "",
    ) -> None:
        with self.connect() as db:
            db.execute(
                """INSERT INTO processing_history(
                    source_path,source_hash,customer_name,status,output_path,message,processed_at
                ) VALUES(?,?,?,?,?,?,?)""",
                (
                    str(source),
                    source_hash,
                    customer,
                    status,
                    str(output) if output else None,
                    message,
                    self._utc_now(),
                ),
            )

    def history(self, limit: int = 500) -> list[sqlite3.Row]:
        with self.connect() as db:
            return list(
                db.execute(
                    "SELECT * FROM processing_history ORDER BY id DESC LIMIT ?",
                    (limit,),
                )
            )

    def integrity_check(self) -> bool:
        with self.connect() as db:
            row = db.execute("PRAGMA integrity_check").fetchone()
        return bool(row and row[0] == "ok")
