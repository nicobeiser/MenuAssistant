from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime, timezone

from db.database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)

    status = Column(String(32), nullable=False, default="pending_payment")

    # Guardamos items como JSON para MVP (después lo normalizás si querés)
    items = Column(JSON, nullable=False)

    amount = Column(Float, nullable=False)

    table_id = Column(String(64), nullable=True)

    # Para MP
    external_reference = Column(String(128), nullable=True, index=True)
    mp_preference_id = Column(String(128), nullable=True, index=True)

    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))