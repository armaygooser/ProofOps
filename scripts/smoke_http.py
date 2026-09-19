"""Run the complete ProofOps workflow through the published web endpoint."""

from __future__ import annotations

import json
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:18766"


def call(path: str, payload: dict | None = None) -> dict:
    body = json.dumps(payload).encode() if payload is not None else b""
    request = Request(
        BASE + path,
        data=body if path != "/health" else None,
        headers={"Content-Type": "application/json"},
        method="POST" if path != "/health" else "GET",
    )
    with urlopen(request, timeout=5) as response:
        return json.load(response)


assert call("/health")["status"] == "ok"
state = call("/api/demo/reset")
for _ in range(7):
    state = call("/api/demo/investigate/advance")
state = call("/api/demo/propose")
state = call("/api/demo/approve", {
    "approver": "smoke-test", "proposal_hash": state["proposal"]["record_sha256"], "acknowledged": True,
})
state = call("/api/demo/execute")
execution_hash = state["execution"]["record_sha256"]
state = call("/api/demo/verify")
assert state["verification"]["status"] == "passed"
state = call("/api/demo/rollback", {
    "approver": "smoke-test", "execution_hash": execution_hash, "confirmed": True,
})
assert state["verification"]["status"] == "invalidated"
assert state["audit"]["valid"] is True
print(json.dumps({
    "phase": state["phase"], "audit_records": state["audit"]["records"],
    "audit_valid": state["audit"]["valid"], "verification": state["verification"]["status"],
}, ensure_ascii=False))
