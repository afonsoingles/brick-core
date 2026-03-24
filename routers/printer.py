from fastapi import APIRouter, Request, BackgroundTasks
from tools.printer import Printer
from decorators.auth import require_auth
from decorators.valid_json import valid_json
from models.print_job import PrintJobStatus

router = APIRouter(prefix="/v2/printer", tags=["printer"])
printer = Printer()

@router.get("/jobs")
@require_auth()
async def get_print_jobs(request: Request, page: int = 1, admin_reviewer_mode: bool = False):

    if admin_reviewer_mode and request.state.user.admin:
        jobs = printer.admin_get_pending_jobs(page=page)
        return {"success": True, "data": jobs or []}
    
    jobs = printer.get_user_jobs(request.state.user.id, page=page, safe= not request.state.user.admin)
    return {"success": True, "data": jobs or []}

@router.get("/jobs/{id}")
@require_auth()
async def get_print_job(request: Request, id: str):
    job = printer.get_job(id, safe=not request.state.user.admin) # admins can see full details, while regular users get SafePrintJob.
    if not job or job["user_id"] != request.state.user.id:
        return {"success": False, "message": "Job not found"}
    
    return {"success": True, "data": job}

@router.post("/jobs/{id}/admin/decision")
@require_auth(require_admin=True)
@valid_json(["decision"])
async def set_admin_decision(request: Request, id: str):
    
    if request.state.json["decision"] not in ["approve", "reject", "set_pending"]:
        return {"success": False, "message": "Invalid decision value"}
    
    job = printer.get_job(id, False)
    if not job:
        return {"success": False, "message": "Job not found"}
    
    if job["status"] == PrintJobStatus.printed:
        return {"success": False, "message": "You may not change the status of a job that has already been printed."}
    
    bindings = {
        "approve": PrintJobStatus.approved,
        "reject": PrintJobStatus.rejected,
        "set_pending": PrintJobStatus.pending,
    }

    reason = request.state.json.get("reason", "")
    if job["status"] == bindings[request.state.json["decision"]]:
        return {"success": False, "message": f"Job is already in {request.state.json['decision']} status."}
    
    printer.update_job_status(id, bindings[request.state.json["decision"]], actor=request.state.user.id, reason=reason)
    return {"success": True, "message": f"Job was updated successfully to {request.state.json['decision']}."}