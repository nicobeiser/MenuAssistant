from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from .db import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    ts = Column(DateTime, default=datetime.utcnow, index=True)

    # tipo de evento: "chat", "upload", "http_request", etc.
    type = Column(String, index=True)

    # endpoint (opcional)
    endpoint = Column(String, nullable=True)

    duration_ms = Column(Float, nullable=True)

    total_ms = Column(Float, nullable=True)
    model_ms = Column(Float, nullable=True)

    # metadata simple
    meta = Column(String, nullable=True)