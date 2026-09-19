export type AgentStatus = 'queued' | 'working' | 'complete';

export interface AgentState {
  id: string;
  name: string;
  permission: string;
  finding: string;
  status: AgentStatus;
  evidence_id: string | null;
}

export interface EvidenceRecord {
  evidence_id: string;
  source: string;
  title: string;
  captured_at: string;
  content_sha256: string;
  envelope_sha256: string;
}

export interface AuditEvent {
  action_id: string;
  status: string;
  recorded_at: string;
  record_sha256: string;
  record_hmac_sha256: string;
  previous_record_sha256: string | null;
  approval_expires_at?: string;
  approver?: string;
}

export interface DemoState {
  product: string;
  display_name: string;
  run_id: string;
  incident_id: string;
  phase: string;
  scenario: string;
  safety_boundary: string;
  core: { name: string; version: string; mode: string };
  agents: AgentState[];
  twin: {
    zone: string;
    temperature_c: number;
    power_kw: number;
    heartbeat_pct: number;
    primary_chiller: string;
    backup_chiller: string;
  };
  evidence: EvidenceRecord[];
  proposal: (AuditEvent & {
    action: string;
    target: string;
    reason: string;
    risk: string;
    reversible: boolean;
    evidence_bundle_sha256: string;
  }) | null;
  approval: AuditEvent | null;
  execution: AuditEvent | null;
  verification: {
    status: string;
    invalidated_by_rollback: boolean;
    evidence_id?: string;
    checks: Array<{ label: string; value: number; passed: boolean }>;
  };
  audit: { valid: boolean; authenticated: boolean; algorithm: string; records: number; head: string | null };
  audit_events: AuditEvent[];
  approver: string | null;
  server_time: string;
}
