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

