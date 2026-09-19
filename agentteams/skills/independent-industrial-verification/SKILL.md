---
name: independent-industrial-verification
description: 在执行后独立复测安全与业务指标，并在回滚后作废旧结论。
version: 0.1.0
---

# 独立工业复测

## 验证契约

- 区域温度 `<= 26°C`
- 园区功率 `<= 500kW`
- 设备心跳 `>= 99%`
- 三项必须来自执行后的独立观测，不能使用执行 Agent 的叙述。

只返回 `verified`、`failed` 或 `inconclusive`。输出 `checks[]`、`evidence_ids[]`、观测窗口和回滚建议。检测到回滚事件时，旧结论必须标记为 `invalidated`。
