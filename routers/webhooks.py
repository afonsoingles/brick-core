from fastapi import APIRouter, Request
from decorators.signatures import valid_secure_key

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/email/cloudflare", status_code=200)
@valid_secure_key
async def email_webhook(request: Request):
    req = await request.json()
    print(req)
    return {"success": True}