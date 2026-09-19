# Risks, Blockers, And Unknowns

## Current Blockers

- None.

## Current Risks

- The deterministic Agent trace demonstrates orchestration and governance but is not a native live AgentTeams/model run.
- The digital twin is demonstration evidence, not proof of production PLC/BMS integration.
- The HMAC audit ledger is process-local and starts a new chain after reset or restart; production requires durable immutable storage.
- `agentteams/workers.yaml` follows the CyberGuard v1beta1 syntax but still requires schema validation against the final competition Controller.
- Element Web launch uses a Matrix room link to a Service Publishing URL; an embedded Matrix widget is not claimed.
- The Vite production bundle is about 667KB before gzip and reports a non-blocking chunk-size advisory.

- Public GitHub claims must say local CyberGuard contract adaptation; the current runtime does not call CyberGuard services or import a CyberGuard package.

## Unknowns / Confirmations Needed

- The final AgentTeams Service Publishing URL is deployment-specific.
- Final visual polish depends on user review of the running page; the automated visual pass found only trivial cosmetic notes (04/05 panel bottom alignment, rollback button edge spacing, heartbeat KPI not warning-colored at 96.7% vs ≥99% target).
