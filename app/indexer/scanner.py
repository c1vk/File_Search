import os
import sqlite3
from pathlib import Path

EXCLUDED_DIRS = {
    # Common version control / dev
    ".git",
    ".hg",
    ".svn",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".idea",
    ".vscode",

    # System / caches
    ".cache",
    "Cache",
    "Caches",
    "tmp",
    "Temp",
    "log",
    "logs",
    "Trash",
    ".mozilla",
    ".thumbnails",
    ".npm",                # npm cache
    ".pip",                # pip cache

    # Large runtime folders (optional)
    ".gradle",
    "build",
    "dist",
    ".tox",
    ".mypy_cache",
}


BATCH_SIZE = 100000  # commit every 1000 files to SQLite to avoid blocking

def scan_directory(root_path: str) -> list[dict]:
    """
    Recursively scan filesystem using os.scandir for speed.
    Returns a list of dicts with file metadata.
    """
    indexed_files = []

    def _scan(dir_path):
        try:
            with os.scandir(dir_path) as it:
                for entry in it:
                    # Skip excluded directories
                    if entry.is_dir(follow_symlinks=False) and entry.name in EXCLUDED_DIRS:
                        continue

                    # Skip broken/deleted files
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        continue

                    if entry.is_dir(follow_symlinks=False):
                        _scan(entry.path)  # recurse
                    elif entry.is_file(follow_symlinks=False):
                        indexed_files.append({
                            "name": entry.name,
                            "path": os.path.normpath(entry.path),
                            "ext": Path(entry.name).suffix.lower(),
                            "mtime": st.st_mtime
                        })
        except (PermissionError, FileNotFoundError):
            pass


    _scan(root_path)
    return indexed_files


def build_index_sqlite(root_path: str, db_path: str):
    """
    Build SQLite index directly while scanning.
    Safe for millions of files, avoids memory spikes.
    """
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # ---- Create table & indexes ----
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS files (
        id INTEGER PRIMARY KEY,
        path TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        ext TEXT,
        mtime REAL
    )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_name ON files(name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mtime ON files(mtime)")

    conn.execute("BEGIN TRANSACTION")
    file_count = 0  # progress counter

    def _scan(dir_path):
        nonlocal file_count
        try:
            with os.scandir(dir_path) as it:
                for entry in it:
                    # Skip excluded directories
                    if entry.is_dir(follow_symlinks=False) and entry.name in EXCLUDED_DIRS:
                        continue

                    # Skip broken/deleted files
                    try:
                        st = entry.stat(follow_symlinks=False)
                    except FileNotFoundError:
                        continue

                    if entry.is_dir(follow_symlinks=False):
                        _scan(entry.path)  # recurse
                    elif entry.is_file(follow_symlinks=False):
                        cursor.execute(
                            "INSERT OR REPLACE INTO files (path, name, ext, mtime) VALUES (?, ?, ?, ?)",
                            (entry.path, entry.name, Path(entry.name).suffix.lower(), st.st_mtime)
                        )
                        file_count += 1

                        # Commit in batches to avoid huge transactions
                        if file_count % BATCH_SIZE == 0:
                            conn.execute("COMMIT")
                            conn.execute("BEGIN TRANSACTION")
                            print(f"[i] Indexed {file_count} files so far...")

        except (PermissionError, FileNotFoundError):
            pass  # skip directories we can't access

    print(f"[i] Starting scan of {root_path} ...")
    _scan(root_path)
    conn.execute("COMMIT")
    conn.close()
    print(f"[✓] Finished indexing {file_count} files into {db_path}")