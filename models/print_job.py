from pydantic import BaseModel, Field
from typing import Optional


class PrintJobLog(BaseModel):
    timestamp: float
    job_id: str
    user_id: str
    description: str


class PrintJob(BaseModel):
    job_id: str
    user_id: str
    cups_job_id: Optional[str] = None
    filename: str
    file: str
    color: bool = True
    copies: int = 1
    status: str
    logs: list[PrintJobLog] = Field(default_factory=list)
    created_at: float
    updated_at: float
