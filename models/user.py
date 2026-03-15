from pydantic import BaseModel, Field
from typing import Optional


class UserPrinterSettings(BaseModel):
    credits: float = 0
    no_credits_action: str = "require_approval"


class User(BaseModel):
    id: str
    name: str
    email: str
    password: Optional[str] = None
    auth_methods: list[str] = Field(default_factory=list)
    region: str
    language: str
    superadmin: bool = False
    admin: bool = False
    printer: UserPrinterSettings = Field(default_factory=UserPrinterSettings)
    permissions: list[str] = Field(default_factory=list)
    suspended: bool = False
    created_at: float
    updated_at: float
