from fastapi import APIRouter, Request
from decorators.signatures import valid_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/email/cloudflare", status_code=200)
@valid_signature
async def email_webhook(request: Request):
    req = await request.json()
    print(req)
    return {"success": True}