from __future__ import annotations

from pydantic import BaseModel, Field


class ApprovalCommand(BaseModel):
    approver: str = Field(min_length=2, max_length=64)
    proposal_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    acknowledged: bool


class RollbackCommand(BaseModel):
    approver: str = Field(min_length=2, max_length=64)
    execution_hash: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmed: bool
