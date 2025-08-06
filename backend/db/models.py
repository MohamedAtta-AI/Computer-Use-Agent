from sqlmodel import SQLModel, Field, Session, create_engine




def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()


class SessionBase(SQLModel):
    __tablename__ = "sessions"
    id = Column(UUID, primary_key=True, default=uuid4)
    title = Column(String(255))
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(UUID, primary_key=True, default=uuid4)
    session_id = Column(UUID, ForeignKey("sessions.id"))
    role = Column(String(16))  # user, assistant, system
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)