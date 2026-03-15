from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


class UserPrinterSettings(BaseModel):
    credits: float = 0
    no_credits_action: str = "require_approval"


class UserPermissions(BaseModel):
    manage_printer: bool = False
    manage_users: bool = False


class SafeUser(BaseModel):
    """User with personal/sensitive information redacted (no password)."""

    id: str
    name: str
    email: str
    auth_methods: list[str] = Field(default_factory=list)
    region: str
    language: str
    superadmin: bool = False
    admin: bool = False
    printer: UserPrinterSettings = Field(default_factory=UserPrinterSettings)
    permissions: UserPermissions = Field(default_factory=UserPermissions)
    suspended: bool = False
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _coerce_permissions(cls, data):
        # Backward compatibility: existing users stored permissions as a list.
        # Discard the list and use default UserPermissions values instead.
        if isinstance(data, dict) and isinstance(data.get("permissions"), list):
            data = dict(data)
            data["permissions"] = UserPermissions()
        return data


class User(SafeUser):
    """Full user model including the hashed password."""

    password: Optional[str] = None
