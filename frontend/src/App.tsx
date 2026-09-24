import { useEffect, useMemo, useState } from 'react';
import {
  clearToken,
  getAlerts,
  getAuditLogs,
  getCurrentUser,
  getDashboardSummary,
  getDevices,
  getIncidents,
  getReports,
  getStoredToken,
  login,
  queryCopilot,
  logout,
} from './services/api';
import type {
  AlertRecord,
  AuditLogRecord,
  DashboardSummary,
  Device,
  IncidentRecord,
  CopilotResponse,
  ReportRecord,
  User,
} from './types/api';

type ViewKey = 'dashboard' | 'search' | 'devices' | 'alerts' | 'incidents' | 'reports' | 'audit-logs' | 'copilot';
type CopilotTurn = { role: 'user' | 'assistant'; content: string };

const demoEmail = 'admin@ai-ntdrs.local';
const demoPassword = 'ChangeMe123!';

const navigation: Array<{ key: ViewKey; label: string }> = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'search', label: 'Global Search' },
  { key: 'devices', label: 'Devices' },
  { key: 'alerts', label: 'Alerts' },
  { key: 'incidents', label: 'Incidents' },
  { key: 'reports', label: 'Reports' },
  { key: 'audit-logs', label: 'Audit Logs' },
  { key: 'copilot', label: 'AI Copilot' },
];

export default function App() {
  const [user, setUser] = useState<User | null>(null);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [devices, setDevices] = useState<Device[]>([]);
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [incidents, setIncidents] = useState<IncidentRecord[]>([]);
  const [reports, setReports] = useState<ReportRecord[]>([]);
  const [auditLogs, setAuditLogs] = useState<AuditLogRecord[]>([]);
  const [copilotResponse, setCopilotResponse] = useState<CopilotResponse | null>(null);
  const [copilotMessages, setCopilotMessages] = useState<CopilotTurn[]>([]);
  const [copilotQuery, setCopilotQuery] = useState('');
  const [copilotLoading, setCopilotLoading] = useState(false);
  const [view, setView] = useState<ViewKey>('dashboard');
  const [globalSearch, setGlobalSearch] = useState('');
  const [deviceSearch, setDeviceSearch] = useState('');
  const [alertSearch, setAlertSearch] = useState('');
  const [alertSeverity, setAlertSeverity] = useState('ALL');
  const [alertStatus, setAlertStatus] = useState('ALL');
  const [incidentSearch, setIncidentSearch] = useState('');
  const [incidentStatus, setIncidentStatus] = useState('ALL');
  const [reportSearch, setReportSearch] = useState('');
  const [auditSearch, setAuditSearch] = useState('');
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | null>(null);
  const [selectedAlertId, setSelectedAlertId] = useState<number | null>(null);
  const [selectedIncidentId, setSelectedIncidentId] = useState<number | null>(null);
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [email, setEmail] = useState(demoEmail);
  const [password, setPassword] = useState(demoPassword);

  async function loadWorkspace() {
    const [currentUser, dashboardSummary, deviceList, alertList, incidentList, reportList, auditLogList] = await Promise.all([
      getCurrentUser(),
      getDashboardSummary(),
      getDevices(),
      getAlerts(),
      getIncidents(),
      getReports(),
      getAuditLogs(),
    ]);

    setUser(currentUser);
    setSummary(dashboardSummary);
    setDevices(deviceList);
    setAlerts(alertList);
    setIncidents(incidentList);
    setReports(reportList);
    setAuditLogs(auditLogList);
  }

  useEffect(() => {
    async function bootstrap() {
      if (!getStoredToken()) {
        setLoading(false);
        return;
      }

      try {
        await loadWorkspace();
      } catch {
        clearToken();
      } finally {
        setLoading(false);
      }
    }

    void bootstrap();
  }, []);

  async function handleLogin(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      await login(email, password);
      await loadWorkspace();
    } catch (loginError) {
      setError(loginError instanceof Error ? loginError.message : 'Unable to sign in');
    } finally {
      setSubmitting(false);
    }
  }

  async function handleLogout() {
    await logout();
    setUser(null);
    setSummary(null);
    setDevices([]);
    setAlerts([]);
    setIncidents([]);
    setReports([]);
    setAuditLogs([]);
    setCopilotResponse(null);
    setCopilotMessages([]);
  }

  async function runCopilotQuery(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const query = copilotQuery.trim();
    if (query.length < 3) return;

    setCopilotLoading(true);
    setError(null);

    try {
      const response = await queryCopilot(query, copilotMessages.slice(-8));
      setCopilotResponse(response);
      setCopilotMessages((messages) => [
        ...messages,
        { role: 'user', content: query },
        { role: 'assistant', content: response.answer },
      ].slice(-20));
      setCopilotQuery('');
      setView('copilot');
    } catch (copilotError) {
      setError(copilotError instanceof Error ? copilotError.message : 'Unable to query copilot');
    } finally {
      setCopilotLoading(false);
    }
  }

  const recentAlerts = useMemo(() => alerts.slice(0, 3), [alerts]);
  const recentDevices = useMemo(() => devices.slice(0, 4), [devices]);
  const filteredDevices = useMemo(() => {
    const query = deviceSearch.trim().toLowerCase();
    return devices.filter((device) => {
      if (!query) {
        return true;
      }

      return [device.device_identifier, device.ip_address, device.hostname ?? '', device.device_type, device.status]
        .some((value) => value.toLowerCase().includes(query));
    });
  }, [deviceSearch, devices]);

  const filteredAlerts = useMemo(() => {
    const query = alertSearch.trim().toLowerCase();
    return alerts.filter((alert) => {
      const matchesQuery = !query || [alert.alert_id, alert.threat_category, alert.severity, alert.status, alert.source_ip, alert.destination_ip]
        .some((value) => value.toLowerCase().includes(query));
      const matchesSeverity = alertSeverity === 'ALL' || alert.severity === alertSeverity;
      const matchesStatus = alertStatus === 'ALL' || alert.status === alertStatus;
      return matchesQuery && matchesSeverity && matchesStatus;
    });
  }, [alertSearch, alertSeverity, alertStatus, alerts]);

  const filteredIncidents = useMemo(() => {
    const query = incidentSearch.trim().toLowerCase();
    return incidents.filter((incident) => {
      const matchesQuery = !query || [incident.incident_code, incident.title, incident.status, incident.summary ?? '']
        .some((value) => value.toLowerCase().includes(query));
      const matchesStatus = incidentStatus === 'ALL' || incident.status === incidentStatus;
      return matchesQuery && matchesStatus;
    });
  }, [incidentSearch, incidentStatus, incidents]);

  const filteredReports = useMemo(() => {
    const query = reportSearch.trim().toLowerCase();
    return reports.filter((report) => {
      if (!query) {
        return true;
      }

      return [report.report_title, report.export_format, report.file_path ?? '', String(report.incident_id ?? '')]
        .some((value) => value.toLowerCase().includes(query));
    });
  }, [reportSearch, reports]);

  const filteredAuditLogs = useMemo(() => {
    const query = auditSearch.trim().toLowerCase();
    return auditLogs.filter((entry) => {
      if (!query) {
        return true;
      }

      return [entry.action, entry.resource, entry.result, entry.ip_address ?? '']
        .some((value) => value.toLowerCase().includes(query));
    });
  }, [auditSearch, auditLogs]);

  const globalSearchQuery = globalSearch.trim().toLowerCase();
  const globalDeviceResults = useMemo(() => {
    if (!globalSearchQuery) {
      return [] as Device[];
    }

    return devices.filter((device) => [device.device_identifier, device.ip_address, device.hostname ?? '', device.device_type, device.status]
      .some((value) => value.toLowerCase().includes(globalSearchQuery)));
  }, [devices, globalSearchQuery]);

  const globalAlertResults = useMemo(() => {
    if (!globalSearchQuery) {
      return [] as AlertRecord[];
    }

    return alerts.filter((alert) => [alert.alert_id, alert.threat_category, alert.severity, alert.status, alert.source_ip, alert.destination_ip]
      .some((value) => value.toLowerCase().includes(globalSearchQuery)));
  }, [alerts, globalSearchQuery]);

  const globalIncidentResults = useMemo(() => {
    if (!globalSearchQuery) {
      return [] as IncidentRecord[];
    }

    return incidents.filter((incident) => [incident.incident_code, incident.title, incident.status, incident.summary ?? '']
      .some((value) => value.toLowerCase().includes(globalSearchQuery)));
  }, [globalSearchQuery, incidents]);

  const globalReportResults = useMemo(() => {
    if (!globalSearchQuery) {
      return [] as ReportRecord[];
    }

    return reports.filter((report) => [report.report_title, report.export_format, report.file_path ?? '', String(report.incident_id ?? '')]
      .some((value) => value.toLowerCase().includes(globalSearchQuery)));
  }, [globalSearchQuery, reports]);

  const globalAuditResults = useMemo(() => {
    if (!globalSearchQuery) {
      return [] as AuditLogRecord[];
    }

    return auditLogs.filter((entry) => [entry.action, entry.resource, entry.result, entry.ip_address ?? '']
      .some((value) => value.toLowerCase().includes(globalSearchQuery)));
  }, [auditLogs, globalSearchQuery]);

  const selectedDevice = useMemo(
    () => filteredDevices.find((device) => device.id === selectedDeviceId) ?? null,
    [filteredDevices, selectedDeviceId],
  );

  const selectedAlert = useMemo(
    () => filteredAlerts.find((alert) => alert.id === selectedAlertId) ?? null,
    [filteredAlerts, selectedAlertId],
  );

  const selectedIncident = useMemo(
    () => filteredIncidents.find((incident) => incident.id === selectedIncidentId) ?? null,
    [filteredIncidents, selectedIncidentId],
  );

  const notifications = useMemo(() => {
    const highSeverityAlerts = alerts
      .filter((alert) => alert.severity === 'HIGH' || alert.severity === 'CRITICAL')
      .slice(0, 4)
      .map((alert) => ({
        title: `${alert.severity} alert ${alert.alert_id}`,
        body: `${alert.threat_category} on ${alert.source_ip}`,
      }));

    const activeIncidents = incidents
      .filter((incident) => incident.status === 'NEW' || incident.status === 'INVESTIGATING')
      .slice(0, 4)
      .map((incident) => ({
        title: `Incident ${incident.incident_code}`,
        body: `${incident.status} - ${incident.title}`,
      }));

    const reportReady = reports.slice(0, 2).map((report) => ({
      title: `Report ready: ${report.report_title}`,
      body: `${report.export_format.toUpperCase()} export available`,
    }));

    return [...highSeverityAlerts, ...activeIncidents, ...reportReady];
  }, [alerts, incidents, reports]);

  useEffect(() => {
    if (filteredDevices.length > 0 && selectedDeviceId === null) {
      setSelectedDeviceId(filteredDevices[0].id);
    }
  }, [filteredDevices, selectedDeviceId]);

  useEffect(() => {
    if (filteredAlerts.length > 0 && selectedAlertId === null) {
      setSelectedAlertId(filteredAlerts[0].id);
    }
  }, [filteredAlerts, selectedAlertId]);

  useEffect(() => {
    if (filteredIncidents.length > 0 && selectedIncidentId === null) {
      setSelectedIncidentId(filteredIncidents[0].id);
    }
  }, [filteredIncidents, selectedIncidentId]);

  if (loading) {
    return (
      <div className="app-shell login-screen login-loading-screen">
        <main className="auth-card panel">
          <p className="eyebrow">AI-NTDRS</p>
          <h1>Loading secure workspace...</h1>
          <p className="muted-text">Preparing dashboard and authentication state.</p>
        </main>
      </div>
    );
  }

  if (!user || !summary) {
    return (
      <div className="app-shell login-screen">
        <section className="login-brand" aria-label="About AI-NTDRS">
          <div className="login-brand-mark" aria-label="AI-NTDRS">
            <span className="brand-icon" aria-hidden="true">
              <svg viewBox="0 0 32 32" fill="none">
                <path d="M16 3.5 27 8v7.4c0 6.2-4.2 10.7-11 13.1C9.2 26.1 5 21.6 5 15.4V8l11-4.5Z" stroke="currentColor" strokeWidth="1.8" />
                <path d="m11.5 16 3 3 6.5-7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </span>
            <span>AI-NTDRS</span>
          </div>

          <div className="login-brand-copy">
            <p className="login-overline"><span /> Security operations platform</p>
            <h1>Clarity when<br />security matters.</h1>
            <p>Monitor your network, investigate threats, and coordinate response from one trusted workspace.</p>
          </div>

          <div className="login-visual" aria-hidden="true">
            <div className="visual-glow" />
            <svg viewBox="0 0 520 330" fill="none">
              <path d="M50 235 143 177l83 41 91-112 85 64 73-55" stroke="url(#line)" strokeWidth="1.5" />
              <path d="m143 177 30 104 53-63 65 72 26-184M317 106l5 184 80-120 73 55" stroke="url(#line)" strokeWidth="1" opacity=".55" />
              <circle cx="50" cy="235" r="5" fill="#75C7FF" /><circle cx="143" cy="177" r="6" fill="#75C7FF" />
              <circle cx="226" cy="218" r="5" fill="#75C7FF" /><circle cx="317" cy="106" r="7" fill="#B7A6FF" />
              <circle cx="402" cy="170" r="5" fill="#75C7FF" /><circle cx="475" cy="115" r="6" fill="#75C7FF" />
              <circle cx="173" cy="281" r="4" fill="#75C7FF" /><circle cx="238" cy="218" r="4" fill="#75C7FF" />
              <circle cx="303" cy="290" r="4" fill="#75C7FF" /><circle cx="402" cy="170" r="20" stroke="#75C7FF" strokeOpacity=".2" />
              <circle cx="317" cy="106" r="25" stroke="#B7A6FF" strokeOpacity=".28" />
              <defs><linearGradient id="line" x1="50" y1="100" x2="475" y2="290" gradientUnits="userSpaceOnUse"><stop stopColor="#6CD8E8" stopOpacity=".18" /><stop offset=".55" stopColor="#8EA9FF" stopOpacity=".8" /><stop offset="1" stopColor="#6CD8E8" stopOpacity=".3" /></linearGradient></defs>
            </svg>
            <div className="visual-label"><span className="visual-pulse" /> Network visibility <span>ACTIVE</span></div>
          </div>

          <p className="login-brand-footer">Built for focused, informed security operations.</p>
        </section>

        <main className="auth-card">
          <div className="auth-card-heading">
            <p className="eyebrow">Welcome back</p>
            <h2>Sign in to your workspace</h2>
            <p>Enter your credentials to continue to the security console.</p>
          </div>

          <form className="auth-form" onSubmit={handleLogin}>
            <label htmlFor="login-email">Email or username</label>
            <input id="login-email" value={email} onChange={(event) => setEmail(event.target.value)} type="text" autoComplete="username" placeholder="you@organization.com" required />

            <label htmlFor="login-password">Password</label>
            <input id="login-password" value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" placeholder="Enter your password" required />

            {error ? <p className="error-text" role="alert">{error}</p> : null}
            <button type="submit" disabled={submitting}>
              {submitting ? <><span className="button-spinner" /> Signing in...</> : 'Sign in securely'}
            </button>
          </form>

          <div className="auth-security-note">
            <svg viewBox="0 0 20 20" fill="none" aria-hidden="true"><path d="M10 2.5 16 5v4.1c0 3.4-2.3 5.9-6 7.2-3.7-1.3-6-3.8-6-7.2V5l6-2.5Z" stroke="currentColor" strokeWidth="1.4" /><path d="m7.5 9.7 1.7 1.7 3.4-3.7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" /></svg>
            Your session is protected with secure authentication.
          </div>
          <div className="auth-system-status"><span /> All systems operational</div>
        </main>
      </div>
    );
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="brand-kicker">AI-NTDRS</p>
          <h1>Security Operations Center</h1>
        </div>
        <nav aria-label="Primary navigation" className="nav-list">
          {navigation.map((item) => (
            <button
              key={item.key}
              type="button"
              className={view === item.key ? 'active' : ''}
              onClick={() => setView(item.key)}
            >
              {item.label}
            </button>
          ))}
        </nav>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Good morning, {user.full_name ?? user.email}</p>
            <h2>Security Overview</h2>
            <p className="muted-text">Last updated: just now</p>
          </div>
          <div className="topbar-actions">
            <button type="button" onClick={() => setView('search')}>Search</button>
            <button type="button" className="notification-button" onClick={() => setNotificationsOpen((value) => !value)}>
              Notifications
              {notifications.length > 0 ? <span className="notification-badge">{notifications.length}</span> : null}
            </button>
            <button type="button" onClick={() => void loadWorkspace()}>Refresh</button>
            <button type="button" onClick={handleLogout}>Logout</button>
          </div>
        </header>

        {notificationsOpen ? (
          <section className="panel notification-panel">
            <div className="notification-header">
              <div>
                <p className="eyebrow">Notification Center</p>
                <h3>Recent security events</h3>
              </div>
              <button type="button" onClick={() => setNotificationsOpen(false)}>Close</button>
            </div>

            {notifications.length > 0 ? (
              <ul className="notification-list">
                {notifications.map((notification) => (
                  <li key={`${notification.title}-${notification.body}`}>
                    <strong>{notification.title}</strong>
                    <p className="muted-text">{notification.body}</p>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="muted-text">No active notifications.</p>
            )}
          </section>
        ) : null}

        {view === 'search' ? (
          <section className="page-stack">
            <div className="panel">
              <p className="eyebrow">Global Search</p>
              <h3>Search across devices, alerts, incidents, reports, and audit logs</h3>
              <p className="muted-text">This workspace searches the currently loaded security records across all major entity types.</p>
              <div className="filter-bar">
                <label>
                  Search all records
                  <input
                    value={globalSearch}
                    onChange={(event) => setGlobalSearch(event.target.value)}
                    placeholder="Device, alert, incident, report, or audit log"
                  />
                </label>
                <button type="button" onClick={() => setGlobalSearch('')}>Clear</button>
              </div>
            </div>

            {globalSearchQuery ? (
              <div className="content-grid">
                <article className="panel table-panel">
                  <p className="eyebrow">Devices</p>
                  <TableFrame emptyMessage="No device matches found.">
                    <SimpleTable
                      headers={['Device', 'IP', 'Risk']}
                      rows={globalDeviceResults.map((device) => [device.device_identifier, device.ip_address, String(device.risk_score)])}
                    />
                  </TableFrame>
                </article>

                <article className="panel table-panel">
                  <p className="eyebrow">Alerts</p>
                  <TableFrame emptyMessage="No alert matches found.">
                    <SimpleTable
                      headers={['Alert', 'Severity', 'Status']}
                      rows={globalAlertResults.map((alert) => [alert.alert_id, alert.severity, alert.status])}
                    />
                  </TableFrame>
                </article>
              </div>
            ) : null}

            {globalSearchQuery ? (
              <div className="content-grid">
                <article className="panel table-panel">
                  <p className="eyebrow">Incidents</p>
                  <TableFrame emptyMessage="No incident matches found.">
                    <SimpleTable
                      headers={['Incident', 'Title', 'Status']}
                      rows={globalIncidentResults.map((incident) => [incident.incident_code, incident.title, incident.status])}
                    />
                  </TableFrame>
                </article>

                <article className="panel table-panel">
                  <p className="eyebrow">Reports and Audit Logs</p>
                  <div className="search-stack">
                    <div>
                      <h4>Reports</h4>
                      <TableFrame emptyMessage="No report matches found.">
                        <SimpleTable
                          headers={['Report', 'Format']}
                          rows={globalReportResults.map((report) => [report.report_title, report.export_format])}
                        />
                      </TableFrame>
                    </div>
                    <div>
                      <h4>Audit Logs</h4>
                      <TableFrame emptyMessage="No audit log matches found.">
                        <SimpleTable
                          headers={['Action', 'Resource', 'Result']}
                          rows={globalAuditResults.map((entry) => [entry.action, entry.resource, entry.result])}
                        />
                      </TableFrame>
                    </div>
                  </div>
                </article>
              </div>
            ) : (
              <article className="panel">
                <p className="muted-text">Enter a search term to look across all loaded security records.</p>
              </article>
            )}
          </section>
        ) : null}

        {view === 'dashboard' ? (
          <>
            <section className="metrics-grid" aria-label="Security overview metrics">
              <article className="metric-card">
                <span>Monitored Devices</span>
                <strong>{summary.total_monitored_devices}</strong>
              </article>
              <article className="metric-card">
                <span>Active Devices</span>
                <strong>{summary.active_devices}</strong>
              </article>
              <article className="metric-card">
                <span>Threats Detected Today</span>
                <strong>{summary.threats_detected_today}</strong>
              </article>
              <article className="metric-card">
                <span>Critical Alerts</span>
                <strong>{summary.critical_alerts}</strong>
              </article>
            </section>

            <section className="content-grid">
              <article className="panel">
                <p className="eyebrow">Current Risk</p>
                <h3>{summary.current_risk_level}</h3>
                <p className="muted-text">The dashboard is connected to the backend API and showing live summary data.</p>
              </article>

              <article className="panel">
                <p className="eyebrow">Network Flow Analysis</p>
                <h3>{summary.network_flows_analyzed.toLocaleString()}</h3>
                <p className="muted-text">Analyzed flows from the monitoring pipeline.</p>
              </article>
            </section>

            <section className="content-grid">
              <article className="panel table-panel">
                <p className="eyebrow">Recent Alerts</p>
                <TableFrame emptyMessage="No alerts have been generated yet.">
                  <SimpleTable
                    headers={["Alert", "Severity", "Risk", "Status"]}
                    rows={recentAlerts.map((alert) => [alert.alert_id, alert.severity, String(alert.risk_score), alert.status])}
                  />
                </TableFrame>
              </article>

              <article className="panel table-panel">
                <p className="eyebrow">Suspicious Devices</p>
                <TableFrame emptyMessage="No devices available.">
                  <SimpleTable
                    headers={["Device", "IP", "Risk", "Alerts"]}
                    rows={recentDevices.map((device) => [device.device_identifier, device.ip_address, String(device.risk_score), String(device.alert_count)])}
                  />
                </TableFrame>
              </article>
            </section>
          </>
        ) : null}

        {view === 'devices' ? (
          <EntityPage title="Device Inventory" subtitle="Authorized endpoints currently tracked by the system.">
            <div className="panel filter-panel">
              <div className="filter-bar">
                <label>
                  Search devices
                  <input
                    value={deviceSearch}
                    onChange={(event) => setDeviceSearch(event.target.value)}
                    placeholder="Device, IP, hostname, or status"
                  />
                </label>
                <button type="button" onClick={() => setDeviceSearch('')}>Clear</button>
              </div>
            </div>
            <TableFrame emptyMessage="No devices available.">
              <SimpleTable
                headers={["Device", "IP Address", "Type", "Status", "Risk", "Alerts"]}
                rows={filteredDevices.map((device) => [device.device_identifier, device.ip_address, device.device_type, device.status, String(device.risk_score), String(device.alert_count)])}
                rowKeys={filteredDevices.map((device) => device.id)}
                onRowClick={(rowIndex) => setSelectedDeviceId(filteredDevices[rowIndex]?.id ?? null)}
              />
            </TableFrame>

            <section className="content-grid">
              <article className="panel">
                <p className="eyebrow">Investigation</p>
                {selectedDevice ? (
                  <div className="detail-grid">
                    <DetailItem label="Device" value={selectedDevice.device_identifier} />
                    <DetailItem label="IP Address" value={selectedDevice.ip_address} />
                    <DetailItem label="Hostname" value={selectedDevice.hostname ?? 'Unknown'} />
                    <DetailItem label="Type" value={selectedDevice.device_type} />
                    <DetailItem label="Status" value={selectedDevice.status} />
                    <DetailItem label="Risk" value={String(selectedDevice.risk_score)} />
                    <DetailItem label="Alerts" value={String(selectedDevice.alert_count)} />
                    <DetailItem label="Activity" value={selectedDevice.activity_level} />
                  </div>
                ) : (
                  <p className="muted-text">Select a device to inspect its security context.</p>
                )}
              </article>

              <article className="panel">
                <p className="eyebrow">Recommended Action</p>
                <h3>{selectedDevice?.risk_score && selectedDevice.risk_score >= 75 ? 'Escalate and investigate immediately' : 'Continue monitoring and review activity patterns'}</h3>
                <p className="muted-text">This summary is derived from the currently selected device and its stored risk profile.</p>
              </article>
            </section>
          </EntityPage>
        ) : null}

        {view === 'alerts' ? (
          <EntityPage title="Alert Management" subtitle="Security alerts generated by the detection pipeline.">
            <div className="panel filter-panel">
              <div className="filter-grid">
                <label>
                  Search alerts
                  <input
                    value={alertSearch}
                    onChange={(event) => setAlertSearch(event.target.value)}
                    placeholder="Alert ID, threat, IP, status"
                  />
                </label>
                <label>
                  Severity
                  <select value={alertSeverity} onChange={(event) => setAlertSeverity(event.target.value)}>
                    <option value="ALL">All severities</option>
                    <option value="LOW">LOW</option>
                    <option value="MODERATE">MODERATE</option>
                    <option value="HIGH">HIGH</option>
                    <option value="CRITICAL">CRITICAL</option>
                  </select>
                </label>
                <label>
                  Status
                  <select value={alertStatus} onChange={(event) => setAlertStatus(event.target.value)}>
                    <option value="ALL">All statuses</option>
                    <option value="NEW">NEW</option>
                    <option value="INVESTIGATING">INVESTIGATING</option>
                    <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="FALSE POSITIVE">FALSE POSITIVE</option>
                  </select>
                </label>
                <button type="button" onClick={() => {
                  setAlertSearch('');
                  setAlertSeverity('ALL');
                  setAlertStatus('ALL');
                }}>
                  Clear
                </button>
              </div>
            </div>
            <TableFrame emptyMessage="No alerts available.">
              <SimpleTable
                headers={["Alert", "Severity", "Threat", "Risk", "Status"]}
                rows={filteredAlerts.map((alert) => [alert.alert_id, alert.severity, alert.threat_category, String(alert.risk_score), alert.status])}
                rowKeys={filteredAlerts.map((alert) => alert.id)}
                onRowClick={(rowIndex) => setSelectedAlertId(filteredAlerts[rowIndex]?.id ?? null)}
              />
            </TableFrame>

            <section className="content-grid">
              <article className="panel">
                <p className="eyebrow">Alert Investigation</p>
                {selectedAlert ? (
                  <div className="detail-grid">
                    <DetailItem label="Alert ID" value={selectedAlert.alert_id} />
                    <DetailItem label="Severity" value={selectedAlert.severity} />
                    <DetailItem label="Threat" value={selectedAlert.threat_category} />
                    <DetailItem label="Risk" value={String(selectedAlert.risk_score)} />
                    <DetailItem label="Status" value={selectedAlert.status} />
                    <DetailItem label="Source" value={selectedAlert.source_ip} />
                    <DetailItem label="Destination" value={selectedAlert.destination_ip} />
                    <DetailItem label="Confidence" value={selectedAlert.model_confidence ? `${Math.round(selectedAlert.model_confidence * 100)}%` : 'Unknown'} />
                  </div>
                ) : (
                  <p className="muted-text">Select an alert to inspect the detection context.</p>
                )}
              </article>

              <article className="panel">
                <p className="eyebrow">Recommended Action</p>
                <h3>{selectedAlert?.recommended_action ?? 'Investigate device activity and verify whether the behavior is authorized.'}</h3>
                <p className="muted-text">The recommendation is shown separately from the AI prediction and the evidence that triggered it.</p>
              </article>
            </section>
          </EntityPage>
        ) : null}

        {view === 'incidents' ? (
          <EntityPage title="Incident Tracking" subtitle="Security incidents assembled from related alerts.">
            <div className="panel filter-panel">
              <div className="filter-grid">
                <label>
                  Search incidents
                  <input
                    value={incidentSearch}
                    onChange={(event) => setIncidentSearch(event.target.value)}
                    placeholder="Incident code, title, or summary"
                  />
                </label>
                <label>
                  Status
                  <select value={incidentStatus} onChange={(event) => setIncidentStatus(event.target.value)}>
                    <option value="ALL">All statuses</option>
                    <option value="NEW">NEW</option>
                    <option value="INVESTIGATING">INVESTIGATING</option>
                    <option value="ACKNOWLEDGED">ACKNOWLEDGED</option>
                    <option value="RESOLVED">RESOLVED</option>
                    <option value="FALSE POSITIVE">FALSE POSITIVE</option>
                  </select>
                </label>
                <button type="button" onClick={() => {
                  setIncidentSearch('');
                  setIncidentStatus('ALL');
                }}>
                  Clear
                </button>
              </div>
            </div>
            <TableFrame emptyMessage="No incidents available.">
              <SimpleTable
                headers={["Incident", "Title", "Status", "Opened", "Updated"]}
                rows={filteredIncidents.map((incident) => [incident.incident_code, incident.title, incident.status, incident.opened_at, incident.last_activity_at])}
                rowKeys={filteredIncidents.map((incident) => incident.id)}
                onRowClick={(rowIndex) => setSelectedIncidentId(filteredIncidents[rowIndex]?.id ?? null)}
              />
            </TableFrame>

            <section className="content-grid">
              <article className="panel">
                <p className="eyebrow">Incident Investigation</p>
                {selectedIncident ? (
                  <div className="detail-grid">
                    <DetailItem label="Incident" value={selectedIncident.incident_code} />
                    <DetailItem label="Title" value={selectedIncident.title} />
                    <DetailItem label="Status" value={selectedIncident.status} />
                    <DetailItem label="Opened" value={selectedIncident.opened_at} />
                    <DetailItem label="Updated" value={selectedIncident.last_activity_at} />
                    <DetailItem label="Summary" value={selectedIncident.summary ?? 'No summary available'} />
                  </div>
                ) : (
                  <p className="muted-text">Select an incident to review its current state.</p>
                )}
              </article>

              <article className="panel">
                <p className="eyebrow">Recommended Action</p>
                <h3>{selectedIncident?.status === 'NEW' ? 'Assign an analyst and review linked alerts' : 'Continue incident handling and update notes'}</h3>
                <p className="muted-text">The incident panel is intentionally simple and grounded in the stored case record.</p>
              </article>
            </section>
          </EntityPage>
        ) : null}

        {view === 'reports' ? (
          <EntityPage title="Reports" subtitle="Incident reports available for export and review.">
            <div className="panel filter-panel">
              <div className="filter-bar">
                <label>
                  Search reports
                  <input
                    value={reportSearch}
                    onChange={(event) => setReportSearch(event.target.value)}
                    placeholder="Report title, incident ID, or format"
                  />
                </label>
                <button type="button" onClick={() => setReportSearch('')}>Clear</button>
              </div>
            </div>
            <TableFrame emptyMessage="No reports available.">
              <SimpleTable
                headers={["Report", "Incident", "Format", "Path"]}
                rows={filteredReports.map((report) => [report.report_title, String(report.incident_id ?? '-'), report.export_format, report.file_path ?? '-'])}
              />
            </TableFrame>
          </EntityPage>
        ) : null}

        {view === 'audit-logs' ? (
          <EntityPage title="Audit Logs" subtitle="Administrative actions recorded by the system.">
            <div className="panel filter-panel">
              <div className="filter-bar">
                <label>
                  Search audit logs
                  <input
                    value={auditSearch}
                    onChange={(event) => setAuditSearch(event.target.value)}
                    placeholder="Action, resource, result, or IP"
                  />
                </label>
                <button type="button" onClick={() => setAuditSearch('')}>Clear</button>
              </div>
            </div>
            <TableFrame emptyMessage="No audit logs available.">
              <SimpleTable
                headers={["Action", "Resource", "Result", "Time"]}
                rows={filteredAuditLogs.map((entry) => [entry.action, entry.resource, entry.result, entry.created_at])}
              />
            </TableFrame>
          </EntityPage>
        ) : null}

        {view === 'copilot' ? (
          <section className="page-stack">
            <div className="panel">
              <div className="copilot-heading-row">
                <div>
                  <p className="eyebrow">AI Security Assistant</p>
                  <h3>How can I help?</h3>
                  <p className="muted-text">Ask about an alert, incident, device, or next steps. Answers use your current SOC data.</p>
                </div>
                {copilotMessages.length > 0 ? <button type="button" className="copilot-clear" onClick={() => { setCopilotMessages([]); setCopilotResponse(null); }}>New conversation</button> : null}
              </div>
              <div className="copilot-mode" role="status">
                <span className={copilotResponse?.assistant_mode === 'local_model' ? 'mode-dot online' : 'mode-dot'} />
                {copilotResponse?.assistant_mode === 'local_model'
                  ? `Private local model · ${copilotResponse.model_name}`
                  : copilotResponse?.assistant_mode === 'fallback'
                    ? 'Local model unavailable · using built-in SOC guidance'
                    : 'Uses a local model when Ollama is running · built-in guidance remains available'}
              </div>

              <div className="copilot-chat" role="log" aria-label="Conversation" aria-live="polite">
                {copilotMessages.length === 0 ? (
                  <div className="copilot-welcome"><span className="copilot-avatar">AI</span><p>Hi, I’m your SOC assistant. Tell me what you’re looking into and I’ll help you make sense of it and suggest safe next steps.</p></div>
                ) : copilotMessages.map((message, index) => (
                  <div className={`copilot-message ${message.role}`} key={`${index}-${message.role}`}>
                    {message.role === 'assistant' ? <span className="copilot-avatar">AI</span> : null}
                    <p>{message.content}</p>
                  </div>
                ))}
                {copilotLoading ? <div className="copilot-message assistant"><span className="copilot-avatar">AI</span><p className="copilot-thinking"><span /><span /><span /> Thinking through the SOC context…</p></div> : null}
              </div>

              {copilotMessages.length === 0 ? (
                <div className="copilot-prompts" aria-label="Suggested questions">
                  {['What needs attention right now?', 'Help me investigate the highest-risk alert', 'What should I do about a suspected compromised account?'].map((prompt) => (
                    <button type="button" key={prompt} onClick={() => setCopilotQuery(prompt)}>{prompt}</button>
                  ))}
                </div>
              ) : null}

              <form className="copilot-composer" onSubmit={runCopilotQuery}>
                <label className="visually-hidden" htmlFor="copilot-question">Ask the SOC assistant</label>
                <input id="copilot-question" value={copilotQuery} onChange={(event) => setCopilotQuery(event.target.value)} placeholder="Describe the issue or ask a question..." autoComplete="off" />
                <button type="submit" disabled={copilotLoading || copilotQuery.trim().length < 3}>
                  {copilotLoading ? 'Thinking...' : 'Send'}
                </button>
              </form>
              {error ? <p className="error-text">{error}</p> : null}
            </div>

            {copilotResponse?.show_context ? <>
            <div className="content-grid">
              <article className="panel">
                <p className="eyebrow">Facts</p>
                <BulletList items={copilotResponse?.facts ?? []} emptyMessage="No facts available." />
              </article>
            </div>

            <div className="content-grid">
              <article className="panel">
                <p className="eyebrow">Predictions</p>
                <BulletList items={copilotResponse?.predictions ?? []} emptyMessage="No predictions available." />
              </article>

              <article className="panel">
                <p className="eyebrow">Recommendations</p>
                <BulletList items={copilotResponse?.recommendations ?? []} emptyMessage="No recommendations available." />
              </article>
            </div>

            <div className="content-grid">
              <article className="panel table-panel">
                <p className="eyebrow">Related Devices</p>
                <TableFrame emptyMessage="No related devices available.">
                  <SimpleTable
                    headers={["Device", "IP", "Risk", "Alerts", "Status"]}
                    rows={(copilotResponse?.related_devices ?? []).map((device) => [device.device_identifier, device.ip_address, String(device.risk_score), String(device.alert_count), device.status])}
                  />
                </TableFrame>
              </article>

              <article className="panel table-panel">
                <p className="eyebrow">Related Alerts</p>
                <TableFrame emptyMessage="No related alerts available.">
                  <SimpleTable
                    headers={["Alert", "Severity", "Threat", "Risk", "Status"]}
                    rows={(copilotResponse?.related_alerts ?? []).map((alert) => [alert.alert_id, alert.severity, alert.threat_category, String(alert.risk_score), alert.status])}
                  />
                </TableFrame>
              </article>
            </div>
            </> : null}
          </section>
        ) : null}
      </main>
    </div>
  );
}

function EntityPage({ title, subtitle, children }: { title: string; subtitle: string; children: React.ReactNode }) {
  return (
    <section className="page-stack">
      <div className="panel">
        <p className="eyebrow">Workspace</p>
        <h3>{title}</h3>
        <p className="muted-text">{subtitle}</p>
      </div>
      {children}
    </section>
  );
}

function TableFrame({ children, emptyMessage }: { children: React.ReactNode; emptyMessage: string }) {
  return <div className="table-frame">{children ?? <p className="muted-text">{emptyMessage}</p>}</div>;
}

function SimpleTable({ headers, rows, rowKeys, onRowClick }: { headers: string[]; rows: string[][]; rowKeys?: Array<string | number>; onRowClick?: (rowIndex: number) => void }) {
  if (rows.length === 0) {
    return <p className="muted-text">No records to display.</p>;
  }

  return (
    <table className="simple-table">
      <thead>
        <tr>
          {headers.map((header) => (
            <th key={header}>{header}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, rowIndex) => (
          <tr key={rowKeys?.[rowIndex] ?? rowIndex} className={onRowClick ? 'clickable-row' : ''} onClick={onRowClick ? () => onRowClick(rowIndex) : undefined}>
            {row.map((cell, cellIndex) => (
              <td key={`${rowIndex}-${cellIndex}`}>{cell}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function BulletList({ items, emptyMessage }: { items: string[]; emptyMessage: string }) {
  if (items.length === 0) {
    return <p className="muted-text">{emptyMessage}</p>;
  }

  return (
    <ul className="bullet-list">
      {items.map((item) => (
        <li key={item}>{item}</li>
      ))}
    </ul>
  );
}

function DetailItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="detail-item">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  );
}
