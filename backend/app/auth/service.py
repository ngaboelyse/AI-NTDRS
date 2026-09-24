from collections.abc import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.passwords import hash_password, verify_password
from app.models.role import Role
from app.models.user import User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(User.email == email))


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def ensure_role(db: Session, role_name: str, description: str | None = None) -> Role:
    role = db.scalar(select(Role).where(Role.name == role_name))
    if role is not None:
        return role

    role = Role(name=role_name, description=description)
    db.add(role)
    db.commit()
    db.refresh(role)
    return role


def create_user(
    db: Session,
    *,
    email: str,
    password: str,
    full_name: str | None = None,
    role_names: Iterable[str] = (),
) -> User:
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        is_active=True,
    )
    user.roles = [ensure_role(db, role_name) for role_name in role_names]
    db.add(user)
    db.commit()
    db.refresh(user)
    return user