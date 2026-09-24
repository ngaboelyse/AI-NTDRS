"""Create the first production administrator without a default password.

Run from the backend directory with an administrator-controlled environment:
``python -m app.cli.create_admin``.
"""
from __future__ import annotations

from getpass import getpass

from sqlalchemy.orm import Session

from app.auth.service import create_user, ensure_role, get_user_by_email
from app.core.config import validate_production_settings
from app.database.migrations import upgrade_database
from app.database.session import engine


def main() -> None:
    validate_production_settings()
    upgrade_database()
    email = input("Administrator email: ").strip().lower()
    if not email or "@" not in email:
        raise SystemExit("Enter a valid administrator email address")
    password = getpass("New password (16+ characters): ")
    confirmation = getpass("Confirm password: ")
    if len(password) < 16:
        raise SystemExit("Password must contain at least 16 characters")
    if password != confirmation:
        raise SystemExit("Passwords do not match")

    with Session(engine) as db:
        if get_user_by_email(db, email):
            raise SystemExit("An account with that email already exists")
        admin_role = ensure_role(db, "Admin", "Full access administrator")
        create_user(db, email=email, password=password, full_name="Administrator", role_names=[admin_role.name])
    print(f"Created administrator account for {email}")


if __name__ == "__main__":
    main()
