"""Mass apk helper functions module."""

import functools
import logging
import os
import platform
from enum import Enum, unique
from timeit import default_timer as timer

__all__ = ["Platform", "detect_platform", "human_time", "elapsed_time"]

log = logging.getLogger(__name__)


@unique
class Platform(Enum):
    """Platform enum used to detected running operating system."""

    OSX = "osx"
    LINUX = "linux"
    WIN = "win"


def detect_platform() -> Platform:
    """Detect running operating system.

    raises RuntimeError if operating system can't be detected.
    """
    detected_system = platform.system()

    if os.name == "posix" and detected_system == "Darwin":
        return Platform.OSX
    elif os.name == "posix" and detected_system == "Linux":
        return Platform.LINUX
    elif os.name == "nt" and detected_system == "Windows":
        return Platform.WIN

    raise RuntimeError("Unsupported OS")


def human_time(start: float, end: float) -> str:
    """Create a human readable string.

    Create a human readable string for elapsed time between
    start and end timestamps.
    """
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(minutes), seconds
    )


def elapsed_time(func):
    """Decorate function `func` to measure its execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        log.debug("%s elapsed time: %s", func.__name__, human_time(start, end))
        return result

    return wrapper
