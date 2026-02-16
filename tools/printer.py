from utils.database import Database
from tools.users import UserTools
import datetime
import uuid
from utils.printer import Printer as PrinterConnector

class Printer:
    def __init__(self):
        self.db = Database()
        self.user_tools = UserTools()
        self.printer = PrinterConnector()


    def register_print_job(self, id, file_name, file_b64):
        job_id = str(uuid.uuid4())
        now_ts = datetime.datetime.now(datetime.timezone.utc).timestamp()

        self.db.mongo.print_jobs.insert_one({
            "_id": job_id,
            "id": job_id,
            "sender": id,
            "file_name": file_name,
            "created_at": now_ts,
        })

        self.printer.print_data(file_b64, job_name=f"brick_print_job_{job_id}")


                

