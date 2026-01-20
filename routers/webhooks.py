from fastapi import APIRouter, Request
from decorators.signatures import verify_signature

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

@router.post("/email/cloudflare", status_code=200)
@verify_signature
async def email_webhook(request: Request):
    
    print(request.json())
    # do something with email, preferably using background task 
    return {"success": True}