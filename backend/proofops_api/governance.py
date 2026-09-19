"""CyberGuard governance contract adapted for an industrial domain pack.

The canonical record hashing, HMAC authentication, previous-record linking,
proposal/approval binding and rollback closure follow the implementation in
CyberGuard ``services/response-executor/app/main.py``. The domain action
allowlist remains local so the security product's allowlist is never weakened.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from copy import deepcopy
from datetime import UTC, datetime, timedelta


def canonical(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)


def sha256(payload: dict) -> str:
    return hashlib.sha256(canonical(payload).encode()).hexdigest()


class GovernanceError(ValueError):
    pass


class CyberGuardGovernanceKernel:
    def __init__(self, audit_key: str) -> None:
        if len(audit_key) < 32:
            raise ValueError("audit key must contain at least 32 characters")
        self._audit_key = audit_key.encode()
        self._events: list[dict] = []

    @property
    def events(self) -> list[dict]:
        return deepcopy(self._events)

    def append(self, event: dict, *, recorded_at: str | None = None) -> dict:
        record = deepcopy(event)
        record["recorded_at"] = recorded_at or datetime.now(UTC).isoformat()
        record["previous_record_sha256"] = self._events[-1]["record_sha256"] if self._events else None
        record["record_sha256"] = sha256(record)
        authenticated = canonical(record)
        record["record_hmac_sha256"] = hmac.new(
            self._audit_key, authenticated.encode(), hashlib.sha256
        ).hexdigest()
        self._events.append(record)
        return deepcopy(record)

    def verify(self) -> dict:
        previous_hash = None
        for index, persisted in enumerate(self._events):
            record = deepcopy(persisted)
            claimed_hmac = record.pop("record_hmac_sha256", None)
            claimed_hash = record.pop("record_sha256", None)
            if record.get("previous_record_sha256") != previous_hash:
                return {"valid": False, "failed_record": index, "reason": "broken_previous_hash"}
            calculated_hash = sha256(record)
            if not isinstance(claimed_hash, str) or not hmac.compare_digest(claimed_hash, calculated_hash):
                return {"valid": False, "failed_record": index, "reason": "record_hash_mismatch"}
            record["record_sha256"] = claimed_hash
            calculated_hmac = hmac.new(
                self._audit_key, canonical(record).encode(), hashlib.sha256
            ).hexdigest()
            if not isinstance(claimed_hmac, str) or not hmac.compare_digest(claimed_hmac, calculated_hmac):
                return {"valid": False, "failed_record": index, "reason": "record_hmac_mismatch"}
            previous_hash = claimed_hash
        return {
            "valid": True,
            "authenticated": True,
            "algorithm": "HMAC-SHA256",
            "records": len(self._events),
            "head": previous_hash,
        }

    def propose(self, payload: dict) -> dict:
        if payload.get("action") != "activate_backup_cooling" or payload.get("target") != "B2-CHILLER-02":
            raise GovernanceError("action is outside the industrial domain allowlist")
        return self.append({**payload, "risk": "L2", "reversible": True, "status": "pending_approval"})

    def approve(self, *, action_id: str, proposal_hash: str, approver: str, ttl_minutes: int = 15) -> dict:
        proposal = self._proposal(action_id)
        if proposal["record_sha256"] != proposal_hash:
            raise GovernanceError("approval is not bound to the current proposal")
        if any(event.get("action_id") == action_id and event.get("status") in {"executed", "rolled_back"}
               for event in self._events):
            raise GovernanceError("action is already closed")
        return self.append({
            "action_id": action_id,
            "incident_id": proposal["incident_id"],
            "run_id": proposal["run_id"],
            "proposal_record_sha256": proposal_hash,
            "approver": approver,
            "status": "approved",
            "approval_expires_at": (datetime.now(UTC) + timedelta(minutes=ttl_minutes)).isoformat(),
        })

    def authorize_execution(self, action_id: str) -> tuple[dict, dict]:
        proposal = self._proposal(action_id)
        approvals = [event for event in self._events
                     if event.get("action_id") == action_id and event.get("status") == "approved"]
        if not approvals:
            raise GovernanceError("human approval is required")
        approval = approvals[-1]
        if approval["proposal_record_sha256"] != proposal["record_sha256"]:
            raise GovernanceError("approval is not bound to this proposal")
        if datetime.fromisoformat(approval["approval_expires_at"]) < datetime.now(UTC):
            raise GovernanceError("approval expired")
        if any(event.get("action_id") == action_id and event.get("status") == "rolled_back"
               for event in self._events):
            raise GovernanceError("action is closed after rollback")
        return proposal, approval

    def execute(self, action_id: str, result: dict) -> dict:
        proposal, approval = self.authorize_execution(action_id)
        existing = next((event for event in reversed(self._events)
                         if event.get("action_id") == action_id and event.get("status") == "executed"), None)
        if existing:
            return deepcopy(existing)
        return self.append({
            "action_id": action_id,
            "incident_id": proposal["incident_id"],
            "run_id": proposal["run_id"],
            "action": proposal["action"],
            "target": proposal["target"],
            "approval_record_sha256": approval["record_sha256"],
            "status": "executed",
            "execution": "digital_twin",
            "result": result,
            "rollback_available": True,
        })

    def rollback(self, action_id: str, execution_hash: str, approver: str, result: dict) -> dict:
        proposal = self._proposal(action_id)
        executed = next((event for event in reversed(self._events)
                         if event.get("action_id") == action_id and event.get("status") == "executed"), None)
        if not executed:
            raise GovernanceError("action has not been executed")
        if executed["record_sha256"] != execution_hash:
            raise GovernanceError("rollback is not bound to the current execution")
        existing = next((event for event in reversed(self._events)
                         if event.get("action_id") == action_id and event.get("status") == "rolled_back"), None)
        if existing:
            return deepcopy(existing)
        return self.append({
            "action_id": action_id,
            "incident_id": proposal["incident_id"],
            "run_id": proposal["run_id"],
            "execution_record_sha256": execution_hash,
            "approver": approver,
            "status": "rolled_back",
            "result": result,
        })

    def _proposal(self, action_id: str) -> dict:
        proposal = next((event for event in self._events
                         if event.get("action_id") == action_id and event.get("status") == "pending_approval"), None)
        if not proposal:
            raise GovernanceError("proposal not found")
        return proposal
