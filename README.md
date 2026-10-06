![Student Companion API](https://raw.githubusercontent.com/omgsh/student-companion-api/main/student-companion-api-social.png)

# Student Companion API

A small REST API for saving study notes and looking them up by subject, built with FastAPI, SQLModel and Postgres (hosted on Supabase). It also serves a simple notes page at `/`.

## Features
- Save, list, view and delete study notes
- Filter notes by subject with `?subject=`
- Newest notes first
- Clear 404 errors when a note doesn't exist
- Auto-generated interactive docs at `/docs`

## Endpoints
| Method | Path | What it does |
|---|---|---|
| `POST` | `/notes` | Save a note (title, body, subject) |
| `GET` | `/notes` | List notes, optionally filtered by `?subject=` |
| `GET` | `/notes/{id}` | Get one note (404 if not found) |
| `DELETE` | `/notes/{id}` | Delete a note (404 if not found) |
| `GET` | `/` | Simple notes page |

## Tech
Python · FastAPI · SQLModel (SQLAlchemy + Pydantic) · Postgres on Supabase · Uvicorn

## Run it locally
```bash
git clone https://github.com/omgsh/student-companion-api.git
cd student-companion-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```
Create a `.env` file with your Postgres connection string:
```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres
```
Then start the server:
```bash
uvicorn main:app --reload
```
Open http://localhost:8000 for the notes page or http://localhost:8000/docs to try the API.

## How it works
- `Note` is a SQLModel class that doubles as the database table and the response shape.
- `NoteCreate` limits what the client can send, so the server sets `id` and `created_at`.
- Each request gets its own database session through FastAPI's dependency injection.
- Tables are created automatically when the app starts.

## Roadmap
- [ ] Tests with pytest
- [ ] Docker + GitHub Actions CI
- [ ] `/ask` endpoint to search notes by meaning (pgvector)

---
Built by [Anthony Rossi](https://www.linkedin.com/in/anthonyrossi01) · [Fierce Builds](https://www.fiercebuilds.com/portfolio)
