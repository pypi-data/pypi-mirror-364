from .db import DB_PATH
from .utils import load_model as _load_model
import sqlite3

def load_model(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT path FROM models WHERE name=?", (name,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise ValueError(f"No model found with name '{name}'")
    return _load_model(row[0])