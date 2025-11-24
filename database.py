# database.py
import sqlite3
from config import DB_NAME
from typing import List, Tuple, Optional

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    c = conn.cursor()
    # A single table for daily logs with optional extra fields
    c.execute("""
    CREATE TABLE IF NOT EXISTS daily_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        sleep_hours REAL DEFAULT 0,
        study_hours REAL DEFAULT 0,
        activities TEXT,
        mood TEXT,
        notes TEXT,
        mode TEXT DEFAULT 'student', -- 'student' or 'employee'
        timestamp TEXT,
        water_intake REAL,
        steps INTEGER,
        screen_time_minutes INTEGER,
        productivity_score REAL
    )
    """)
    conn.commit()
    conn.close()

def insert_log(date: str,
               sleep_hours: float,
               study_hours: float,
               activities: str,
               timestamp: str,
               mood: Optional[str] = None,
               notes: Optional[str] = None,
               mode: str = "student",
               water_intake: Optional[float] = None,
               steps: Optional[int] = None,
               screen_time_minutes: Optional[int] = None,
               productivity_score: Optional[float] = None):
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO daily_logs
        (date, sleep_hours, study_hours, activities, mood, notes, mode, timestamp,
         water_intake, steps, screen_time_minutes, productivity_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (date, sleep_hours, study_hours, activities, mood, notes, mode, timestamp,
          water_intake, steps, screen_time_minutes, productivity_score))
    conn.commit()
    conn.close()

def update_log(log_id: int, **kwargs):
    if not kwargs:
        return
    keys = []
    vals = []
    for k, v in kwargs.items():
        keys.append(f"{k} = ?")
        vals.append(v)
    vals.append(log_id)
    sql = f"UPDATE daily_logs SET {', '.join(keys)} WHERE id = ?"
    conn = get_connection()
    c = conn.cursor()
    c.execute(sql, tuple(vals))
    conn.commit()
    conn.close()

def fetch_logs() -> List[Tuple]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs ORDER BY date ASC")
    rows = c.fetchall()
    conn.close()
    return rows

def fetch_log_by_id(log_id: int):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM daily_logs WHERE id = ?", (log_id,))
    row = c.fetchone()
    conn.close()
    return row

def export_csv(path: str = "habit_export.csv"):
    import csv
    rows = fetch_logs()
    headers = ["id", "date", "sleep_hours", "study_hours", "activities", "mood",
               "notes", "mode", "timestamp", "water_intake", "steps", "screen_time_minutes", "productivity_score"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow(r)
    return path
