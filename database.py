import sqlite3
from datetime import datetime
import threading
from config import DB_PATH

class Database:
    """
    Complete SQLite database layer for the toolkit.
    All data persisted between sessions. Thread-safe execution.
    """

    SCHEMA = """
    CREATE TABLE IF NOT EXISTS command_log (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp   TEXT NOT NULL,
        command     TEXT NOT NULL,
        output      TEXT,
        error       TEXT,
        status      TEXT,   -- success/error/warning
        duration_ms INTEGER,
        technician  TEXT,
        machine     TEXT,
        panel       TEXT    -- which panel triggered it
    );

    CREATE TABLE IF NOT EXISTS tickets (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_number   TEXT UNIQUE,
        title           TEXT NOT NULL,
        description     TEXT,
        priority        TEXT,   -- low/medium/high/critical
        status          TEXT,   -- open/in_progress/resolved/closed
        category        TEXT,   -- network/system/hardware/software/other
        assigned_to     TEXT,
        machine         TEXT,
        created_at      TEXT,
        updated_at      TEXT,
        resolved_at     TEXT,
        notes           TEXT    -- JSON array of notes
    );

    CREATE TABLE IF NOT EXISTS devices (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        ip              TEXT UNIQUE NOT NULL,
        hostname        TEXT,
        mac_address     TEXT,
        device_type     TEXT,
        os_info         TEXT,
        status          TEXT,
        open_ports      TEXT,   -- JSON array
        canvas_x        REAL,   -- Saved topology position
        canvas_y        REAL,
        notes           TEXT,
        first_seen      TEXT,
        last_seen       TEXT,
        details         TEXT    -- JSON blob
    );

    CREATE TABLE IF NOT EXISTS alert_rules (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_id     TEXT UNIQUE,
        name        TEXT,
        level       TEXT,
        metric      TEXT,
        threshold   REAL,
        duration    INTEGER,
        enabled     INTEGER,    -- 1/0
        targets     TEXT,       -- JSON array of emails
        cooldown    INTEGER,
        last_fired  TEXT,
        created_at  TEXT
    );

    CREATE TABLE IF NOT EXISTS settings (
        key         TEXT PRIMARY KEY,
        value       TEXT,
        updated_at  TEXT
    );
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.executescript(self.SCHEMA)
            self.conn.commit()

    def execute(self, query, params=()):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            self.conn.commit()
            return cursor

    def fetchall(self, query, params=()):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def fetchone(self, query, params=()):
        with self.lock:
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchone()

    def close(self):
        try:
            self.conn.close()
        except:
            pass

db = Database()
