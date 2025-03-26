import sys
import os


if getattr(sys, 'frozen', False):

    EXE_PATH = os.path.abspath(sys.executable)
    EXE_DIR = os.path.dirname(EXE_PATH)
else:

    EXE_DIR = os.path.dirname(os.path.abspath(__file__))


DATA_FILE = os.path.join(EXE_DIR, "vacation_calendar_data.json")
VERSION = "1.3.0"
