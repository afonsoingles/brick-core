from fastapi import APIRouter, Request
from decorators.valid_json import valid_json
from decorators.auth import require_auth
from tools.users import UserTools
from tools.sessions import SessionsController
from tools.otp import LoginCodes
from utils.mailer import Mailer
import os

router = APIRouter(prefix="/v1/auth")

sessions_controller = SessionsController()
user_tools = UserTools()
login_codes = LoginCodes()
mailer = Mailer()


@router.post("/methods")
@valid_json(["email"])
async def get_auth_methods(request: Request):
    user = user_tools.get_user_by_email(request.state.json["email"])
    
    if user == "not_found":
        return {"success": False, "message": "User not found"}
    
    return {
        "success": True,
        "methods": user["auth_methods"]
    }

@router.post("/otp/send")
@valid_json(["email"])
async def send_otp(request: Request):

    user = user_tools.get_user_by_email(request.state.json["email"])

    if user == "not_found":
        return {"success": False, "message": "User not found"}

    if not "otp" in user["auth_methods"]:
        return {"success": False, "message": "OTP authentication is disabled."}
    
    rate_limited = login_codes._is_rate_limited(user["id"])
    if rate_limited:
        return {"success": False, "message": "Too many requests. Please try again later."}
    
    attempt_id, random_code = login_codes.generate_otp(user["id"])

    if user["language"] == "PT":
        subject = "O seu código de autenticação"
        template = "auth_otp_login_pt"
    else:
        subject = "Your authentication code"
        template = "auth_otp_login_en"
    
    m = mailer.send_email(
        sender=os.environ.get("DEFAULT_SENDER_EMAIL"),
        sender_name=os.environ.get("DEFAULT_SENDER_NAME"),
        to=user["email"],
        subject=subject,
        template=template,
        otp=random_code
    )

    return {"success": True, "attempt_id": attempt_id, "message": "Sent code! Please check your email."}

@router.post("/otp/verify")
@valid_json(["id", "code"])
async def verify_otp(request: Request):
    attempt_id = request.state.json["id"]
    code = request.state.json["code"]

    verify = login_codes.verify_otp(attempt_id, code)
    if verify != "invalid_code":
        token = sessions_controller.create_session(verify)

        return {"success": True, "token": token}
    
    return {"success": False, "message": "Invalid code."},

@router.post("/password")
@valid_json(["email", "password"])
async def password_login(request: Request):

    email = request.state.json["email"]
    password = request.state.json["password"]

    user = user_tools.get_user_by_email(email, False)

    if user == "not_found":
        return {"success": False, "message": "User not found"}
    
    if not "password" in user["auth_methods"]:
        return {"success": False, "message": "Password authentication is disabled."}
    
    verify = user_tools.verify_password_hash(password, user["password"])
    if not verify:
        return {"success": False, "message": "Invalid password."}
    
    token = sessions_controller.create_session(user["id"])

    return {"success": True, "token": token}

@router.post("/logout")
@require_auth()
async def logout(request: Request):
    token = request.headers.get("Authorization").split(" ")[1]
    sessions_controller.revoke_session(token)

    return {"success": True, "message": "Logged out successfully."}

@router.get("/me")
@require_auth()
async def get_user(request: Request):
    user = request.state.user

    return {
        "success": True,
        "user": user
    }