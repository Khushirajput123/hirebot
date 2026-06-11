import sqlite3
import pandas as pd
from datetime import datetime
import os


def init_db():
    """
    Creates database file and table if they don't exist.
    Run this once when app starts.
    """

    # Create data folder if not exists
    os.makedirs("data", exist_ok=True)

    conn = sqlite3.connect("data/results.db")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_name TEXT,
            match_score INTEGER,
            match_level TEXT,
            matched_skills TEXT,
            missing_skills TEXT,
            strengths   TEXT,
            weaknesses  TEXT,
            suggestions TEXT,
            summary     TEXT,
            timestamp   TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database ready")


def save_result(resume_name, result):
    """
    Saves one analysis result to database.

    INPUT:  resume_name (string), result (dict from scorer.py)
    """

    conn = sqlite3.connect("data/results.db")

    conn.execute("""
        INSERT INTO analyses 
        (resume_name, match_score, match_level, matched_skills,
         missing_skills, strengths, weaknesses, suggestions, 
         summary, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resume_name,
        result.get("match_score", 0),
        result.get("match_level", ""),
        # Convert lists to strings for storage
        ", ".join(result.get("matched_skills", [])),
        ", ".join(result.get("missing_skills", [])),
        ", ".join(result.get("strengths", [])),
        ", ".join(result.get("weaknesses", [])),
        ", ".join(result.get("suggestions", [])),
        result.get("overall_summary", ""),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_history():
    """
    Returns all past analyses as pandas DataFrame
    """
    conn = sqlite3.connect("data/results.db")

    try:
        df = pd.read_sql(
            "SELECT * FROM analyses ORDER BY timestamp DESC",
            conn
        )
    except:
        df = pd.DataFrame()  # empty if no data yet

    conn.close()
    return df