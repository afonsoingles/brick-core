

def print_approved_jobs():
    import os
    from tools.printer import PrinterConnector, Printer
    from models.print_job import PrintJobStatus
    from utils.storage import Storage

    storage = Storage()
    printer = Printer()
    printer_connector = PrinterConnector()
    approved_jobs = printer.daemon_get_approved_jobs(page=1, per_page=10)
    for job in approved_jobs:
        file_data = storage.get_file_data(os.environ.get("S3_USER_CONTENT_BUCKET"), job["file"])
        printer_connector.print_data(file_data, job_name=job["filename"])
        printer.update_job_status(job["id"], PrintJobStatus.printed, actor="system")

    
    