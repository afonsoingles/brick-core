from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime
import hashlib


class PrintJobLog(BaseModel):
    id: str
    timestamp: datetime
    actor: str  # "system" or a user id
    type: str   # e.g. "job_created", "job_accepted", "job_rejected"
    description: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def _coerce_old_format(cls, data):
        # Backward compatibility: old logs had {timestamp, job_id, user_id, description}.
        if isinstance(data, dict) and "job_id" in data and "id" not in data:
            data = dict(data)
            raw = f"{data.get('job_id', '')}{data.get('timestamp', '')}"
            data["id"] = hashlib.md5(raw.encode()).hexdigest()
            data["actor"] = data.pop("user_id", "system")
            data["type"] = "legacy"
            data.pop("job_id", None)
        return data


class PrintJob(BaseModel):
    id: str
    user_id: str
    cups_job_id: Optional[str] = None
    filename: str
    file: str
    color: bool = True
    copies: int = 1
    status: str
    logs: list[PrintJobLog] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="before")
    @classmethod
    def _coerce_old_format(cls, data):
        # Backward compatibility: old documents stored the job identifier as "job_id".
        if isinstance(data, dict) and "job_id" in data and "id" not in data:
            data = dict(data)
            data["id"] = data.pop("job_id")
        return data

    def to_safe(self) -> "SafePrintJob":
        return SafePrintJob.model_validate(self.model_dump())


class SafePrintJob(BaseModel):
    """PrintJob with internal/sensitive fields redacted (no cups_job_id, no file path)."""

    id: str
    user_id: str
    filename: str
    color: bool = True
    copies: int = 1
    status: str
    logs: list[PrintJobLog] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
