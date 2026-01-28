from fastapi import APIRouter, Request, BackgroundTasks
from decorators.signatures import valid_secure_key
from utils.printer import Printer
from tasks.proccess_printer_email import proccess_printer_email
import os
import base64


router = APIRouter(prefix="/webhooks", tags=["webhooks"])
printer = Printer()

@router.post("/email/cloudflare", status_code=200)
@valid_secure_key
async def email_webhook(request: Request, background_tasks: BackgroundTasks):
    request = await request.json()
    if request.get("to") == os.environ.get("PRINTER_EMAIL"):
        background_tasks.add_task(proccess_printer_email, request)
        
    return {"success": True}