from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy import inspect

from app.database.session import engine
from app.models.incident_note import IncidentNote
from app.models.response_action_request import ResponseActionRequest
from app.models.revoked_token import RevokedToken
from app.models.sensor_event_receipt import SensorEventReceipt
from app.models.base import Base
import app.models  # noqa: F401 - register the existing application tables

INITIAL_REVISION = "6a204ea472ba"
LEGACY_CORE_TABLES = {"users", "roles", "devices", "network_flows", "alerts", "incidents"}


def upgrade_database() -> None:
    backend_dir = Path(__file__).resolve().parents[2]
    config = Config(str(backend_dir / "alembic.ini"))
    config.set_main_option("script_location", str(backend_dir / "migrations"))
    table_names = set(inspect(engine).get_table_names())
    if "alembic_version" not in table_names:
        if table_names and not LEGACY_CORE_TABLES.issubset(table_names):
            raise RuntimeError("Found an unversioned database with an unknown schema; back it up and migrate it deliberately")
        if table_names:
            # Adopt the schema created by earlier AI-NTDRS versions without
            # rerunning the initial CREATE TABLE operations over existing data.
            Base.metadata.create_all(bind=engine, tables=[
                IncidentNote.__table__,
                ResponseActionRequest.__table__,
                RevokedToken.__table__,
                SensorEventReceipt.__table__,
            ], checkfirst=True)
            command.stamp(config, INITIAL_REVISION)
    command.upgrade(config, "head")
