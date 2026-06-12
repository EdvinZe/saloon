from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class AdminAuthResponse(BaseModel):
    authenticated: bool
    role: str | None = None
    username: str | None = None
