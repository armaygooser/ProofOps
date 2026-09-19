from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    host: str = os.getenv("PROOFOPS_API_HOST", "127.0.0.1")
    port: int = int(os.getenv("PROOFOPS_API_PORT", "18765"))
    demo_mode: str = os.getenv("PROOFOPS_DEMO_MODE", "deterministic")


settings = Settings()
