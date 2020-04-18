import functools
import logging
import os
import platform
from enum import Enum, unique
from timeit import default_timer as timer

log = logging.getLogger(__name__)


@unique
class PLATFORM(Enum):
    OSX = "osx"
    LINUX = "linux"
    WIN = "win"


def detect_platform() -> PLATFORM:
    """
    Detect running operating system

    :raises RuntimeError when operating not detected
    """

    detected_system = platform.system()

    if "posix" == os.name and "Darwin" == detected_system:
        return PLATFORM.OSX
    elif "posix" == os.name and "Linux" == detected_system:
        return PLATFORM.LINUX
    elif "nt" == os.name and "Windows" == detected_system:
        return PLATFORM.WIN

    raise RuntimeError("Unsupported OS")


def human_time(start, end) -> str:
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(minutes), seconds
    )


def elapsed_time(func):
    """
    Decorator for measuring execution time of decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        log.debug("{} elapsed time: {}".format(func.__name__, human_time(start, end)))
        return result

    return wrapper
