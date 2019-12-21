import subprocess
from enum import Enum, unique
from mass_apk.helpers import get_adb_path
from mass_apk.exceptions import AdbError


@unique
class APK(Enum):
    """Installing an apk can end up with one these results"""

    FAILED = -1
    INSTALLED = 0
    EXISTS = -1


adb_path = get_adb_path()


def adb_start():
    """
    Starts an instance of adb server
    """
    adb_command("start-server")


def adb_kill():
    """
    Kills adb server
    """
    adb_command("kill-server")


def adb_state():
    """
    Gets the state of adb server if state is device then phone is connected
    """
    state = adb_command("get-state", ignore_return_code=True)

    if "error" in state.lower():
        return False

    return True


def adb_command(cmd, ignore_return_code=False):
    """
    Executes a command in the adb shell
    """
    global adb_path
    cmd = f"{adb_path} {cmd}"

    exit_code, output = subprocess.getstatusoutput(cmd)
    if ignore_return_code:
        return output
    if exit_code == 0:
        return output

    raise AdbError(f"adb Exit code {exit_code}, an error occurred\n{output}")


def adb_push(source_path) -> APK:
    """
    Push apk  package to android device
    """

    # -d is to allow downgrade of apk
    # -r is to reinstall existing apk
    state = adb_command(f"install -d  -r {source_path}")

    if "success" in state.lower():  # apk installed
        return APK.INSTALLED

    # when here, means something strange is happening
    if "failure" or "failed" in state.lower():
        return APK.FAILED
