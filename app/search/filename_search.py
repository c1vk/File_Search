import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "file_index.db"

def search_files(query: str, limit=50):
    """
    Search files by name directly from SQLite.
    Returns a list of full paths.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT path FROM files WHERE name LIKE ? LIMIT ?",
        (f"%{query}%", limit)
    )
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    return results

