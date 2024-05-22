import datetime
import logging
import sys


class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(levelname)s %(asctime)s: "
    format_2 = "%(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset + format_2,
        logging.INFO: grey + format + reset + format_2,
        logging.WARNING: yellow + format + reset + format_2,
        logging.ERROR: red + format + reset + format_2,
        logging.CRITICAL: bold_red + format + reset + format_2,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

    def formatTime(self, record, datefmt=None):
        ct = self.converter(record.created)
        t = datetime.datetime.fromtimestamp(record.created)
        return t.strftime("%H:%M:%S.%f")[:-3]


def setup_logging(level=logging.DEBUG):
    logger = logging.getLogger("My_app")
    logger.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger


logger = setup_logging()
