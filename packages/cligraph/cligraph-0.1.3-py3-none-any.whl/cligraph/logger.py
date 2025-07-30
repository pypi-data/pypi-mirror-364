import logging
import time
import os
from appdirs import user_log_dir

BASE_DIR = user_log_dir("cligraph")
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(BASE_DIR, exist_ok=True)

t = time.localtime()
current_time = time.strftime("%H-%M-%S", t)

LOG_FILE = os.path.join(LOG_DIR, f"cligraph_{current_time}.log")

log_progress = logging.getLogger(__name__)
log_progress.setLevel(logging.INFO)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
progress_handler = logging.FileHandler(LOG_FILE)

progress_handler.setFormatter(formatter)
log_progress.addHandler(progress_handler)