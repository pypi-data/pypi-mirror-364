import sqlite3
import os
from pathlib import Path
from tabulate import tabulate

DB_PATH = Path(os.getcwd()) / ".modelstack.sqlite"


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            path TEXT NOT NULL,
            framework TEXT,
            accuracy REAL,
            registered_on TEXT
        )
    ''')
    conn.commit()
    conn.close()


def register_model(name, path, framework, accuracy, timestamp):
    from pathlib import Path

    ext = Path(path).suffix.lower()

    # Supported extensions
    supported_exts = {".pkl", ".joblib", ".h5", ".pt"}

    if ext == "":
        print(f"Warning: The file '{path}' has no extension.")
        confirm = input("Do you want to register it anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("Registration cancelled.")
            return
    elif ext not in supported_exts:
        print(f"Warning: Extension '{ext}' is not officially supported.")
        confirm = input("Continue anyway? (y/N): ").strip().lower()
        if confirm != "y":
            print("Registration cancelled.")
            return

    # Connect to DB
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Check for duplicate model name
    cursor.execute("SELECT * FROM models WHERE name = ?", (name,))
    existing = cursor.fetchone()
    if existing:
        confirm = input(f"A model named '{name}' already exists. Overwrite? (y/N): ").strip().lower()
        if confirm != "y":
            print("Registration cancelled.")
            conn.close()
            return
        # Overwrite
        cursor.execute("DELETE FROM models WHERE name = ?", (name,))

    # Insert or update
    cursor.execute('''
        INSERT INTO models (name, path, framework, accuracy, registered_on)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, path, framework, accuracy, timestamp))

    conn.commit()
    conn.close()
    print(f"Model '{name}' registered successfully.")



def list_models():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name, framework, accuracy, path, registered_on FROM models")
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print("No models registered yet.")
        return
    print(tabulate(rows, headers=["Name", "Framework", "Accuracy", "Path", "Registered On"]))


def delete_model(name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the model exists
    cursor.execute("SELECT 1 FROM models WHERE name=?", (name,))
    if cursor.fetchone() is None:
        print(f"No model named '{name}' found in registry.")
    else:
        cursor.execute("DELETE FROM models WHERE name=?", (name,))
        conn.commit()
        print(f"Model '{name}' deleted from registry.")
    
    conn.close()

def delete_all_models():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM models")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("No models to delete from registry.")
    else:
        cursor.execute("DELETE FROM models")
        conn.commit()
        print("All models deleted from registry.")
    
    conn.close()