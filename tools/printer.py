from utils.database import Database
from tools.users import UserTools
from models.print_job import PrintJob, PrintJobLog, PrintJobStatus, SafePrintJob
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

    def calculate_cost(self, file, color=True, copies=1):

        decoded_file = base64.b64decode(file)
        pdf = PdfReader(io.BytesIO(decoded_file))
        pages = len(pdf.pages)

        cost = 0.50 * pages
        if color:
            cost *= 2

        cost *= copies

        return cost
    
    def _create_log(self, actor, log_type, description=None):
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        return PrintJobLog(
            id=str(uuid.uuid4()),
            timestamp=now_ts,
            actor=actor,
            type=log_type,
            description=description,
        )

    def register_job(self, user_id, filename, file, color=True, copies=1, status="pending"):
        job_id = str(uuid.uuid4())
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        creation_log = self._create_log(actor=user_id, log_type="job_created", description="Created this print job.")

        job = PrintJob(
            id=job_id,
            user_id=user_id,
            filename=filename,
            file=file,
            color=color,
            copies=copies,
            status=PrintJobStatus(status),
            logs=[creation_log],
            created_at=now_ts,
            updated_at=now_ts,
        )

        job_dict = job.model_dump()
        job_dict["_id"] = job_id  # MongoDB requires _id

        self.db.mongo.print_jobs_v2.insert_one(job_dict)

    def register_bulk_jobs(self, jobs):
        for job in jobs:
            self.register_job(job["user_id"], job["filename"], job["file"], color=job["color"], copies=job["copies"], status=job["status"])
    
    def get_user_jobs(self, user, page=1, per_page=10, safe=True):
        skip = (page - 1) * per_page
        raw_jobs = list(self.db.mongo.print_jobs_v2.find({"user_id": user}).sort("created_at", -1).skip(skip).limit(per_page))
        return [SafePrintJob.model_validate(j).to_safe().model_dump() for j in raw_jobs] if safe else [PrintJob.model_validate(j).model_dump() for j in raw_jobs]
    
    def admin_get_pending_jobs(self, page=1, per_page=10):
        skip = (page - 1) * per_page
        raw_jobs = list(self.db.mongo.print_jobs_v2.find({"status": "pending"}).sort("created_at", -1).skip(skip).limit(per_page))
        return [PrintJob.model_validate(j).model_dump() for j in raw_jobs]
    
    def get_job(self, id, safe=True):
        raw = self.db.mongo.print_jobs_v2.find_one({"_id": id})
        if not raw:
            return None
        return SafePrintJob.model_validate(raw).model_dump() if safe else PrintJob.model_validate(raw).model_dump()