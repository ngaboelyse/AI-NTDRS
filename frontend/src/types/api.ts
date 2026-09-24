export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  roles: string[];
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface DashboardSummary {
  total_monitored_devices: number;
  active_devices: number;
  threats_detected_today: number;
  critical_alerts: number;
  network_flows_analyzed: number;
  current_risk_level: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}

export interface Device {
  id: number;
  device_identifier: string;
  ip_address: string;
  hostname?: string | null;
  device_type: string;
  last_seen?: string | null;
  activity_level: string;
  risk_score: number;
  alert_count: number;
  status: string;
}

export interface AlertRecord {
  id: number;
  alert_id: string;
  source_ip: string;
  destination_ip: string;
  protocol: string;
  threat_category: string;
  risk_score: number;
  severity: string;
  detection_reason: string;
  model_confidence?: number | null;
  status: string;
  assigned_analyst_id?: number | null;
  analyst_notes?: string | null;
  recommended_action?: string | null;
  resolution_time?: string | null;
}

export interface IncidentRecord {
  id: number;
  incident_code: string;
  title: string;
  status: string;
  summary?: string | null;
  assigned_analyst_id?: number | null;
  opened_at: string;
  last_activity_at: string;
  resolved_at?: string | null;
}

export interface IncidentNote {
  id: number;
  incident_id: number;
  author_user_id: number;
  body: string;
  created_at: string;
}

export interface ResponseActionRequest {
  id: number;
  incident_id?: number | null;
  alert_id?: number | null;
  action_type: string;
  details: string;
  status: string;
  requested_by_user_id: number;
  approved_by_user_id?: number | null;
  rejected_by_user_id?: number | null;
  requested_at: string;
  approved_at?: string | null;
}

export interface SimulatedResponseAction {
  id: number;
  incident_id?: number | null;
  alert_id?: number | null;
  action_type: string;
  is_simulated: boolean;
  requested_by_user_id: number;
  approved_by_user_id?: number | null;
  details?: string | null;
  executed_at: string;
  result: string;
}

export interface ReportRecord {
  id: number;
  report_title: string;
  incident_id?: number | null;
  generated_by_user_id?: number | null;
  export_format: string;
  file_path?: string | null;
}

export interface AuditLogRecord {
  id: number;
  user_id?: number | null;
  action: string;
  resource: string;
  result: string;
  event_metadata?: Record<string, unknown> | null;
  ip_address?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CopilotResponse {
  answer: string;
  assistant_mode: 'local_model' | 'fallback' | string;
  model_name: string;
  show_context: boolean;
  facts: string[];
  predictions: string[];
  recommendations: string[];
  unknowns: string[];
  related_devices: Array<{
    id: number;
    device_identifier: string;
    ip_address: string;
    device_type: string;
    risk_score: number;
    alert_count: number;
    status: string;
  }>;
  related_alerts: Array<{
    id: number;
    alert_id: string;
    severity: string;
    threat_category: string;
    risk_score: number;
    status: string;
    source_ip: string;
    destination_ip: string;
  }>;
}
