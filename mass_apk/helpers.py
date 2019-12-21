import os
import platform
from enum import Enum, unique


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
    print(
        "Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds)
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
