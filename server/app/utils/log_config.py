import logging

# Define custom time log level
TIME_LOG_LEVEL = 15
logging.addLevelName(TIME_LOG_LEVEL, "TIME")

def time(self, message, *args, **kwargs):
    if self.isEnabledFor(TIME_LOG_LEVEL):
        self._log(TIME_LOG_LEVEL, message, args, **kwargs)

# Add the custom method to the Logger class
logging.Logger.time = time

# Loggers to suppress
logging.getLogger('httpcore').setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.ERROR)
logging.getLogger('protego').setLevel(logging.ERROR)

class ColoredFormatter(logging.Formatter):
    COLOR_CODES = {
        "DEBUG": "\033[94m",
        "TIME": "\033[96m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
        "CRITICAL": "\033[95m",
        "ENDC": "\033[0m",
    }

    def format(self, record):
        msg = super().format(record)
        color_code = self.COLOR_CODES.get(record.levelname, self.COLOR_CODES["ENDC"])
        return f"{color_code}{msg}{self.COLOR_CODES['ENDC']}"

def setup_colored_logger(name="colored_logger"):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = ColoredFormatter(
        "%(asctime)s [%(name)s] %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)

    return logger


