"""Forward Suricata EVE JSONL flow events to the authenticated AI-NTDRS API."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx


def stable_event_id(event: dict) -> str:
    event_data = json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(event_data.encode("utf-8")).hexdigest()


def forward_file(eve_file: Path, api_url: str, sensor_id: str, sensor_key: str, *, follow: bool, from_start: bool) -> None:
    parsed = urlparse(api_url)
    if parsed.scheme != "https" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
        raise SystemExit("Use HTTPS when forwarding sensor data to a non-local API")
    if len(sensor_key) < 32:
        raise SystemExit("Set SENSOR_API_KEY to a random secret of at least 32 characters")
    if not eve_file.is_file():
        raise SystemExit(f"EVE log not found: {eve_file}")

    with httpx.Client(timeout=15) as client, eve_file.open("r", encoding="utf-8") as stream:
        if not from_start:
            stream.seek(0, 2)
        while True:
            line = stream.readline()
            if not line:
                if follow:
                    time.sleep(0.5)
                    continue
                break
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                print("Skipping malformed EVE JSON line")
                continue
            if event.get("event_type") != "flow":
                continue

            event_id = stable_event_id(event)
            headers = {
                "X-Sensor-Key": sensor_key,
                "X-Sensor-ID": sensor_id,
                "X-Event-ID": event_id,
            }
            for attempt in range(5):
                try:
                    response = client.post(api_url, json=event, headers=headers)
                    if response.status_code == 409:
                        print(f"Event {event_id[:12]} was already recorded")
                        break
                    if response.status_code >= 500 or response.status_code == 429:
                        if attempt < 4:
                            time.sleep(min(2 ** attempt, 10))
                            continue
                    if 400 <= response.status_code < 500:
                        print(f"Sensor event rejected ({response.status_code}): {response.text[:300]}")
                        break
                    response.raise_for_status()
                    print(f"Forwarded event {event_id[:12]}: HTTP {response.status_code}")
                    break
                except httpx.HTTPError as exc:
                    if attempt == 4:
                        print(f"Could not forward event {event_id[:12]} after 5 attempts: {exc}")
                    else:
                        time.sleep(min(2 ** attempt, 10))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("eve_file", type=Path, help="Path to Suricata eve.json")
    parser.add_argument("--api-url", default="http://127.0.0.1:8000/api/telemetry/suricata/flow")
    parser.add_argument("--sensor-id", default="suricata-edge-1")
    parser.add_argument("--follow", action="store_true", help="Continue tailing the file as new events arrive")
    parser.add_argument("--from-start", action="store_true", help="Replay existing events; duplicates are safely ignored")
    args = parser.parse_args()
    forward_file(
        args.eve_file,
        args.api_url,
        args.sensor_id,
        os.environ.get("SENSOR_API_KEY", ""),
        follow=args.follow,
        from_start=args.from_start,
    )


if __name__ == "__main__":
    main()
