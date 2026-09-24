"""Create a local AI-NTDRS user and assign an explicit role.

Run from the backend directory: ``python -m app.cli.create_user``.
"""
from getpass import getpass

from sqlalchemy.orm import Session

from app.auth.service import create_user, ensure_role, get_user_by_email
from app.core.config import validate_production_settings
from app.database.migrations import upgrade_database
from app.database.session import engine


def main() -> None:
    validate_production_settings()
    upgrade_database()
    email = input("User email: ").strip().lower()
    if not email or "@" not in email:
        raise SystemExit("Enter a valid email address")
    role_name = input("Role (Admin, Security Analyst, Viewer): ").strip()
    allowed_roles = {"Admin", "Security Analyst", "Viewer"}
    if role_name not in allowed_roles:
        raise SystemExit("Choose Admin, Security Analyst, or Viewer")
    password = getpass("New password (16+ characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 16:
        raise SystemExit("Password must contain at least 16 characters")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    with Session(engine) as db:
        if get_user_by_email(db, email):
            raise SystemExit("An account with that email already exists")
        ensure_role(db, role_name)
        create_user(db, email=email, password=password, full_name=None, role_names=[role_name])
    print(f"Created {role_name} account for {email}")


if __name__ == "__main__":
    main()
