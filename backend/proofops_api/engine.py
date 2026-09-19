from __future__ import annotations

import os
from copy import deepcopy
from datetime import UTC, datetime
from threading import RLock
from uuid import uuid4

from .governance import CyberGuardGovernanceKernel, GovernanceError, sha256

AGENT_BLUEPRINTS = [
    ("signal-fusion", "信号融合", "read:telemetry", "温度 31.8°C 与主冷机效率衰减同步出现，排除单传感器漂移。"),
    ("equipment-diagnosis", "设备诊断", "read:equipment", "CHILLER-01 换热效率下降 18%，建议启用备用机分担负载。"),
    ("load-forecast", "负荷预测", "read:history", "未来 15 分钟温度预计升至 34.2°C，风险窗口剩余 11 分钟。"),
    ("safety-policy", "安全策略", "read:policy", "备用机启用后预计 482kW，低于 B2 安全上限 500kW。"),
    ("action-planner", "动作规划", "propose:action", "形成最小可逆动作：启用 CHILLER-02，保持主机运行并观察 90 秒。"),
    ("controlled-operator", "受控执行", "execute:approved", "执行通道已锁定，等待人类批准与提案哈希绑定。"),
    ("independent-verifier", "独立复测", "read:post-state", "已登记独立复测契约：温度≤26°C、功率≤500kW、心跳≥99%。"),
]


class DemoEngine:
    def __init__(self) -> None:
        self._lock = RLock()
        self.reset()

    def reset(self) -> dict:
        with self._lock:
            self.run_id = f"RUN-{uuid4().hex[:8].upper()}"
            self.incident_id = "INC-B2-COOLING-017"
            key = os.getenv("PROOFOPS_AUDIT_HMAC_KEY", "proofops-demo-audit-key-change-before-production-2026")
            self.kernel = CyberGuardGovernanceKernel(key)
            self.phase = "detected"
            self.agent_cursor = 0
            self.action_id: str | None = None
            self.approver: str | None = None
            self.evidence: list[dict] = []
            self.verification = {"status": "not_started", "invalidated_by_rollback": False, "checks": []}
            self.twin = {
                "zone": "B2 数据机房", "temperature_c": 31.8, "power_kw": 436.0,
                "heartbeat_pct": 96.7, "primary_chiller": "degraded", "backup_chiller": "standby",
            }
            self.agents = [
                {"id": item[0], "name": item[1], "permission": item[2], "finding": item[3],
                 "status": "queued", "evidence_id": None}
                for item in AGENT_BLUEPRINTS
            ]
            self._add_evidence("alarm-snapshot", "告警快照", {
                "source": "B2-BMS", "temperature_c": 31.8, "power_kw": 436.0,
                "heartbeat_pct": 96.7, "classification": "internal",
            })
            return self.snapshot()

    def advance_investigation(self) -> dict:
        with self._lock:
            if self.phase not in {"detected", "investigating"}:
                raise GovernanceError("investigation is not available in the current phase")
            self.phase = "investigating"
            if self.agent_cursor >= len(self.agents):
                return self.snapshot()
            agent = self.agents[self.agent_cursor]
            agent["status"] = "complete"
            evidence = self._add_evidence(agent["id"], f"{agent['name']}结论", {
                "agent_id": agent["id"], "permission": agent["permission"], "finding": agent["finding"],
                "run_id": self.run_id,
            })
            agent["evidence_id"] = evidence["evidence_id"]
            self.agent_cursor += 1
            if self.agent_cursor < len(self.agents):
                self.agents[self.agent_cursor]["status"] = "working"
            else:
                self.phase = "ready_to_propose"
            return self.snapshot()

    def propose(self) -> dict:
        with self._lock:
            if self.phase != "ready_to_propose":
                raise GovernanceError("all seven agents must finish before proposal creation")
            self.action_id = f"ACT-{uuid4().hex[:10].upper()}"
            self.kernel.propose({
                "action_id": self.action_id,
                "incident_id": self.incident_id,
                "run_id": self.run_id,
                "action": "activate_backup_cooling",
                "target": "B2-CHILLER-02",
                "reason": "B2 温度持续升高且主冷机效率衰减；启用备用冷机是当前最小可逆动作。",
                "model_mode": "deterministic",
                "evidence_bundle_sha256": sha256({"evidence": [item["envelope_sha256"] for item in self.evidence]}),
                "verification_contract": {"temperature_c_lte": 26.0, "power_kw_lte": 500.0, "heartbeat_pct_gte": 99.0},
            })
            self.phase = "awaiting_approval"
            return self.snapshot()

    def approve(self, approver: str, proposal_hash: str, acknowledged: bool) -> dict:
        with self._lock:
            if self.phase != "awaiting_approval" or not self.action_id:
                raise GovernanceError("no proposal is awaiting approval")
            if not acknowledged:
                raise GovernanceError("risk acknowledgement is required")
            self.kernel.approve(action_id=self.action_id, proposal_hash=proposal_hash, approver=approver)
            self.approver = approver
            self.phase = "approved"
            return self.snapshot()

    def execute(self) -> dict:
        with self._lock:
            if self.phase != "approved" or not self.action_id:
                raise GovernanceError("an approved proposal is required")
            self.twin.update(temperature_c=25.6, power_kw=482.0, heartbeat_pct=99.6, backup_chiller="running")
            self.kernel.execute(self.action_id, {
                "command": "BMS.START", "target": "B2-CHILLER-02", "receipt": "accepted",
                "twin_state_sha256": sha256(self.twin),
            })
            self.phase = "executed"
            return self.snapshot()

    def verify(self) -> dict:
        with self._lock:
            if self.phase not in {"executed", "verified"}:
                raise GovernanceError("execution must complete before independent verification")
            checks = [
                {"label": "区域温度 ≤ 26°C", "value": self.twin["temperature_c"], "passed": self.twin["temperature_c"] <= 26.0},
                {"label": "总功率 ≤ 500kW", "value": self.twin["power_kw"], "passed": self.twin["power_kw"] <= 500.0},
                {"label": "设备心跳 ≥ 99%", "value": self.twin["heartbeat_pct"], "passed": self.twin["heartbeat_pct"] >= 99.0},
            ]
            evidence = self._add_evidence("independent-verification", "独立复测回执", {
                "verifier": "independent-verifier", "checks": checks,
                "twin_state": self.twin, "run_id": self.run_id,
            })
            self.verification = {
                "status": "passed" if all(item["passed"] for item in checks) else "failed",
                "invalidated_by_rollback": False,
                "checks": checks,
                "evidence_id": evidence["evidence_id"],
            }
            self.phase = "verified" if self.verification["status"] == "passed" else "verification_failed"
            return self.snapshot()

    def rollback(self, approver: str, execution_hash: str, confirmed: bool) -> dict:
        with self._lock:
            if self.phase not in {"executed", "verified", "verification_failed"} or not self.action_id:
                raise GovernanceError("there is no reversible execution")
            if not confirmed:
                raise GovernanceError("rollback confirmation is required")
            self.twin.update(temperature_c=28.9, power_kw=438.0, heartbeat_pct=98.4, backup_chiller="standby")
            self.kernel.rollback(self.action_id, execution_hash, approver, {
                "command": "BMS.STOP", "target": "B2-CHILLER-02", "receipt": "accepted",
                "twin_state_sha256": sha256(self.twin),
            })
            if self.verification["status"] != "not_started":
                self.verification["status"] = "invalidated"
                self.verification["invalidated_by_rollback"] = True
            self.phase = "rolled_back"
            return self.snapshot()

    def snapshot(self) -> dict:
        events = self.kernel.events
        proposal = next((item for item in events if item.get("status") == "pending_approval"), None)
        approval = next((item for item in reversed(events) if item.get("status") == "approved"), None)
        execution = next((item for item in reversed(events) if item.get("status") == "executed"), None)
        return {
            "product": "ProofOps", "display_name": "证控中枢", "run_id": self.run_id,
            "incident_id": self.incident_id, "phase": self.phase,
            "scenario": "B2 冷却异常处置", "safety_boundary": "isolated_digital_twin",
            "core": {"name": "CyberGuard governance contract", "version": "0.14", "mode": "embedded_domain_adapter"},
            "agents": deepcopy(self.agents), "twin": deepcopy(self.twin), "evidence": deepcopy(self.evidence),
            "proposal": proposal, "approval": approval, "execution": execution,
            "verification": deepcopy(self.verification), "audit": self.kernel.verify(), "audit_events": events,
            "approver": self.approver, "server_time": datetime.now(UTC).isoformat(),
        }

    def _add_evidence(self, source: str, title: str, content: dict) -> dict:
        captured_at = datetime.now(UTC).isoformat()
        content_sha = sha256(content)
        envelope = {"source": source, "title": title, "captured_at": captured_at, "content_sha256": content_sha}
        item = {
            "evidence_id": f"EVD-{uuid4().hex[:10].upper()}", "source": source, "title": title,
            "captured_at": captured_at, "content_sha256": content_sha,
            "envelope_sha256": sha256(envelope), "content": deepcopy(content),
        }
        self.evidence.append(item)
        return item


engine = DemoEngine()
