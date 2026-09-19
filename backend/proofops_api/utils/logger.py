from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("proofops")


def configure_logging() -> None:
    if logger.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def log_event(*, trace_id: str, span_id: str, event_type: str, payload: dict[str, Any]) -> None:
    logger.info(json.dumps({
        "timestamp": datetime.now(UTC).isoformat(),
        "trace_id": trace_id,
        "span_id": span_id,
        "event_type": event_type,
        "payload": payload,
    }, ensure_ascii=False, separators=(",", ":")))
