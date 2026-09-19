# CyberGuard 基座复用说明

## 复用对象

ProofOps 参考 CyberGuard v0.14（本地基线提交 `5893bd3`）的治理内核实现工业领域适配，来源是：

- `services/response-executor/app/main.py`
- `services/security-tool-gateway/app/store.py`
- `services/security-tool-gateway/app/run_view.py`
- `skills/controlled-response/SKILL.md`
- `skills/recovery-verification/SKILL.md`

上游仓库：<https://github.com/elsechord/CyberGuard>

核心执行器基线：<https://github.com/elsechord/CyberGuard/blob/5893bd3/services/response-executor/app/main.py>

这些实现形成领域无关的闭环：证据固定 → 动作提案 → 人工审批 → 受控执行 → 独立复测 → 回滚。

## ProofOps 中的对应关系

| CyberGuard 治理能力 | ProofOps 工业适配 |
|---|---|
| Evidence ID、内容 SHA 与封装 SHA | BMS 快照与七个 Agent 结论的独立摘要 |
| 安全动作允许列表 | `activate_backup_cooling / B2-CHILLER-02` 独立允许列表 |
| L2 人工审批 | 值班总管确认风险并绑定提案记录 SHA-256 |
| HMAC 串联动作审计 | 提案、批准、执行与回滚的 HMAC-SHA256 操作链 |
| 执行回执与幂等语义 | 数字孪生 `BMS.START/BMS.STOP` 回执 |
| 独立 recovery verifier | 温度、功率与心跳三项执行后独立观测阶段 |
| 回滚关闭动作 | 回滚绑定执行哈希并让旧复测结论失效 |

## 当前集成级别

当前是**本地契约适配**：ProofOps 没有运行时调用 CyberGuard API，也没有直接导入 CyberGuard Python 包。`backend/proofops_api/governance.py` 根据上述基线实现相同治理语义，但使用独立工业白名单与确定性数字孪生。

如需升级为“运行时复用 CyberGuard 基座”，下一步应在 CyberGuard 中提供版本化的通用动作提供者接口，由 ProofOps 通过正式 API 或共享包调用；不能把工业动作伪装为现有安全动作。

## 没有复用的部分

安全告警归一化、IOC、端点隔离、身份实验室和主机实验室仍属于 CyberGuard。ProofOps 没有用安全动作名称伪装工业动作，也没有扩大 CyberGuard 的默认允许列表。

## 演示真实性

- 哈希、HMAC、状态门、审批绑定与回滚由 FastAPI 后端实时计算。
- 设备状态、Agent 调查结论和执行回执来自确定性数字孪生。
- 人类审批人当前是输入字符串，没有生产身份鉴权。
- 独立复测是同一进程内的独立阶段，不是已部署的独立 AgentTeams Worker。
- 完整分层见 [`DEMO_TRUTH_BOUNDARY.md`](DEMO_TRUTH_BOUNDARY.md)。
