# AI Network Threat Detection & Response System (AI-NTDRS)

AI-NTDRS is a security operations prototype for inventory, flow-based detections, alert and incident handling, audit records, and a locally hosted AI Copilot. It is intended for authorized environments. It is not yet a validated production IDS/SOAR platform.

## Capabilities

- FastAPI service with user authentication and role-gated analyst actions.
- React + TypeScript SOC interface for devices, alerts, incidents, reports, and Copilot.
- Flow risk scoring and a Random Forest demo artifact trained on synthetic scenarios.
- Authenticated Suricata EVE flow forwarding with idempotent event ingestion.
- Incident notes, case assignment/status updates, audit logging, and a two-person approval path for simulated response actions.
- Local Ollama Copilot integration. Conversation examples are not collected automatically for fine-tuning.

## Run locally with Docker Compose

1. Copy `.env.example` to `.env`.
2. Generate unique values for `SECRET_KEY`, `SENSOR_API_KEY`, and `POSTGRES_PASSWORD`. For example, in PowerShell:

   ```powershell
   python -c "import secrets; print(secrets.token_urlsafe(48))"
   ```

   Use a different generated value for each variable. Keep `.env` private; it is ignored by Git.
3. Start the stack:

   ```powershell
   docker compose up --build -d
   ```

4. Download the local chat model once:

   ```powershell
   docker compose exec ollama ollama pull qwen3.5:4b
   ```

5. Open <http://localhost:8080>. Development mode seeds a demo administrator and sample records. The default local demo login is `admin@ai-ntdrs.local` / `ChangeMe123!`; change these in `.env` for local use. The sign-in form does not prefill credentials.

The Compose ports bind to loopback for local use. The frontend proxies `/api` to the backend. Expose it beyond this computer only behind a TLS reverse proxy and with production settings.

## Production setup

Set `ENVIRONMENT=production`, `DEMO_SEED_ENABLED=false`, `FLOW_MODEL_ENABLED=false` until an operational model has been validated, a random `SECRET_KEY`, a random `SENSOR_API_KEY`, a unique database password, a non-demo `DEMO_ADMIN_PASSWORD`, and deployed origins. The application refuses to start with the development signing key, demo credentials/seeding, SQLite, placeholder sensor keys, local CORS origins, or an unvalidated model enabled.

Create the initial administrator interactively; the password is entered without echoing to the terminal:

```powershell
docker compose exec backend python -m app.cli.create_admin
```

Create additional analyst, viewer, or administrator accounts with `docker compose exec backend python -m app.cli.create_user`.

Startup applies versioned database migrations. Store credentials in a secret manager in hosted environments. Configure HTTPS, firewall rules, database backups, monitoring, and an incident-data retention policy at the deployment layer.

## Suricata flow ingestion

Onboard monitored devices through `POST /api/devices` as an Admin or Security Analyst. Configure Suricata to write EVE JSON to a local file, then run the included forwarder on the sensor host. It forwards only `event_type=flow`, uses a stable SHA-256 event key for retry-safe ingestion, and requires the same `SENSOR_API_KEY` configured on the backend:

```powershell
$env:SENSOR_API_KEY = "<your configured sensor key>"
python -m app.services.suricata_forwarder C:\Suricata\log\eve.json `
  --api-url https://soc.example.org/api/telemetry/suricata/flow `
  --sensor-id campus-edge-1 --follow
```

Use `--from-start` to replay an existing EVE log. The endpoint accepts registered devices only; it does not ingest packet payloads. Protect the sensor key and use HTTPS when sending to a remote server.

See [operations, security, and model limitations](docs/OPERATIONS_AND_SECURITY.md), [local Copilot setup](docs/LOCAL_AI_COPILOT.md), and [Copilot fine-tuning](ml/training/COPILOT_FINE_TUNING.md).
