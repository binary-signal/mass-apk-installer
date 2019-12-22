import os
import platform
import logging
from enum import Enum, unique
import functools
from timeit import default_timer as timer

log = logging.getLogger(__name__)


@unique
class OS(Enum):
    OSX = "osx"
    LINUX = "linux"
    WIN = "win"


def MASSAPK_OS() -> OS:
    """
    Detect running operating system

    :raises RuntimeError when operating not detected
    """

    detected_system = platform.system()

    if "posix" == os.name and "Darwin" == detected_system:
        return OS.OSX
    elif "posix" == os.name and "Linux" == detected_system:
        return OS.LINUX
    elif "nt" == os.name and "Windows" == detected_system:
        return OS.WIN

    raise RuntimeError("Unsupported OS")


MASSAPK_OS = MASSAPK_OS()


def human_time(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    return "Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(
        int(hours), int(minutes), seconds
    )


def rename_fix(path):
    """
    Apply  rename fix to files inside folder path,
    replace space character with  underscore
    """
    if os.path.isdir(path):
        files = [file for file in os.listdir(path) if file.endswith(".apk")]

        def check_file(f):
            if " " in f:
                return f.replace(" ", "_")
            return f

        new_files = [check_file(file) for file in files]

        for old, new in zip(files, new_files):
            os.rename(os.path.join(path, old), os.path.join(path, new))
    raise NotADirectoryError


def timed(func):
    """
    Decorator for measuring execution time of decorated function.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = timer()
        result = func(*args, **kwargs)
        end = timer()
        log.info("{} elapsed time: {}".format(func.__name__, human_time(start, end)))
        return result

    return wrapper
