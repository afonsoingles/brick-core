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

    def calculate_cost(self, file, color=True, copies=1):

        decoded_file = base64.b64decode(file)
        pdf = PdfReader(io.BytesIO(decoded_file))
        pages = len(pdf.pages)

        cost = 0.50 * pages
        if color:
            cost *= 2

        cost *= copies

        return cost
    
    def _create_log(self, job_id, user_id, message):
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        log_entry = {
            "timestamp": now_ts,
            "job_id": job_id,
            "user_id": user_id,
            "description": message
        }
        return log_entry

    def register_job(self, user_id, file, color=True, copies=1, status="pending"):
        job_id = str(uuid.uuid4())
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()
        creation_log = self._create_log(job_id=job_id, user_id=user_id, message="Created this print job.")

        self.db.mongo.print_jobs_v2.insert_one({
            "_id": job_id,
            "job_id": job_id,
            "user_id": user_id,
            "cups_job_id": None,
            "file": file,
            "color": color,
            "copies": copies,
            "status": status,
            "logs": [creation_log],
            "created_at": now_ts,
            "updated_at": now_ts
        })

    def register_bulk_jobs(self, jobs):
        for job in jobs:
            self.register_job(job["user_id"], job["file"], color=job["color"], copies=job["copies"], status=job["status"])