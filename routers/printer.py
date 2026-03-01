from fastapi import APIRouter, Request, BackgroundTasks
from tools.printer import Printer
from decorators.auth import require_auth

router = APIRouter(prefix="/v1/printer", tags=["printer"])
printer = Printer()

@router.get("/jobs")
@require_auth()
async def get_print_jobs(request: Request, page: int = 1):
    
    jobs = printer.get_user_print_jobs(request.state.user["id"], page)
    return {"success": True, "data": jobs}

@router.get("/admin/pending")
@require_auth(require_admin=True)
async def get_pending_jobs(request: Request, page: int = 1):
    jobs = printer.get_pending_print_jobs(page)
    
    return {"success": True, "data": jobs}

@router.get("/jobs/{id}")
@require_auth()
async def get_print_job(request: Request, id: str):
    
    job = printer.get_print_job(id)
    if job is None:
        return {"success": False, "error": "Job not found"}
    
    if job["sender"] != request.state.user["id"]:
        return {"success": False, "error": "Job not found"}