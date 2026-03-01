from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from .db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    # tipo de evento: "chat", "upload", "delete_image"
    type = Column(String, index=True)

    # endpoint
    endpoint = Column(String, nullable=True)

    # duración (ms)
    duration_ms = Column(Float, nullable=True)

    # metadata simple (ej: filename, count uploads)
    meta = Column(String, nullable=True)