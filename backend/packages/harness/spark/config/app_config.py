from dotenv import load_dotenv
import logging
from pydantic import BaseModel



load_dotenv()
logger = logging.getLogger(__name__)
CONFIG_FILE_DATEBASE_DEFAULTS = {
    "backend": "sqlite",
    "sqlite_dir": "spark/data"
}



class AppConfig(BaseModel):

    def __init__(self):
        super().__init__()
        print("test and delete later in class")
    @classmethod
    def testcase(self):
        print("test and delete later")
    @staticmethod
    def test_static():
        print("test and delete later static")



def apply_logging_level(name: str | None) -> None:
    print("test and delete later in apply_logging_level")



def get_app_config():
    print("test and delete later in get_app_config")
