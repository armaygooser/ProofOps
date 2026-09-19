import {
  ApiOutlined,
  AuditOutlined,
  CheckCircleFilled,
  ClockCircleOutlined,
  CloudServerOutlined,
  ControlOutlined,
  DatabaseOutlined,
  ExperimentOutlined,
  EyeOutlined,
  FireOutlined,
  LockOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  RobotOutlined,
  SafetyCertificateFilled,
  SafetyCertificateOutlined,
  SyncOutlined,
  ThunderboltOutlined,
  UndoOutlined,
  WarningFilled,
} from '@ant-design/icons';
import {
  Badge,
  Button,
  Checkbox,
  ConfigProvider,
  Input,
  Modal,
  Progress,
  Space,
  Spin,
  Tag,
  Tooltip,
  Typography,
  message,
  theme,
} from 'antd';
import { useEffect, useMemo, useState } from 'react';

import { demoApi } from './api';
import type { AgentState, AuditEvent, DemoState, EvidenceRecord } from './types';
import { shortHash } from './utils/hash';

const { Text } = Typography;

const phaseNames: Record<string, string> = {
  detected: '异常已发现',
  investigating: '智能体调查中',
  ready_to_propose: '调查完成',
  awaiting_approval: '等待人类审批',
  approved: '已批准，待执行',
  executed: '动作已执行',
  verified: '独立复测通过',
  verification_failed: '独立复测未通过',
  rolled_back: '已安全回滚',
};

const statusColors: Record<string, string> = {
  queued: 'default',
  working: 'processing',
  complete: 'success',
};

const eventNames: Record<string, string> = {
  pending_approval: '提案入链',
  approved: '人类批准',
  executed: '受控执行',
  rolled_back: '安全回滚',
};

const delay = (ms: number) => new Promise((resolve) => window.setTimeout(resolve, ms));

function Metric({ label, value, unit, tone }: { label: string; value: string | number; unit: string; tone?: string }) {
  return (
    <div className={`metric-cell ${tone ?? ''}`}>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{unit}</small>
    </div>
  );
}

function AgentRow({ agent, index }: { agent: AgentState; index: number }) {
  return (
    <div className={`agent-row agent-${agent.status}`}>
      <div className="agent-index">0{index + 1}</div>
      <div className="agent-main">
        <div className="agent-title">
          <strong>{agent.name}</strong>
          <Badge status={statusColors[agent.status] as 'default' | 'processing' | 'success'} />
        </div>
        <Tag variant="filled" className="permission-tag"><LockOutlined /> {agent.permission}</Tag>
        <p>{agent.status === 'queued' ? '等待上游证据…' : agent.finding}</p>
      </div>
      <div className="agent-evidence">
        {agent.evidence_id ? <Tooltip title={agent.evidence_id}><SafetyCertificateFilled /></Tooltip> : <ClockCircleOutlined />}
      </div>
    </div>
  );
}

function HashLine({ label, value }: { label: string; value?: string | null }) {
  return (
    <div className="hash-line">
      <span>{label}</span>
      <Tooltip title={value ?? '尚未生成'}><code>{shortHash(value)}</code></Tooltip>
    </div>
  );
}

function EvidenceCard({ record }: { record: EvidenceRecord }) {
  return (
    <div className="evidence-card">
      <div className="evidence-icon"><DatabaseOutlined /></div>
      <div className="evidence-copy">
        <strong>{record.title}</strong>
        <span>{record.evidence_id}</span>
        <HashLine label="内容" value={record.content_sha256} />
        <HashLine label="封装" value={record.envelope_sha256} />
      </div>
    </div>
  );
}

function AuditNode({ event, active }: { event: AuditEvent; active: boolean }) {
  return (
    <div className={`audit-node ${active ? 'audit-active' : ''}`}>
      <span className="audit-dot"><CheckCircleFilled /></span>
      <div>
        <strong>{eventNames[event.status] ?? event.status}</strong>
        <code>{shortHash(event.record_sha256)}</code>
      </div>
    </div>
  );
}

export function ProofOpsApp() {
  const [state, setState] = useState<DemoState | null>(null);
  const [busy, setBusy] = useState(false);
  const [approveOpen, setApproveOpen] = useState(false);
  const [rollbackOpen, setRollbackOpen] = useState(false);
  const [approver, setApprover] = useState('值班总管-01');
  const [acknowledged, setAcknowledged] = useState(false);
  const [messageApi, contextHolder] = message.useMessage();

  useEffect(() => {
    demoApi.get().then(setState).catch((error: Error) => messageApi.error(error.message));
  }, [messageApi]);

  const completion = useMemo(() => {
    if (!state) return 0;
    return Math.round((state.agents.filter((agent) => agent.status === 'complete').length / 7) * 100);
  }, [state]);

  const mutate = async (operation: () => Promise<DemoState>, success?: string) => {
    setBusy(true);
    try {
      const next = await operation();
      setState(next);
      if (success) messageApi.success(success);
      return next;
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : '操作失败');
      return null;
    } finally {
      setBusy(false);
    }
  };

  const runToApproval = async () => {
    setBusy(true);
    try {
      let next = await demoApi.post('reset');
      setState(next);
      await delay(450);
      for (let index = 0; index < 7; index += 1) {
        next = await demoApi.post('investigate/advance');
        setState(next);
        await delay(520);
      }
      next = await demoApi.post('propose');
      setState(next);
      messageApi.success('七个智能体已完成调查，提案等待人类审批');
    } catch (error) {
      messageApi.error(error instanceof Error ? error.message : '演示启动失败');
    } finally {
      setBusy(false);
    }
  };

  const approve = async () => {
    if (!state?.proposal) return;
    const next = await mutate(
      () => demoApi.post('approve', {
        approver,
        proposal_hash: state.proposal?.record_sha256,
        acknowledged,
      }),
      '批准已与提案哈希绑定并写入审计链',
    );
    if (next) {
      setApproveOpen(false);
      setAcknowledged(false);
    }
  };

  const rollback = async () => {
    if (!state?.execution) return;
    const next = await mutate(
      () => demoApi.post('rollback', {
        approver,
        execution_hash: state.execution?.record_sha256,
        confirmed: true,
      }),
      '设备已回到安全状态，旧复测结论已失效',
    );
    if (next) setRollbackOpen(false);
  };

  if (!state) {
    return <div className="boot-screen"><Spin size="large" /><span>正在连接证控中枢…</span></div>;
  }

  const latestEvidence = state.evidence.slice(-4).reverse();
  const latestEvents = state.audit_events.slice(-4);
  const backupRunning = state.twin.backup_chiller === 'running';
  const canRollback = ['executed', 'verified', 'verification_failed'].includes(state.phase);

  return (
    <ConfigProvider theme={{
      algorithm: theme.darkAlgorithm,
      token: {
        colorPrimary: '#20d7ff', colorSuccess: '#33e6a6', colorWarning: '#ffbd4a', colorError: '#ff5f77',
        colorBgBase: '#07101f', colorTextBase: '#eaf8ff', borderRadius: 6, fontSize: 13,
        fontFamily: 'Inter, "Microsoft YaHei", "PingFang SC", sans-serif',
      },
    }}>
      {contextHolder}
      <main className="control-room">
        <header className="topbar">
          <div className="brand-lockup">
            <div className="brand-mark"><SafetyCertificateOutlined /></div>
            <div>
              <div className="brand-line"><strong>ProofOps</strong><span>证控中枢</span></div>
              <small>TRUSTED AGENTIC OPERATIONS CENTER</small>
            </div>
          </div>
          <div className="mission-title">
            <span className="eyebrow">ACTIVE INCIDENT · {state.incident_id}</span>
            <h1>{state.scenario}</h1>
          </div>
          <div className="top-actions">
            <Tag icon={<ExperimentOutlined />} color="geekblue">隔离数字孪生</Tag>
            <Tag icon={<SafetyCertificateFilled />} color={state.audit.valid ? 'success' : 'error'}>
              审计链 {state.audit.valid ? '可信' : '异常'}
            </Tag>
            <Button icon={<ReloadOutlined />} disabled={busy} onClick={() => mutate(() => demoApi.post('reset'), '演示已重置')}>
              重置
            </Button>
          </div>
        </header>

        <section className="status-rail">
          <div className="phase-block">
            <span className="pulse-dot" />
            <div><small>当前态势</small><strong>{phaseNames[state.phase] ?? state.phase}</strong></div>
          </div>
          <Metric label="区域温度" value={state.twin.temperature_c.toFixed(1)} unit="°C" tone={state.twin.temperature_c > 26 ? 'danger' : 'safe'} />
          <Metric label="园区功率" value={state.twin.power_kw.toFixed(0)} unit="kW" tone={state.twin.power_kw > 500 ? 'danger' : ''} />
          <Metric label="设备心跳" value={state.twin.heartbeat_pct.toFixed(1)} unit="%" tone={state.twin.heartbeat_pct >= 99 ? 'safe' : 'warning'} />
          <div className="run-meta"><span>RUN</span><code>{state.run_id}</code><small>CyberGuard contract v{state.core.version}</small></div>
        </section>

        <section className="dashboard-grid">
          <aside className="panel agent-panel">
            <div className="panel-heading">
              <div><span>01</span><div><small>AGENT WORKFORCE</small><h2>协同调查链</h2></div></div>
              <Progress type="circle" percent={completion} size={44} strokeColor="#20d7ff" railColor="#15283e" />
            </div>
            <div className="agent-list">
              {state.agents.map((agent, index) => <AgentRow key={agent.id} agent={agent} index={index} />)}
            </div>
            <Button
              block type="primary" size="large" icon={<PlayCircleOutlined />}
              disabled={busy || state.phase === 'awaiting_approval'} loading={busy}
              onClick={runToApproval}
            >
              一键演示至审批
            </Button>
          </aside>

          <section className="panel twin-panel">
            <div className="panel-heading compact">
              <div><span>02</span><div><small>ISOLATED DIGITAL TWIN</small><h2>B2 冷却系统镜像</h2></div></div>
              <Tag color={backupRunning ? 'success' : 'default'}>{backupRunning ? '动作生效' : '仅观测'}</Tag>
            </div>

            <div className={`twin-stage ${backupRunning ? 'twin-stable' : 'twin-alert'}`}>
              <div className="radar-ring ring-one" /><div className="radar-ring ring-two" />
              <div className="flow-line flow-a" /><div className="flow-line flow-b" />
              <div className="zone-label"><CloudServerOutlined /><span>B2<br />DATA HALL</span></div>
              <div className="thermal-core">
                <small>实时温度</small>
                <strong>{state.twin.temperature_c.toFixed(1)}<em>°C</em></strong>
                <span>{state.twin.temperature_c <= 26 ? 'SAFE RANGE' : 'THERMAL ALERT'}</span>
              </div>
              <div className="equipment-card primary-unit">
                <span>主冷机</span><strong>CHILLER-01</strong>
                <Tag color="warning">效率衰减</Tag>
              </div>
              <div className={`equipment-card backup-unit ${backupRunning ? 'unit-running' : ''}`}>
                <span>备用冷机</span><strong>CHILLER-02</strong>
                <Tag color={backupRunning ? 'success' : 'default'}>{backupRunning ? '运行中' : '待机'}</Tag>
              </div>
              <div className="twin-legend">
                <span><i className="legend-cyan" />遥测流</span>
                <span><i className="legend-amber" />风险区</span>
                <span><i className="legend-green" />安全边界</span>
              </div>
            </div>

            <div className="verification-contract">
              <div className="contract-title"><EyeOutlined /><span>独立复测契约</span></div>
              {['温度 ≤ 26°C', '功率 ≤ 500kW', '心跳 ≥ 99%'].map((label, index) => {
                const check = state.verification.checks[index];
                return (
                  <div className="contract-check" key={label}>
                    {check?.passed ? <CheckCircleFilled /> : <span className="check-empty" />}
                    <span>{label}</span>
                  </div>
                );
              })}
              <Tag color={state.verification.status === 'passed' ? 'success' : state.verification.status === 'invalidated' ? 'error' : 'default'}>
                {state.verification.status === 'passed' ? '复测通过' : state.verification.status === 'invalidated' ? '已因回滚失效' : '等待复测'}
              </Tag>
            </div>
          </section>

          <aside className="panel approval-panel">
            <div className="panel-heading compact">
              <div><span>03</span><div><small>HUMAN AUTHORITY</small><h2>人类审批舱</h2></div></div>
              <LockOutlined className="heading-icon" />
            </div>

            {state.proposal ? (
              <div className="proposal-sheet">
                <div className="risk-strip"><WarningFilled /><span>L2 可逆操作</span><Tag color="warning">15 分钟有效</Tag></div>
                <div className="proposal-target"><small>拟执行对象</small><strong>B2-CHILLER-02</strong><span>启用备用冷机 · 保留主机运行</span></div>
                <div className="reason-box"><small>智能体合议结论</small><p>{state.proposal.reason}</p></div>
                <HashLine label="证据包 SHA-256" value={state.proposal.evidence_bundle_sha256} />
                <HashLine label="提案记录 SHA-256" value={state.proposal.record_sha256} />
                <div className="boundary-note"><SafetyCertificateOutlined /> 人类只批准这一份目标、参数和证据均已固定的提案。</div>
              </div>
            ) : (
              <div className="empty-proposal"><RobotOutlined /><strong>等待调查结论</strong><span>智能体没有执行权限，只能形成提案。</span></div>
            )}

            <div className="command-stack">
              <Button
                type="primary" size="large" icon={<SafetyCertificateOutlined />} block
                disabled={state.phase !== 'awaiting_approval' || busy}
                onClick={() => setApproveOpen(true)}
              >人类批准提案</Button>
              <Button
                size="large" icon={<ThunderboltOutlined />} block
                disabled={state.phase !== 'approved' || busy}
                onClick={() => mutate(() => demoApi.post('execute'), '受控动作已执行')}
              >执行已批准动作</Button>
              <Button
                size="large" icon={<AuditOutlined />} block
                disabled={state.phase !== 'executed' || busy}
                onClick={() => mutate(() => demoApi.post('verify'), '独立复测已完成')}
              >启动独立复测</Button>
              <Button
                danger size="large" icon={<UndoOutlined />} block
                disabled={!canRollback || busy}
                onClick={() => setRollbackOpen(true)}
              >回滚到安全状态</Button>
            </div>
          </aside>

          <section className="panel proof-panel">
            <div className="proof-column evidence-column">
              <div className="panel-heading compact">
                <div><span>04</span><div><small>INDEPENDENT DIGESTS</small><h2>证据哈希摘要</h2></div></div>
                <Tag>{state.evidence.length} 份证据</Tag>
              </div>
              <div className="evidence-grid">
                {latestEvidence.map((record) => <EvidenceCard key={record.evidence_id} record={record} />)}
              </div>
            </div>
            <div className="proof-divider" />
            <div className="proof-column audit-column">
              <div className="panel-heading compact">
                <div><span>05</span><div><small>HMAC LINKED LEDGER</small><h2>操作审计链</h2></div></div>
                <Tag color={state.audit.valid ? 'success' : 'error'}>{state.audit.algorithm} · {state.audit.records} 条</Tag>
              </div>
              <div className="audit-chain">
                {latestEvents.length ? latestEvents.map((event, index) => (
                  <AuditNode key={event.record_sha256} event={event} active={index === latestEvents.length - 1} />
                )) : <div className="audit-empty"><ControlOutlined /> 首个动作提案生成后开始串联记录</div>}
              </div>
              <HashLine label="当前链头" value={state.audit.head} />
            </div>
          </section>
        </section>

        <footer className="footer-bar">
          <span><ApiOutlined /> CyberGuard 治理契约 · 嵌入式领域适配器</span>
          <span><SyncOutlined spin={busy} /> {busy ? '流程运行中' : '状态已同步'}</span>
          <span><FireOutlined /> DEMO MODE · 未连接真实 PLC / BMS</span>
        </footer>
      </main>

      <Modal
        title="批准受控操作" open={approveOpen} confirmLoading={busy}
        okText="确认批准并写入审计链" cancelText="返回复核"
        okButtonProps={{ disabled: !acknowledged }}
        onOk={approve} onCancel={() => setApproveOpen(false)}
      >
        <div className="approval-modal-copy">
          <p>批准对象：<strong>B2-CHILLER-02</strong></p>
          <p>提案哈希：<code>{state.proposal?.record_sha256}</code></p>
          <Input value={approver} onChange={(event) => setApprover(event.target.value)} addonBefore="审批人" />
          <Checkbox checked={acknowledged} onChange={(event) => setAcknowledged(event.target.checked)}>
            我已核对目标、风险、证据摘要与回滚能力，仅批准当前哈希对应的提案。
          </Checkbox>
        </div>
      </Modal>

      <Modal
        title="执行安全回滚" open={rollbackOpen} confirmLoading={busy}
        okText="确认回滚" okButtonProps={{ danger: true }} cancelText="取消"
        onOk={rollback} onCancel={() => setRollbackOpen(false)}
      >
        <div className="approval-modal-copy">
          <p>系统将停止 B2-CHILLER-02，并恢复数字孪生的安全基线。</p>
          <p>执行记录：<code>{state.execution?.record_sha256}</code></p>
          <p className="rollback-warning">回滚完成后，当前独立复测结论会被标记为失效。</p>
        </div>
      </Modal>
    </ConfigProvider>
  );
}
