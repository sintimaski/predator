import sys

from app.logger import logger


class TerminalColors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"


class Terminus:
    def __init__(self):
        pass

    def print(self):
        pass


def printc(message, color):
    logger.debug(color + message + TerminalColors.RESET)


def colorize(message, color):
    return color + message + TerminalColors.RESET
