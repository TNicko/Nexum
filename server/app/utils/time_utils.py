import os
import time
from typing import Union
from app.utils.log_config import setup_colored_logger

logger = setup_colored_logger("time")
logger.propagate = False

LOG_FILE_PATH = os.path.join("logs", "time_logs.txt")
IS_FILE = False

def log_time(action: str, start_time: Union[float, int], decimal_places: int = 5, output_to_file: bool = IS_FILE) -> None:
    duration = round(time.time() - start_time, decimal_places)
    log_message = f"{action}: {duration}s\n"
    logger.time(log_message)
    
    if output_to_file:
        with open(LOG_FILE_PATH, "a") as file:
            file.write(log_message)

