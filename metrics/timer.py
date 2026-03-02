import time
from contextlib import contextmanager

@contextmanager
def span():
    t0 = time.perf_counter()
    data = {}
    try:
        yield data
        data["ok"] = True
    except Exception as e:
        data["ok"] = False
        data["error"] = repr(e)
        raise
    finally:
        data["ms"] = (time.perf_counter() - t0) * 1000