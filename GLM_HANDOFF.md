# ProofOps 交接给 GLM

## 当前状态

ProofOps · 证控中枢已经达到可演示状态。项目位于 `D:\Projects\ProofOps`，Git 分支为 `main`。Docker Compose 当前正在运行：

- 控制台：`http://127.0.0.1:18766`
- API：`http://127.0.0.1:18765`

## 已完成

- React + TypeScript + Vite + Ant Design 企业中控页面。
- 七个权限隔离 Agent 的确定性调查流程。
- CyberGuard v0.14 治理契约适配：SHA-256 证据摘要、HMAC 串联审计、提案审批绑定、有效期、受控执行、独立复测与回滚。
- B2 冷却异常数字孪生与 `activate_backup_cooling` 独立允许列表。
- AgentTeams Worker 草案、三个 Skill、Element Web 房间链接启动说明。
- Pytest、Ruff、Vitest、前端构建、Docker 镜像构建和容器 HTTP 冒烟测试。
- 55 秒录屏脚本：`docs/DEMO_RUNBOOK.md`。

## 恢复顺序

1. 阅读 `AGENT_HANDOFF.md`。
2. 阅读 `.agent-handoff/snapshot.md`、`risks.md`、`backlog.md`、`validation.md`。
3. 阅读 `docs/CYBERGUARD_REUSE.md` 和 `agentteams/ELEMENT_LAUNCH.md`。
4. 运行 `git status`，不要覆盖用户在 UI 上提出的新修改。

## 如果用户要改 UI

主要文件：

- `frontend/src/App.tsx`
- `frontend/src/styles/global.css`

保留以下产品规则：Agent 只调查和提案；人类批准；证据摘要与操作审计链分开展示；回滚后旧复测必须失效；始终标注隔离数字孪生。

## 如果用户要上 AgentTeams

当前仓库只提供可审核 Worker/Skill 资源和打开方式，没有冒充已部署 live run。使用实际 AgentTeams Controller 验证 `agentteams/workers.yaml` 字段，上传 Skill 包，通过 Service Publishing 发布 18766 端口，再把生成 URL 写入 `agentteams/room-message.md`。保留部署回执后才能把页面标注为 live run。

## 已知限制

- 当前 Agent 调查是确定性编排，不是实时模型调用。
- 工业设备是数字孪生，没有接入真实 PLC/BMS。
- HMAC 审计在进程内存中，容器重启或点击重置会创建新链；比赛演示足够，生产版应写入持久化不可变存储。
- Ant Design 单包约 667KB，Vite 有 chunk size 提示，但不影响本地演示。

## 常用验证

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend
npm --prefix frontend test
npm --prefix frontend run build
docker compose build
.\.venv\Scripts\python.exe scripts\smoke_http.py
```
