# Validation History

| Date | Command/Check | Result | Notes |
| --- | --- | --- | --- |
| 2026-09-19 | `.venv\\Scripts\\python.exe -m pytest` | passed | 2 tests cover complete governed flow, rollback invalidation and exact proposal-hash binding. Two upstream Starlette/TestClient deprecation warnings only. |
| 2026-09-19 | `.venv\\Scripts\\python.exe -m ruff check backend scripts` | passed | Final check after automatic import formatting. |
| 2026-09-19 | `npm test` | passed | 2 Vitest assertions for SHA-256 display identity. |
| 2026-09-19 | `npm run build` | passed | TypeScript and Vite production build completed; only a non-blocking bundle-size advisory remains. |
| 2026-09-19 | Headless Edge at 1920×1080 | partially passed | `docs/reports/proofops-dashboard.png` only captured the loading transition page; the earlier "page loaded" claim never visually confirmed the rendered UI. |
| 2026-09-19 | GLM resume checks: `docker compose ps`, `curl /health`, `curl :18766/`, `curl :18766/api/demo` | passed | Both containers up (API healthy); web 200; nginx `/api` proxy 200; demo state is `phase=detected`, 0 audit events, 0/7 agents complete (initial incident state). |
| 2026-09-19 | Headless Edge `--virtual-time-budget=15000` at 1920×1080 | passed | `docs/reports/proofops-dashboard-live.png` (876KB) shows the fully rendered console: 5 panels, digital twin 31.8°C, evidence hashes, Chinese text intact, professional dark theme; only trivial cosmetic notes (panel bottom alignment, button edge spacing). Closes the blocked visual inspection. |
| 2026-09-19 | `docker compose build` | passed | Both API and web images built successfully. |
| 2026-09-19 | `docker compose up -d` / `docker compose ps` | passed | API is healthy and web container is running on port 18766. |
| 2026-09-19 | `.venv\\Scripts\\python.exe scripts\\smoke_http.py` | passed | Published web endpoint completed investigate → propose → approve → execute → verify → rollback; final audit valid and verification invalidated. |

## Validation Caveats

- AgentTeams resources are reviewable drafts based on existing CyberGuard v1beta1 Worker syntax; they were not applied to a live Controller in this session.
- Service Publishing requires the actual deployment's generated URL.
