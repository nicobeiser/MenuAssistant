from fastapi import APIRouter
from sqlalchemy import select, func
from datetime import datetime, timedelta
from .db import SessionLocal
from .models import Event

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/daily")
async def daily_counts():
    async with SessionLocal() as session:
        q = select(
            func.date(Event.ts).label("day"),
            Event.type,
            func.count().label("count"),
        ).group_by(func.date(Event.ts), Event.type).order_by(func.date(Event.ts))
        rows = (await session.execute(q)).all()
    return [{"day": str(r.day), "type": r.type, "count": r.count} for r in rows]


@router.get("/summary")
async def summary(days: int = 7):
    since = datetime.utcnow() - timedelta(days=days)

    async with SessionLocal() as session:
        q_chats = select(func.count()).where(Event.type == "chat", Event.ts >= since)
        total_chats = (await session.execute(q_chats)).scalar_one()

        q_uploads = select(func.count()).where(Event.type == "upload", Event.ts >= since)
        total_uploads = (await session.execute(q_uploads)).scalar_one()

        q_avg = select(func.avg(Event.duration_ms)).where(
            Event.type == "chat",
            Event.ts >= since,
            Event.duration_ms.isnot(None),
        )
        avg_latency_ms = (await session.execute(q_avg)).scalar_one()
        avg_latency_ms = float(avg_latency_ms) if avg_latency_ms is not None else 0.0

        q_chat_fail = select(func.count()).where(
            Event.type == "chat",
            Event.ts >= since,
            Event.meta.isnot(None),
            Event.meta.like("%ok=False%"),
        )
        chat_fail = (await session.execute(q_chat_fail)).scalar_one()

    return {
        "days": days,
        "since_utc": since.isoformat(),
        "total_chats": int(total_chats),
        "total_uploads": int(total_uploads),
        "avg_latency_ms": avg_latency_ms,
        "errors": int(chat_fail),
    }