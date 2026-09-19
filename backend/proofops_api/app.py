from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .engine import engine
from .governance import GovernanceError
from .models import ApprovalCommand, RollbackCommand
from .utils.lifecycle import lifecycle
from .utils.logger import configure_logging


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    with lifecycle(trace_id=str(uuid4()), span_id="application.startup"):
        yield


app = FastAPI(
    title="ProofOps API",
    version="0.1.0",
    description="Industrial domain adapter powered by CyberGuard governance primitives.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:18766", "http://localhost:18766"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Approval-Secret"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "proofops-api", "demo_mode": settings.demo_mode,
            "governance_core": "cyberguard-contract-v0.14"}


@app.get("/api/meta")
def meta() -> dict[str, object]:
    return {"product": "ProofOps", "display_name": "证控中枢", "scenario": "B2 冷却异常处置",
            "agentteams_task": False, "model_mode": settings.demo_mode,
            "safety_boundary": "isolated_digital_twin"}


@app.get("/api/demo")
def demo_state() -> dict:
    return engine.snapshot()


@app.post("/api/demo/reset")
def reset_demo() -> dict:
    return engine.reset()


@app.post("/api/demo/investigate/advance")
def advance_investigation() -> dict:
    try:
        return engine.advance_investigation()
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@app.post("/api/demo/propose")
def create_proposal() -> dict:
    try:
        return engine.propose()
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@app.post("/api/demo/approve")
def approve_proposal(command: ApprovalCommand) -> dict:
    try:
        return engine.approve(command.approver, command.proposal_hash, command.acknowledged)
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@app.post("/api/demo/execute")
def execute_action() -> dict:
    try:
        return engine.execute()
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@app.post("/api/demo/verify")
def verify_action() -> dict:
    try:
        return engine.verify()
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None


@app.post("/api/demo/rollback")
def rollback_action(command: RollbackCommand) -> dict:
    try:
        return engine.rollback(command.approver, command.execution_hash, command.confirmed)
    except GovernanceError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from None
