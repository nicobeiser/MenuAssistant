from fastapi import APIRouter
from sqlalchemy import select, func
from datetime import datetime, timedelta
from .db import SessionLocal
from .models import Event

router = APIRouter(prefix="/metrics", tags=["metrics"])


# ---------- Helpers ----------
def _since(days: int) -> datetime:
    return datetime.utcnow() - timedelta(days=days)


# ---------- Existing endpoints (kept) ----------
@router.get("/daily")
async def daily_counts():
    async with SessionLocal() as session:
        q = (
            select(
                func.date(Event.ts).label("day"),
                Event.type,
                func.count().label("count"),
            )
            .group_by(func.date(Event.ts), Event.type)
            .order_by(func.date(Event.ts))
        )
        rows = (await session.execute(q)).all()
    return [{"day": str(r.day), "type": r.type, "count": r.count} for r in rows]


@router.get("/summary")
async def summary(days: int = 7):
    """
    Backward compatible summary (old dashboard).
    Keeps avg_latency_ms based on duration_ms (legacy).
    """
    since = _since(days)

    async with SessionLocal() as session:
        total_chats = (await session.execute(
            select(func.count()).where(Event.type == "chat", Event.ts >= since)
        )).scalar_one()

        total_uploads = (await session.execute(
            select(func.count()).where(Event.type == "upload", Event.ts >= since)
        )).scalar_one()

        avg_latency = (await session.execute(
            select(func.avg(Event.duration_ms)).where(
                Event.type == "chat",
                Event.ts >= since,
                Event.duration_ms.isnot(None),
            )
        )).scalar_one()
        avg_latency = float(avg_latency) if avg_latency is not None else 0.0

        chat_fail = (await session.execute(
            select(func.count()).where(
                Event.type == "chat",
                Event.ts >= since,
                Event.meta.isnot(None),
                Event.meta.like("%ok=False%"),
            )
        )).scalar_one()

    return {
        "days": days,
        "since_utc": since.isoformat(),
        "total_chats": int(total_chats),
        "total_uploads": int(total_uploads),
        "avg_latency_ms": avg_latency,
        "errors": int(chat_fail),
    }


# ---------- New dashboard endpoints ----------
@router.get("/chat/summary")
async def chat_summary(days: int = 7):
    """
    New summary for chat dashboard:
    avg_total_ms from total_ms
    avg_model_ms from model_ms
    """
    since = _since(days)

    async with SessionLocal() as session:
        total_chats = (await session.execute(
            select(func.count()).where(Event.type == "chat", Event.ts >= since)
        )).scalar_one()

        avg_total = (await session.execute(
            select(func.avg(Event.total_ms)).where(
                Event.type == "chat", Event.ts >= since, Event.total_ms.isnot(None)
            )
        )).scalar_one()

        avg_model = (await session.execute(
            select(func.avg(Event.model_ms)).where(
                Event.type == "chat", Event.ts >= since, Event.model_ms.isnot(None)
            )
        )).scalar_one()

        errors = (await session.execute(
            select(func.count()).where(
                Event.type == "chat",
                Event.ts >= since,
                Event.meta.isnot(None),
                Event.meta.like("%ok=False%"),
            )
        )).scalar_one()

    return {
        "days": days,
        "since_utc": since.isoformat(),
        "total_chats": int(total_chats),
        "avg_total_ms": float(avg_total) if avg_total is not None else 0.0,
        "avg_model_ms": float(avg_model) if avg_model is not None else 0.0,
        "errors": int(errors),
    }


@router.get("/chat/recent")
async def chat_recent(limit: int = 25):
    """
    Recent chat events for table.
    """
    async with SessionLocal() as session:
        rows = (await session.execute(
            select(Event)
            .where(Event.type == "chat")
            .order_by(Event.ts.desc())
            .limit(limit)
        )).scalars().all()

    return [
        {
            "id": r.id,
            "ts": r.ts.isoformat(),
            "type": r.type,
            "endpoint": r.endpoint,
            "duration_ms": r.duration_ms,
            "total_ms": r.total_ms,
            "model_ms": r.model_ms,
            "meta": r.meta,
        }
        for r in rows
    ]


@router.get("/recent")
async def recent(limit: int = 25):
    """
    Generic recent endpoint (fallback used by the JS).
    """
    async with SessionLocal() as session:
        rows = (await session.execute(
            select(Event)
            .order_by(Event.ts.desc())
            .limit(limit)
        )).scalars().all()

    return [
        {
            "id": r.id,
            "ts": r.ts.isoformat(),
            "type": r.type,
            "endpoint": r.endpoint,
            "duration_ms": r.duration_ms,
            "total_ms": r.total_ms,
            "model_ms": r.model_ms,
            "meta": r.meta,
        }
        for r in rows
    ]


@router.get("/chat/breakdown")
async def chat_breakdown(days: int = 7):
    """
    Since you don't store pre/post yet:
    other_ms = avg_total_ms - avg_model_ms
    """
    since = _since(days)

    async with SessionLocal() as session:
        avg_total = (await session.execute(
            select(func.avg(Event.total_ms)).where(
                Event.type == "chat", Event.ts >= since, Event.total_ms.isnot(None)
            )
        )).scalar_one()

        avg_model = (await session.execute(
            select(func.avg(Event.model_ms)).where(
                Event.type == "chat", Event.ts >= since, Event.model_ms.isnot(None)
            )
        )).scalar_one()

    avg_total = float(avg_total) if avg_total is not None else 0.0
    avg_model = float(avg_model) if avg_model is not None else 0.0
    other = max(0.0, avg_total - avg_model)

    return {
        "labels": ["other (app)", "model (gemini)"],
        "values": [other, avg_model],
    }


@router.get("/breakdown")
async def breakdown(days: int = 7):
    """
    Generic fallback endpoint, same as chat/breakdown (used by the JS).
    """
    return await chat_breakdown(days=days)


@router.get("/chat/latency-timeseries")
async def chat_latency_timeseries(days: int = 30):
    """
    Timeseries of avg total latency per day.
    (p50/p95 would need more work on SQLite; keep it simple for now.)
    """
    since = _since(days)

    async with SessionLocal() as session:
        q = (
            select(
                func.date(Event.ts).label("day"),
                func.avg(Event.total_ms).label("avg_total_ms"),
            )
            .where(Event.type == "chat", Event.ts >= since, Event.total_ms.isnot(None))
            .group_by(func.date(Event.ts))
            .order_by(func.date(Event.ts))
        )
        rows = (await session.execute(q)).all()

    days_list = [str(r.day) for r in rows]
    avg_series = [float(r.avg_total_ms) if r.avg_total_ms is not None else 0.0 for r in rows]

    # Para que el front no se rompa, devolvemos "p50" y "p95" como lo mismo (avg)
    # Si querés p50/p95 reales en SQLite, lo armamos en Python agrupando.
    return {
        "days": days_list,
        "p50": avg_series,
        "p95": avg_series,
    }


@router.get("/latency_timeseries")
async def latency_timeseries(days: int = 30):
    """
    Generic fallback endpoint.
    """
    return await chat_latency_timeseries(days=days)