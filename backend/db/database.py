from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.engine import Engine
from sqlalchemy import event

# if PRODUCTION:
#     db_url = os.getenv("DATABASE_URL")
# else:
#     db_file_name = "database.db"
#     db_url = f"sqlite:///{db_file_name}"

db_url = "sqlite:///database.db"

connect_args = {"check_same_thread": False}
engine = create_engine(db_url, echo=True, connect_args=connect_args)

# Enable foreign keys in SQLite
@event.listens_for(Engine, "connect")
def on_connect(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")
    cursor.close()


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session