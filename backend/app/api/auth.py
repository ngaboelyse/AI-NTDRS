from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user, require_role, security_scheme
from app.auth.service import authenticate_user
from app.auth.tokens import JWT_ALGORITHM, create_access_token
from app.core.config import settings
from app.database.session import get_db
from app.models.revoked_token import RevokedToken
from app.schemas.auth import LogoutResponse, TokenResponse, UserRead

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    db.execute(delete(RevokedToken).where(RevokedToken.expires_at < datetime.now(timezone.utc)))
    db.commit()

    token = create_access_token(subject=user.email)
    return TokenResponse(access_token=token)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    current_user = Depends(get_current_user),
    credentials=Depends(security_scheme),
    db: Session = Depends(get_db),
) -> LogoutResponse:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = jwt.decode(credentials.credentials, settings.secret_key, algorithms=[JWT_ALGORITHM])
    token_id = payload["jti"]
    db.add(RevokedToken(
        jti=token_id,
        expires_at=datetime.fromtimestamp(payload["exp"], timezone.utc),
        revoked_at=datetime.now(timezone.utc),
    ))
    db.commit()
    return LogoutResponse(status="logged_out", user=current_user.email)


@router.get("/me", response_model=UserRead)
def me(current_user = Depends(get_current_user)) -> UserRead:
    return UserRead(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        roles=[role.name for role in current_user.roles],
    )


@router.get("/admin-check")
def admin_check(current_user = Depends(require_role("Admin"))) -> dict[str, str]:
    return {"status": "ok", "user": current_user.email}
