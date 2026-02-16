from utils.database import Database
from tools.users import UserTools
import datetime
import uuid
from utils.printer import Printer as PrinterConnector
from pypdf import PdfReader
import io
import base64

class Printer:
    def __init__(self):
        self.db = Database()
        self.user_tools = UserTools()
        self.printer = PrinterConnector()

    def _has_enough_credits(self, id, pages, color=True):
        user = self.user_tools.get_user_by_id(id)
        
        cost = pages * 0.5
        if color:
            cost *= 2
        
        return user["printer"]["credits"] >= cost, cost
    
    def _remove_credits(self, id, cost):
        user = self.user_tools.get_user_by_id(id)
        user["printer"]["credits"] -= cost

        self.user_tools.update_user(id, {"printer": user["printer"]})

        
    def register_print_job(self, id, file_name, content):
        user = self.user_tools.get_user_by_id(id)
        job_id = str(uuid.uuid4())
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        
        pages = len(PdfReader(io.BytesIO(content)).pages)
        has_credits, cost = self._has_enough_credits(id, pages, color=True)

        if not has_credits:
            if user["printer"]["no_credits_action"] == "require_approval":
                self.db.mongo.print_jobs.insert_one({
                    "_id": job_id,
                    "id": job_id,
                    "sender": id,
                    "cost": cost,
                    "pages": pages,
                    "content": str(base64.b64encode(content).decode("utf-8")),
                    "file_name": file_name,
                    "status": "pending",
                    "created_at": now_ts,
                })
                return "pending"
            
            return "not_enough_credits"
        
        self._remove_credits(id, cost)

        self.db.mongo.print_jobs.insert_one({
            "_id": job_id,
            "id": job_id,
            "sender": id,
            "cost": cost,
            "pages": pages,
            "file_name": file_name,
            "status": "approved",
            "created_at": now_ts,
        })

        self.printer.print_data(content, job_name=f"Brick_{job_id}")

    def get_user_print_jobs(self, id, page=1, per_page=10):
        skip = (page - 1) * per_page
        jobs = list(self.db.mongo.print_jobs.find({"sender": id}).sort("created_at", -1).skip(skip).limit(per_page))
        

        return jobs
    
    def get_print_job(self, job_id):
        job = self.db.mongo.print_jobs.find_one({"id": job_id})
        return job
    
    def approve_print_job(self, job_id):
        job = self.db.mongo.print_jobs.find_one({"id": job_id})
        if not job:
            return "job_not_found"
        
        if job["status"] != "pending":
            return "job_not_pending"
        
        #self._remove_credits(job["sender"], job["cost"])
        self.db.mongo.print_jobs.update_one({"id": job_id}, {"$set": {"status": "approved"}})
        content_decoded = base64.b64decode(job["content"])
        self.printer.print_data(content_decoded, job_name=f"Brick_{job_id}")
    
    def reject_print_job(self, job_id):
        job = self.db.mongo.print_jobs.find_one({"id": job_id})
        if not job:
            return "job_not_found"
        
        if job["status"] != "pending":
            return "job_not_pending"
        
        self.db.mongo.print_jobs.update_one({"id": job_id}, {"$set": {"status": "rejected"}})
    
    def get_pending_print_jobs(self, page=1, per_page=10):
        skip = (page - 1) * per_page
        jobs = list(self.db.mongo.print_jobs.find({"status": "pending"}).sort("created_at", -1).skip(skip).limit(per_page))
        return jobs