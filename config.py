import os
PROJECT_PATH = os.path.split(os.path.abspath(__file__))[0]

UPLOAD_ROOT_PATH = os.path.join(PROJECT_PATH,"upload")

BUILD_DIR_NAME = "build"
LOG_DIR_NAME = "log"

HOST = "http://0.0.0.0:5000/"

MIN_GAP = 1.5

WATCH_DIR = [
    r"C:\Documents\Desktop\latex",

]