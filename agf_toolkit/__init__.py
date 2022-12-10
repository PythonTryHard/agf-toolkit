__description__ = "A toolkit for Artery Gear: Fusion"
__version__ = "0.0.1"
__author__ = "PythonTryHard - Arisu#9695 (<@!263986827214585857>)"

import os

from dotenv import load_dotenv

load_dotenv()

print(os.environ.get("LOGGING_LEVEL", "INFO"))
os.environ["LOGURU_LEVEL"] = os.environ.get("LOGGING_LEVEL", "INFO")

DATA_DIR = "~/.agf_toolkit"
