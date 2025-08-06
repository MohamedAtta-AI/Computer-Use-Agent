from sqlmodel import SQLModel, Session, create_engine
from backend.core.config import get_settings

settings = get_settings()
engine = create_engine(settings.db_url, echo=settings.production)


def init_db():
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session