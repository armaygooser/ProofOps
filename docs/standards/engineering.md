# Engineering conventions

- Code identifiers and public APIs use English.
- Internal documentation and explanatory comments may use Chinese.
- Configuration is declarative and validated at startup.
- External side effects require an explicit proposal, human approval, allowlist match and audit record.
- Evidence content hashes and the operation audit chain are separate concepts in code and UI.
- The deterministic demo must label `model_mode=deterministic` and `agentteams_task=false` until a native run is captured.
- Logs are structured JSON with `trace_id`, `span_id`, `event_type` and bounded payloads.
