from indexer.scanner import build_index_sqlite
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR / "database" / "file_index.db"
ROOT_TO_INDEX = "/home/vamsi"  # or "/" for full disk

# Build index if DB doesn't exist or is empty
import sqlite3
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
try:
    cursor.execute("SELECT 1 FROM files LIMIT 1")
except sqlite3.OperationalError:
    # Table does not exist, build index
    print("[i] SQLite index missing, building now...")
    build_index_sqlite(ROOT_TO_INDEX, str(DB_PATH))
finally:
    conn.close()

