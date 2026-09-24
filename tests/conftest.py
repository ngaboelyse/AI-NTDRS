from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.auth.dependencies import get_current_user
from app.database.session import get_db
from app.main import app
from app.core.config import settings
from app.models.base import Base
from app.models.device import Device
from app.models.role import Role
from app.models.user import User
from app.auth.passwords import hash_password


@pytest.fixture()
def engine():
    test_engine = create_engine(
        'sqlite+pysqlite://',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    return test_engine


@pytest.fixture()
def session_factory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture()
def db_session(session_factory) -> Generator[Session, None, None]:
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session: Session, session_factory) -> Generator[TestClient, None, None]:
    settings.environment = 'test'

    def override_get_db():
        yield db_session

    def override_current_user():
        user = db_session.query(User).first()
        if user is None:
            role = Role(name='Admin', description='Administrator')
            db_session.add(role)
            db_session.flush()
            user = User(
                email='admin@ai-ntdrs.local',
                password_hash=hash_password('ChangeMe123!'),
                full_name='Demo Admin',
                is_active=True,
            )
            user.roles.append(role)
            db_session.add(user)
            db_session.commit()
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_current_user

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture()
def seed_user(db_session: Session) -> User:
    role = Role(name='Admin', description='Administrator')
    user = User(
        email='admin@ai-ntdrs.local',
        password_hash=hash_password('ChangeMe123!'),
        full_name='Demo Admin',
        is_active=True,
    )
    user.roles.append(role)
    db_session.add_all([role, user])
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def seed_device(db_session: Session) -> Device:
    device = Device(
        device_identifier='PC-025',
        ip_address='192.168.1.25',
        hostname='pc-025.university.local',
        device_type='Workstation',
        activity_level='normal',
        risk_score=0.0,
        alert_count=0,
        status='online',
    )
    db_session.add(device)
    db_session.commit()
    db_session.refresh(device)
    return device
