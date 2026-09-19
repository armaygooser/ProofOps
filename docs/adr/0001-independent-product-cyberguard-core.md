# ADR 0001: Independent ProofOps product over CyberGuard governance core

## Status

Accepted — 2026-09-19

## Decision

ProofOps is a sibling repository rather than a CyberGuard demo directory. It owns the industrial domain pack, UI and deterministic digital twin.

For the same-day demonstration, ProofOps embeds a narrow domain adapter extracted from the CyberGuard v0.14 governance contract. It preserves canonical hashing, HMAC-linked records, proposal-bound approval, expiry, execution guards and rollback closure. Industrial actions stay in a separate allowlist, so CyberGuard's security allowlist remains unchanged.

A later production connector may call deployed CyberGuard services through a versioned generic action-provider interface. This demo does not claim that remote connector exists.

## Consequences

- Product identity and release lifecycle are independent.
- Governance semantics and code provenance remain traceable to CyberGuard.
- The demo distinguishes deterministic Agent orchestration from a native live model run.
- The console opens from AgentTeams Element Web through a room link to a service-published URL.
