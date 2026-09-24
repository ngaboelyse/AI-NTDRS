import type {
  AlertRecord,
  AuditLogRecord,
  DashboardSummary,
  Device,
  CopilotResponse,
  IncidentRecord,
  IncidentNote,
  ResponseActionRequest,
  ReportRecord,
  SimulatedResponseAction,
  TokenResponse,
  User,
} from '../types/api';

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000/api';
const tokenStorageKey = 'ai-ntdrs-token';

function getHeaders(includeJson = true): HeadersInit {
  const headers: HeadersInit = {};
  const token = localStorage.getItem(tokenStorageKey);

  if (includeJson) {
    headers['Content-Type'] = 'application/json';
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  return headers;
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers: {
      ...getHeaders(init.body instanceof FormData ? false : init.body !== undefined),
      ...init.headers,
    },
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getStoredToken(): string | null {
  return localStorage.getItem(tokenStorageKey);
}

export function clearToken(): void {
  localStorage.removeItem(tokenStorageKey);
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.set('username', email);
  formData.set('password', password);

  const response = await fetch(`${apiBaseUrl}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Invalid credentials');
  }

  const tokenResponse = (await response.json()) as TokenResponse;
  localStorage.setItem(tokenStorageKey, tokenResponse.access_token);
  return tokenResponse;
}

export async function getCurrentUser(): Promise<User> {
  return request<User>('/auth/me');
}

export async function getDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>('/dashboard/summary');
}

export async function getDevices(): Promise<Device[]> {
  return request<Device[]>('/devices');
}

export async function registerDevice(payload: { device_identifier: string; ip_address: string; hostname?: string; device_type: string }): Promise<Device> {
  return request<Device>('/devices', { method: 'POST', body: JSON.stringify(payload) });
}

export async function getAlerts(): Promise<AlertRecord[]> {
  return request<AlertRecord[]>('/alerts');
}

export async function updateAlert(alertId: number, changes: { status?: string; assigned_analyst_id?: number | null; analyst_notes?: string | null }): Promise<AlertRecord> {
  return request<AlertRecord>(`/alerts/${alertId}`, { method: 'PATCH', body: JSON.stringify(changes) });
}

export async function getIncidents(): Promise<IncidentRecord[]> {
  return request<IncidentRecord[]>('/incidents');
}

export async function updateIncident(incidentId: number, changes: { status?: string; summary?: string | null; assigned_analyst_id?: number | null }): Promise<IncidentRecord> {
  return request<IncidentRecord>(`/incidents/${incidentId}`, { method: 'PATCH', body: JSON.stringify(changes) });
}

export async function getIncidentNotes(incidentId: number): Promise<IncidentNote[]> {
  return request<IncidentNote[]>(`/incidents/${incidentId}/notes`);
}

export async function addIncidentNote(incidentId: number, body: string): Promise<IncidentNote> {
  return request<IncidentNote>(`/incidents/${incidentId}/notes`, { method: 'POST', body: JSON.stringify({ body }) });
}

export async function getResponseActionRequests(): Promise<ResponseActionRequest[]> {
  return request<ResponseActionRequest[]>('/response-actions/requests');
}

export async function requestResponseAction(payload: { incident_id: number; action_type: string; details: string }): Promise<ResponseActionRequest> {
  return request<ResponseActionRequest>('/response-actions/requests', { method: 'POST', body: JSON.stringify(payload) });
}

export async function approveResponseAction(requestId: number): Promise<SimulatedResponseAction> {
  return request<SimulatedResponseAction>(`/response-actions/requests/${requestId}/approve`, { method: 'POST' });
}

export async function rejectResponseAction(requestId: number): Promise<ResponseActionRequest> {
  return request<ResponseActionRequest>(`/response-actions/requests/${requestId}/reject`, { method: 'POST' });
}

export async function getSimulatedResponseActions(): Promise<SimulatedResponseAction[]> {
  return request<SimulatedResponseAction[]>('/response-actions');
}

export async function getReports(): Promise<ReportRecord[]> {
  return request<ReportRecord[]>('/reports');
}

export async function getAuditLogs(): Promise<AuditLogRecord[]> {
  return request<AuditLogRecord[]>('/audit-logs');
}

export async function queryCopilot(
  query: string,
  history: Array<{ role: 'user' | 'assistant'; content: string }> = [],
): Promise<CopilotResponse> {
  return request<CopilotResponse>('/copilot/query', {
    method: 'POST',
    body: JSON.stringify({ query, history }),
  });
}

export async function logout(): Promise<void> {
  try {
    await request('/auth/logout', { method: 'POST' });
  } finally {
    clearToken();
  }
}
