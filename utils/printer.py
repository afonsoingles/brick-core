import os
import cups
import tempfile


class Printer:
    def __init__(self):
        self.host = os.environ.get("PRINTER_CUPS_HOST")
        self.port = int(os.environ.get("PRINTER_CUPS_PORT"))
        self._printer = os.environ.get("PRINTER_CUPS_PRINTER_NAME")
        self._connection = cups.Connection(host=self.host, port=self.port)
        printers = self._connection.getPrinters()
        if not printers:
            raise Exception("No printers found on the CUPS server. Please configure a printer first.")

        if self._printer and self._printer in printers:
            self.printer = self._printer
        else:
            self.printer = list(printers.keys())[0]
    
    def print_file(self, path: str, job_name: str ="BRICK"):
        if not os.path.isfile(path):
            raise Exception(f"File not found: {path}")

        job_id = self._connection.printFile(
            self.printer,
            path,
            job_name,
            {}
        )
        return job_id

    def print_data(self, data: bytes, job_name: str ="BRICK"):
        with tempfile.NamedTemporaryFile(delete=True) as temp_file:
            temp_file.write(data)
            temp_file.flush()
            job_id = self.print_file(temp_file.name, job_name)
        return job_id
