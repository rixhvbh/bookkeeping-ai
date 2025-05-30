# utils/logger_config.py

import logging
from datetime import datetime
import os

def setup_logger(log_folder='logs', log_name='run_log.txt'):
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, log_name)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

    logging.info("Logger initialized.")
