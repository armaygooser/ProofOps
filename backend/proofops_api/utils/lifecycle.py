from __future__ import annotations

import time
from collections.abc import Iterator
from contextlib import contextmanager

from .logger import log_event


@contextmanager
def lifecycle(*, trace_id: str, span_id: str) -> Iterator[None]:
    started = time.perf_counter()
    log_event(trace_id=trace_id, span_id=span_id, event_type="Function_Start", payload={})
    try:
        yield
    except Exception as exc:
        log_event(trace_id=trace_id, span_id=span_id, event_type="Error", payload={"type": type(exc).__name__})
        raise
    finally:
        log_event(
            trace_id=trace_id,
            span_id=span_id,
            event_type="Function_End",
            payload={"duration_ms": round((time.perf_counter() - started) * 1000, 3)},
        )
