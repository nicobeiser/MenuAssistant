from metrics.timer import span
from fastapi.concurrency import run_in_threadpool
from metrics.service import track_event
from first import recieve_prompt 

async def handle_chat(message: str) -> dict:
    with span() as total:
        result = await run_in_threadpool(recieve_prompt, message)

    total_ms = float(total["ms"])

    if isinstance(result, dict) and "text" in result and "metrics" in result:
        m = result["metrics"] or {}
        model_ms = m.get("model_latency_ms")

        await track_event(
            type="chat",
            total_ms=total_ms,
            model_ms=float(model_ms) if model_ms else None,
            meta=(
                f"ok={m.get('ok')};"
                f"images={m.get('images_count')};"
                f"prompt_chars={m.get('prompt_chars')}"
            ),
        )
        return {"reply": result["text"]}

    await track_event(type="chat", total_ms=total_ms, model_ms=None, meta="fallback=true")
    return {"reply": str(result)}