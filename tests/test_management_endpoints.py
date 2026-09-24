from datetime import datetime, timezone

from app.models.audit_log import AuditLog
from app.models.incident import Incident
from app.models.report import Report


def test_incidents_reports_and_audit_logs(client, seed_user, db_session):
    incident = Incident(
        incident_code='INC-1042',
        title='Multiple suspicious activities',
        status='INVESTIGATING',
        summary='Demo incident for regression coverage',
        assigned_analyst_id=seed_user.id,
        opened_at=datetime.now(timezone.utc),
        last_activity_at=datetime.now(timezone.utc),
        resolved_at=None,
    )
    db_session.add(incident)
    db_session.flush()

    report = Report(
        report_title='Incident Report INC-1042',
        incident_id=incident.id,
        generated_by_user_id=seed_user.id,
        export_format='pdf',
        file_path='/reports/inc-1042.pdf',
    )
    audit_log = AuditLog(
        user_id=seed_user.id,
        action='Alert acknowledged',
        resource='ALT-TEST-001',
        result='SUCCESS',
        event_metadata={'source': 'test'},
        ip_address='127.0.0.1',
    )
    db_session.add_all([report, audit_log])
    db_session.commit()

    incidents_response = client.get('/api/incidents')
    reports_response = client.get('/api/reports')
    audit_logs_response = client.get('/api/audit-logs')

    assert incidents_response.status_code == 200
    assert incidents_response.json()[0]['incident_code'] == 'INC-1042'

    assert reports_response.status_code == 200
    assert reports_response.json()[0]['report_title'] == 'Incident Report INC-1042'

    assert audit_logs_response.status_code == 200
    assert audit_logs_response.json()[0]['action'] == 'Alert acknowledged'
