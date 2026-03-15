from fastapi import APIRouter, Request, BackgroundTasks
from tools.printer import Printer
from decorators.auth import require_auth

router = APIRouter(prefix="/v2/printer", tags=["printer"])
printer = Printer()

@router.get("/jobs")
@require_auth()
async def get_print_jobs(request: Request, page: int = 1):
    
    jobs = printer.get_user_jobs(request.state.user["id"], page=page)
    return {"success": True, "data": jobs or []}

@router.get("/jobs/{id}")
@require_auth()
async def get_print_job(request: Request, id: str):
    job = printer.get_job(id)
    if not job or job["user_id"] != request.state.user["id"]:
        return {"success": False, "message": "Job not found"}
    
    return {"success": True, "data": job}