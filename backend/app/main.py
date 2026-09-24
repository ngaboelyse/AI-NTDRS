from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sqlalchemy.orm import Session

from app.auth.service import create_user, ensure_role
from app.api.router import api_router
from app.core.config import settings, validate_production_settings
from app.database.migrations import upgrade_database
from app.database.session import engine
from app.models.role import Role
from app.models.user import User
from app.services.demo_seed import seed_demo_data
from app.services.model_inference import get_inference_service

app = FastAPI(
    title="AI-NTDRS API",
    version="0.1.0",
    description="Backend API for the AI Network Threat Detection & Response System",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")


@app.on_event("startup")
def startup_event() -> None:
    if settings.environment == "test":
        return

    validate_production_settings()

    upgrade_database()
    with Session(engine) as db:
        admin_role = ensure_role(db, "Admin", "Full access administrator")
        ensure_role(db, "Security Analyst", "Security investigation and alert handling")
        ensure_role(db, "Viewer", "Read-only dashboard access")

        if settings.demo_seed_enabled:
            admin_user = db.query(User).filter(User.email == settings.demo_admin_email).one_or_none()
            if admin_user is None:
                create_user(
                    db,
                    email=settings.demo_admin_email,
                    password=settings.demo_admin_password,
                    full_name="Demo Administrator",
                    role_names=[admin_role.name],
                )

            seed_demo_data(db)

    # Only load a flow model when an operator explicitly enables it. Production
    # requires a separate validation acknowledgement for non-demo artifacts.
    if settings.flow_model_enabled:
        get_inference_service().load_models()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": settings.app_name,
        "status": "running",
    }
