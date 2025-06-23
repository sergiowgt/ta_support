from dataclasses import dataclass
from dotenv import load_dotenv

import os

load_dotenv()
@dataclass
class DbConfig:
    def __init__(self):
        self.driver =  os.environ.get('DB_DRIVER', '')
        self.host =  os.environ.get('DB_HOST', '')
        self.db_name = os.environ.get('DB_NAME', '')
        self.user = os.environ.get('DB_USER', '')
        self.password = os.environ.get('DB_PASSWORD', '')
        self.echo = os.environ.get('DB_ECHO', '')
        self.timeout = os.environ.get('DB_TIMEOUT', 0)

    def get_path(self): 
        return f"{self.driver}://{self.user}:{self.password}@{self.host}/{self.db_name}"