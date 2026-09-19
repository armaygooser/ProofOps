---
name: industrial-observation
description: 以只读权限调查工业遥测、设备状态和安全边界，输出可解析证据引用。
version: 0.1.0
---

# 工业只读调查

## 安全边界

- 只读取本次 `run_id` 的遥测、设备清单、历史负荷与策略。
- 不调用执行端点，不生成审批，不把其他 Agent 的叙述当成设备事实。
- 工具未返回 Evidence ID 时只能输出 `PARTIAL` 或 `BLOCKED`。

## 输出

返回 `status`、`finding`、`evidence_ids[]`、`counter_evidence[]`、`unknowns[]` 与 `recommended_next_read`。
