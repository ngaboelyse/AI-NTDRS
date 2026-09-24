import type {
  AlertRecord,
  AuditLogRecord,
  DashboardSummary,
  Device,
  CopilotResponse,
  IncidentRecord,
  ReportRecord,
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

export async function getAlerts(): Promise<AlertRecord[]> {
  return request<AlertRecord[]>('/alerts');
}

export async function getIncidents(): Promise<IncidentRecord[]> {
  return request<IncidentRecord[]>('/incidents');
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
