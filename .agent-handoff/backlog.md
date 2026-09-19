# Task Backlog

## User Review

- [ ] Review the running control-room UI and request any visual changes.

## CyberGuard Runtime Reuse

- [ ] Extract a versioned `cyberguard-governance` Python package from CyberGuard.
- [ ] Refactor the CyberGuard response executor to consume the shared package without weakening its tests or allowlist.
- [ ] Pin ProofOps to a CyberGuard tag or commit and replace the local contract adaptation with the shared package where appropriate.

## Final Deployment Follow-ups

- [ ] Apply `agentteams/workers.yaml` and package the three Skills on the actual AgentTeams Controller.
- [ ] Publish port 18766, replace `PROOFOPS_PUBLISHED_URL`, and capture the Element Web launch recording.
- [ ] Capture Worker and tool receipts before labeling any screen a live AgentTeams model run.

## GitHub Publication

- [x] Publish the independent repository at `https://github.com/armaygooser/ProofOps`.
- [x] Add a GitHub-facing README that explains the CyberGuard migration, quick start and verified demo boundary.

## Optional Production Work

- [ ] Persist the HMAC audit ledger in immutable storage across process restarts.
- [ ] Add a versioned remote CyberGuard generic action-provider interface.
- [ ] Replace the digital twin adapter with an approved BMS/PLC connector only after site safety review.
