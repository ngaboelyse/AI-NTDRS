# AI-NTDRS REST API Overview

This document summarizes the currently implemented backend API surface for AI-NTDRS.

## Authentication

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`

## Dashboard

- `GET /api/dashboard/summary`

## Devices

- `GET /api/devices`
- `GET /api/devices/{id}`

## Alerts

- `GET /api/alerts`
- `GET /api/alerts/{id}`

## Flows

- `GET /api/flows`
- `POST /api/flows`

## Incidents

- `GET /api/incidents`
- `GET /api/incidents/{id}`

## Reports

- `GET /api/reports`
- `GET /api/reports/{id}`

## Audit Logs

- `GET /api/audit-logs`
- `GET /api/audit-logs/{id}`

## AI Security Copilot

- `POST /api/copilot/query`

## Notes

- All protected endpoints require a bearer token.
- The login endpoint accepts form-encoded credentials.
- The copilot endpoint returns grounded summaries from the actual database state rather than free-form generated claims.
- Flow ingestion is safe by default and uses heuristic risk scoring until the final ML model selection and training workflow is completed.
