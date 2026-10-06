import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select

# Load DATABASE_URL (and any other vars) from the local .env file.
load_dotenv()

database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise RuntimeError("DATABASE_URL is not set. Add it to .env.")

# One engine shared by every request. echo=False keeps SQL out of the logs.
engine = create_engine(database_url)


class Note(SQLModel, table=True):
    """A study note stored in Postgres."""

    id: int | None = Field(default=None, primary_key=True)
    title: str
    body: str
    subject: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class NoteCreate(SQLModel):
    """Fields the client sends when creating a note. id and created_at are set by the server."""

    title: str = Field(
        description="Short name for the note",
        schema_extra={"examples": ["Photosynthesis"]},
    )
    body: str = Field(
        description="The note itself",
        schema_extra={"examples": ["Plants turn sunlight into energy."]},
    )
    subject: str = Field(
        description="Class or topic. Use the same spelling when you filter the list.",
        schema_extra={"examples": ["Biology"]},
    )


def get_session():
    """Open a DB session for one request, then close it."""
    with Session(engine) as session:
        yield session


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create missing tables when the app starts. Safe to run more than once.
    SQLModel.metadata.create_all(engine)
    yield


app = FastAPI(
    title="Student Companion",
    description="Save study notes and look them up by subject. The notes page is at /.",
    lifespan=lifespan,
)


@app.get("/", include_in_schema=False)
def home():
    # The notes page: a form and a list, instead of the raw API docs.
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.post("/notes", response_model=Note, summary="Save a note")
def create_note(payload: NoteCreate, session: Session = Depends(get_session)):
    note = Note.model_validate(payload)
    session.add(note)
    session.commit()
    session.refresh(note)  # load the generated id and created_at
    return note


@app.get("/notes", response_model=list[Note], summary="List notes")
def list_notes(
    subject: str | None = Query(
        default=None,
        description="Only return notes for this subject. Leave it blank to see every note.",
        examples=["Biology"],
    ),
    session: Session = Depends(get_session),
):
    # Optional ?subject= filter. Omit it to return every note, newest first.
    statement = select(Note).order_by(Note.created_at.desc())
    if subject is not None:
        statement = statement.where(Note.subject == subject)
    return session.exec(statement).all()


@app.get("/notes/{note_id}", response_model=Note, summary="Get one note")
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@app.delete("/notes/{note_id}", summary="Delete a note")
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    session.delete(note)
    session.commit()
    return {"ok": True}
