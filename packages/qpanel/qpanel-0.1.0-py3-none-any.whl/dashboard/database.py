# eops_dashboard/database.py
from sqlmodel import create_engine, SQLModel, Session

DATABASE_FILE = "eops_panel.db"
DATABASE_URL = f"sqlite:///{DATABASE_FILE}"

# The connect_args is needed for SQLite to work correctly with FastAPI's threading.
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Initializes the database and creates tables if they don't exist."""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session