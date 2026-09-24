# Operations, security, and model limitations

## Authentication and roles

- Production startup rejects the development signing key, demo password/seeding, placeholder sensor key, SQLite, and loopback CORS origins. Generate independent random values for `SECRET_KEY`, `SENSOR_API_KEY`, `DEMO_ADMIN_PASSWORD`, and the database password, even though demo account seeding remains disabled.
- Production startup does not provision a demo account. Run `python -m app.cli.create_admin` in the backend container to create an administrator with an interactive, non-echoed password prompt.
- Access tokens carry a unique identifier. Logout revokes that token in the shared database; expired revocation rows are pruned on login.
- Viewers can read SOC data. Admins and Security Analysts can register devices, ingest manual flows, update alerts/incidents, add case notes, and request simulations. Audit-log reads and response-simulation approvals require Admin. An administrator other than the requester must approve or reject a request.
- Approved response actions are always stored as `SIMULATED`; the application does not change firewall, endpoint, or identity controls.

This does not yet include MFA, password reset, organization SSO, or automated login throttling. Add those before exposing accounts to the public internet.

## Database changes

Alembic is wired into backend startup, and the initial schema revision is under `backend/migrations/versions`. Add a new revision for every future schema change; do not edit a migration that has already been applied to a shared database. Back up production data before applying schema changes. The initial baseline is intended for this repository's first deployment; for an existing database, inspect it and back it up before adopting the migration version.

## Suricata ingestion

The backend accepts authenticated Suricata EVE flow events at `POST /api/telemetry/suricata/flow`. The forwarder in `backend/app/services/suricata_forwarder.py` reads `event_type=flow` JSONL events, retries temporary HTTP failures, and sends a stable event ID. The receipt table prevents duplicate processing when a sender retries. Register the internal device IP first; events for unknown assets are rejected. No packet payload is collected. Suricata flow events do not provide the application's failed-connection or request-frequency features, so the adapter marks those as zero; do not enable the demo classifier on this mapping without retraining and validation.

Use an independent, high-entropy sensor key per deployment, restrict sensor-to-API network paths, and use HTTPS off-host. A single shared key is the current sensor authentication design; per-sensor key rotation and identity are future work. Plan event-receipt retention for high-volume networks.

## Detection validity

The committed Random Forest and its validation report are generated from synthetic scenarios. The perfect validation scores reflect that synthetic generator and are not estimates of operational accuracy. Production refuses to enable a flow model unless `FLOW_MODEL_VALIDATED=true` is explicitly set; use `FLOW_MODEL_ENABLED=false` until operational evaluation is complete. The inference service reports no confidence until calibration is available; its Random Forest threat-vote score is explicitly uncalibrated. The heuristic risk score is a triage aid, not a probability of compromise.

Before using detections operationally, collect authorized, representative, labeled flow metadata; split evaluation by time, site, or device rather than random rows; report per-class precision/recall and false-positive/negative rates; tune thresholds with analysts; calibrate scores; and monitor drift. Keep the synthetic model in demo mode until this evaluation is complete.

## Deployment boundaries

Compose binds ports to loopback and is a local/demo stack. For a hosted SOC, terminate TLS at a maintained reverse proxy, restrict network access, set backups and restore drills, and monitor database health, ingestion lag, API failures, and model availability. The readiness route checks the database and reports whether a flow model loaded; Ollama can be unavailable and the Copilot will fall back to built-in guidance.
