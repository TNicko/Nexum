import time
from typing import Union
from app.utils.log_config import setup_colored_logger

logger = setup_colored_logger("time")
logger.propagate = False
def log_time(action: str, start_time: Union[float, int], decimal_places: int = 5) -> None:
    duration = round(time.time() - start_time, decimal_places)
    logger.time(f"{action}: {duration}s")

