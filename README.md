# Notes App

A single-page notes app. You write a note in the browser, it's sent to a Python (Flask) backend, stored in a SQLite database, and shown on the same page.

It's a small project for learning the request-response flow and basic data storage.

## Project structure

```
notes-app/
├── app.py             # Flask backend: routes + SQLite
├── requirements.txt   # Python dependencies
├── README.md
└── static/
    └── index.html     # The single page (HTML, CSS, JavaScript)
```

`notes.db` is created automatically the first time you run the app.

## Requirements

- Python 3.9 or newer
- pip

## Setup and run

```bash
# 1. (Optional) create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the server
python app.py
```

Open http://localhost:5000 in your browser.

To stop the server, press `Ctrl+C`.

## How it works

```
Browser (index.html)                Flask (app.py)               SQLite (notes.db)
        │                                │                               │
        │  GET /api/notes                │                               │
        │ ─────────────────────────────► │  SELECT * FROM notes          │
        │                                │ ────────────────────────────► │
        │ ◄───────────────────────────── │ ◄──────────────────────────── │
        │  200 [ {id, title, body, ...} ]│                               │
        │                                │                               │
        │  POST /api/notes {title, body} │                               │
        │ ─────────────────────────────► │  INSERT INTO notes ...        │
        │ ◄───────────────────────────── │ ────────────────────────────► │
        │  201 {saved note}              │                               │
```

1. **Page load:** the browser fetches `GET /api/notes` and renders the list.
2. **Save:** the form sends `POST /api/notes` with JSON. The server validates it, inserts a row, and returns the saved note. The page then reloads the list.
3. **Delete:** the Delete button sends `DELETE /api/notes/<id>`.

## API reference

| Method   | Endpoint           | Body                   | Success response       | Errors                                  |
|----------|--------------------|------------------------|------------------------|-----------------------------------------|
| `GET`    | `/api/notes`       | none                   | `200` list of notes    | none                                    |
| `POST`   | `/api/notes`       | `{ "title", "body" }`  | `201` the created note | `400` empty or too-long body            |
| `DELETE` | `/api/notes/<id>`  | none                   | `204` no content       | `404` note not found                    |

**Note object**

```json
{
  "id": 1,
  "title": "Shopping",
  "body": "Milk, eggs, bread",
  "created_at": "2026-11-19T09:41:58Z"
}
```

- `title` is optional and limited to 120 characters.
- `body` is required and limited to 10,000 characters.
- Notes are returned newest first.

**Try it from the command line**

```bash
# Create a note
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "body": "My first note"}'

# List notes
curl http://localhost:5000/api/notes

# Delete note 1
curl -X DELETE http://localhost:5000/api/notes/1
```

## Database

SQLite, in a single file (`notes.db`) next to `app.py`.

```sql
CREATE TABLE notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL DEFAULT '',
    body       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
);
```

To reset all data, stop the server and delete `notes.db`.

## Security notes

- SQL queries use `?` placeholders, so user input can't inject SQL.
- The page renders notes with `textContent`, so HTML or scripts typed into a note are shown as text and never run.
- `debug=True` is for local development only. Don't use it in production.

## Troubleshooting

**"The requested URL was not found on the server"**
- Make sure `index.html` is inside a `static` folder next to `app.py` (or directly next to `app.py`).
- Open `/` (http://localhost:5000/). Paths like `/index.html` return 404.

**Page doesn't load, or you see a different app on port 5000**
- Another program may be using the port (macOS AirPlay Receiver often does). Change the last line of `app.py` to `app.run(debug=True, port=5001)` and open http://localhost:5001.

**`ModuleNotFoundError: No module named 'flask'`**
- Run `pip install -r requirements.txt`, and make sure your virtual environment is activated.

## Ideas for next steps

- Edit notes (`PUT /api/notes/<id>`)
- Search and filter notes
- Tags or colors
- User accounts, so each person sees only their own notes
- Switch to SQLAlchemy, or to PostgreSQL for deployment
