# ProofOps · 证控中枢

> 面向工业操作的可信智能体决策系统。七个 Agent 调查，人类批准，受控执行器落地，独立角色复测，所有操作由哈希记录并可回滚。

ProofOps 是独立于 CyberGuard 的演示产品，用 B2 冷却异常说明 CyberGuard 的治理基座可以迁移到工业运维。它复用了 CyberGuard 的治理契约和核心算法，同时用独立领域包约束工业动作，避免放宽原安全产品的动作白名单。

## 60 秒看懂

1. **七智能体调查**：信号融合、设备诊断、负荷预测、安全策略、动作规划、受控执行、独立复测，各自拥有最小权限。
2. **人类保留权力**：Agent 只能形成提案；L2 操作必须由值班总管批准，批准记录绑定精确提案 SHA-256，并设置 15 分钟有效期。
3. **可验证执行**：数字孪生执行 `BMS.START B2-CHILLER-02`，回执和状态摘要进入 HMAC 串联操作链。
4. **独立复测**：温度 ≤26°C、功率 ≤500kW、心跳 ≥99% 三项均满足才通过。
5. **可控回滚**：回滚绑定执行记录哈希；完成后旧复测结论自动失效。

## 一键启动

需要 Docker Desktop：

```powershell
docker compose up --build
```

浏览器打开 <http://127.0.0.1:18766>。点击 **一键演示至审批**，然后依次体验批准、执行、复测和回滚。

### 本地开发

```powershell
npm --prefix frontend install
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

终端 1：

```powershell
.\.venv\Scripts\python.exe -m uvicorn proofops_api.app:app --host 127.0.0.1 --port 18765
```

终端 2：

```powershell
npm --prefix frontend run dev -- --host 127.0.0.1
```

## 验证

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check backend
npm --prefix frontend test
npm --prefix frontend run build
```

## CyberGuard 复用边界

`backend/proofops_api/governance.py` 从 CyberGuard v0.14 的 `services/response-executor/app/main.py` 提取并领域化了以下规则：

- 规范 JSON 的 SHA-256 记录摘要；
- `previous_record_sha256` 串联与 HMAC-SHA256 鉴真；
- 提案、审批和执行之间的精确哈希绑定；
- 审批有效期、幂等执行与回滚关闭语义；
- 执行后独立复测，回滚后旧结论失效。

工业动作 `activate_backup_cooling` 位于 ProofOps 独立白名单中。CyberGuard 原有安全动作白名单没有被修改。详见 [CYBERGUARD_REUSE.md](docs/CYBERGUARD_REUSE.md)。

## AgentTeams / Element Web

ProofOps 随附七个 Worker 草案和三个权限隔离 Skill。部署控制台后，通过 AgentTeams Service Publishing 发布 18766 端口，在 Matrix 房间投递发布地址，即可从 Element Web 打开控制台。

操作步骤见 [ELEMENT_LAUNCH.md](agentteams/ELEMENT_LAUNCH.md)。当前确定性演示不会冒充真实 AgentTeams 模型运行。

## 目录

```text
frontend/       React + TypeScript + Ant Design 中控页面
backend/        FastAPI、CyberGuard 治理适配器和数字孪生
domainpack/     角色、动作白名单与复测契约
agentteams/     Worker、Skill 与 Element Web 打开方式
docs/           架构、复用说明、录屏脚本与报告
```

## 安全边界

默认模式只连接隔离数字孪生，不连接真实 PLC、BMS 或生产设备。生产接入需要设备协议适配、凭据隔离、部署审批与现场安全验证。

## License

Apache-2.0。详见 `LICENSE`。
