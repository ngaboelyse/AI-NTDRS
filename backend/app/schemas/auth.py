from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., description="Administrator email address or local username")
    password: str = Field(..., min_length=8)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    status: str
    user: str


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    is_active: bool
    roles: list[str] = Field(default_factory=list)
