# Validation History

| Date | Command/Check | Result | Notes |
| --- | --- | --- | --- |
| 2026-09-19 | `.venv\\Scripts\\python.exe -m pytest` | passed | 2 tests cover complete governed flow, rollback invalidation and exact proposal-hash binding. Two upstream Starlette/TestClient deprecation warnings only. |
| 2026-09-19 | `.venv\\Scripts\\python.exe -m ruff check backend scripts` | passed | Final check after automatic import formatting. |
| 2026-09-19 | `npm test` | passed | 2 Vitest assertions for SHA-256 display identity. |
| 2026-09-19 | `npm run build` | passed | TypeScript and Vite production build completed; only a non-blocking bundle-size advisory remains. |
| 2026-09-19 | Headless Edge at 1920×1080 | passed | Page loaded and generated `docs/reports/proofops-dashboard.png`. Codex screenshot inspection was blocked by a Windows sandbox helper failure. |
| 2026-09-19 | `docker compose build` | passed | Both API and web images built successfully. |
| 2026-09-19 | `docker compose up -d` / `docker compose ps` | passed | API is healthy and web container is running on port 18766. |
| 2026-09-19 | `.venv\\Scripts\\python.exe scripts\\smoke_http.py` | passed | Published web endpoint completed investigate → propose → approve → execute → verify → rollback; final audit valid and verification invalidated. |

## Validation Caveats

- AgentTeams resources are reviewable drafts based on existing CyberGuard v1beta1 Worker syntax; they were not applied to a live Controller in this session.
- Service Publishing requires the actual deployment's generated URL.
