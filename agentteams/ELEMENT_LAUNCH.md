# 从 AgentTeams Element Web 打开 ProofOps

## 演示路径

1. 在演示机启动 ProofOps：`docker compose up --build`。
2. 确认控制台可通过 `http://<演示机>:18766` 访问。
3. 使用当前 AgentTeams 部署的 Service Publishing 功能发布 18766 端口，记录 Controller 返回的 HTTPS 地址。
4. 在 ProofOps Team 的 Matrix 房间发送 `agentteams/room-message.md` 中的消息，并把占位地址替换成实际发布地址。
5. 在 Element Web 房间中点击 **打开证控中枢**。控制台在浏览器标签页打开；回到房间可继续查看智能体调查、审批等待与结果消息。

## 事实边界

- Element Web 是 AgentTeams 的 Matrix 客户端；这里使用房间链接打开 Service Publishing 地址。
- 当前资料不声明 ProofOps 是 Element 内嵌 Widget。
- 本仓库默认流程是确定性数字孪生。只有真实 Worker 运行被部署并留存回执后，才可将画面标记为 AgentTeams live run。

## 录屏建议

先录 Element 房间收到调查任务，再点击房间中的 ProofOps 链接。控制台一键运行到审批，人工点击批准、执行、独立复测，最后演示回滚使旧验证失效。
