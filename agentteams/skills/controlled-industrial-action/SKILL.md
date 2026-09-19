---
name: controlled-industrial-action
description: 形成并执行绑定证据、审批和回滚句柄的工业白名单动作。
version: 0.1.0
---

# 受控工业操作

## 强制流程

1. 验证 `run_id`、Evidence ID 与动作白名单。
2. 固定 `action`、`target`、参数、证据包哈希和复测契约。
3. L2 提案暂停等待人类批准；Agent 不得获得审批密钥。
4. 执行前核对批准记录与提案 SHA-256 完全一致且未过期。
5. 只返回真实 Action ID、回执、审计哈希与回滚句柄。

任何不一致均输出 `BLOCKED`，不得替换相近目标。
