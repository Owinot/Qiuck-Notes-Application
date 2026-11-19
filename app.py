"""Notes app backend: Flask + SQLite.

Run:  pip install -r requirements.txt && python app.py
Open: http://localhost:5000
"""
import sqlite3
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory

BASE = Path(__file__).parent
DB_PATH = BASE / "notes.db"

app = Flask(__name__, static_folder=str(BASE / "static"), static_url_path="/static")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as db:
        db.execute(
            """CREATE TABLE IF NOT EXISTS notes (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   title TEXT NOT NULL DEFAULT '',
                   body TEXT NOT NULL,
                   created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
               )"""
        )


@app.get("/")
def index():
    # Look for index.html in ./static first, then next to app.py
    for folder in (BASE / "static", BASE):
        if (folder / "index.html").exists():
            return send_from_directory(folder, "index.html")
    return (
        "index.html not found. Put it in a 'static' folder next to app.py "
        f"(looked in: {BASE / 'static'} and {BASE}).",
        404,
    )


@app.get("/api/notes")
def list_notes():
    with get_db() as db:
        rows = db.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    return jsonify([dict(r) for r in rows])


@app.post("/api/notes")
def create_note():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()[:120]
    body = (data.get("body") or "").strip()
    if not body:
        return jsonify(error="Note text can't be empty."), 400
    if len(body) > 10_000:
        return jsonify(error="Note is too long (10,000 characters max)."), 400
    with get_db() as db:
        cur = db.execute("INSERT INTO notes (title, body) VALUES (?, ?)", (title, body))
        row = db.execute("SELECT * FROM notes WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


@app.delete("/api/notes/<int:note_id>")
def delete_note(note_id):
    with get_db() as db:
        cur = db.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    if cur.rowcount == 0:
        return jsonify(error="Note not found."), 404
    return "", 204


init_db()

if __name__ == "__main__":
    app.run(debug=True)