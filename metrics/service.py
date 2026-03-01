from .db import SessionLocal
from .models import Event

async def track_event(
    type: str,
    endpoint: str | None = None,
    duration_ms: float | None = None,
    meta: str | None = None,
):
    async with SessionLocal() as session:
        session.add(Event(
            type=type,
            endpoint=endpoint,
            duration_ms=duration_ms,
            meta=meta,
        ))
        await session.commit()