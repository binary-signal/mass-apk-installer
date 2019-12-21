from typing import List, Dict, Union, NoReturn
import subprocess
from functools import wraps
import logging
import os
import inspect
from enum import Enum, unique

from mass_apk.helpers import MASSAPK_OS, OS
from mass_apk.exceptions import MassApkError

_log = logging.getLogger(__name__)


class AdbError(MassApkError):
    pass


class ApkAlreadyExists(AdbError):
    pass


class Adb(object):
    @unique
    class AdbState(Enum):
        """Define adb-server state enum"""

        CONNECTED = True
        DISCONNECTED = False

    @unique
    class AdbFlag(Enum):
        # fmt:off
        ALL = ""        # list all packages
        USER = "-3"     # list 3d party packages only (default)
        SYSTEM = "-S"   # list system packages only
        # fmt:on

    @staticmethod
    def compatibility(func):
        """Decorator for making `pull` commands compatible with linux and osx"""

        @wraps(func)
        def wrapper_compatibility(*args, **kwargs):
            if func.__name__ == "pull":
                if Adb._os != OS.WIN:
                    cmd = kwargs.pop("cmd")
                    cmd = cmd.replace("pull", "shell cat")
                    cmd = f"{cmd} > base.apk"
                    kwargs.update({"cmd": cmd})

            return func(*args, **kwargs)

        return wrapper_compatibility

    @classmethod
    def _get_adb_path(cls) -> os.path:
        """Return adb path based on operating system detected during import"""

        if MASSAPK_OS == OS.OSX:
            return os.path.join("adb", "osx", "adb")

        elif MASSAPK_OS == OS.WIN:
            return os.path.join("adb", "win", "adb.exe")

        elif MASSAPK_OS == OS.LINUX:
            return os.path.join("adb", "linux", "adb")

    _os = MASSAPK_OS

    def __init__(self, auto_connect=False):
        self._path = self._get_adb_path()
        self._state = self.__class__.AdbState.DISCONNECTED
        if auto_connect:
            self.start_server()

    @property
    def path(self):
        return self._path

    @property
    def state(self) -> AdbState:
        """
        Gets the state of adb server

        If `adb-server` state is `device` then phone is connected
        """
        return self._update_state()

    def _update_state(self) -> AdbState:
        """Checks if a android phone is connected to adb-server via cable."""
        command_output = self._exec_command("get-state")

        if "error" not in command_output:
            self._state = self.__class__.AdbState.CONNECTED

        return self._state

    def start_server(self):
        """Starts adb-server process."""
        self._exec_command("start-server")

    def stop_server(self):
        """Kills adb server."""
        self._exec_command("kill-server")

    # TODO install and restore apks with generator

    @compatibility
    def _exec_command(self, cmd, return_stdout=False) -> Union[NoReturn, str]:
        """Low level function to send shell commands to running adb-server process.

        :raises AdbError
        """

        # frame hack to pull command and maintained a unified abstraction

        # if "pull" in inspect.stack()[1].function:
        #     if self.__class__._os != OS.WIN:
        #         cmd = cmd.replace("pull", "shell cat")
        #         cmd = f"{cmd} > base.apk"

        cmd = f"{self._path} {cmd}"

        return_code, output = subprocess.getstatusoutput(cmd)
        output = output.lower()

        if return_code != 0:
            raise AdbError(output)
        else:
            if return_stdout:
                return output

    def push(self, source_path, ignore_errors=True):
        """Pushes apk package to android device.

        Before calling `push` function make sure that function `connect` has been
        called earlier and `self.state` returns `true`

        extra parameters are passed to adb-server in order to  avoid errors like the following
        faulty error messages:
            `operation failed apk is already installed on device`
            `operation failed apk version is lower than the one currently installed on device`

         -d is to allow downgrade of apk
         -r is to reinstall existing apk
         """

        try:
            self._exec_command(f"install -d  -r {source_path}")
        except AdbError as error:
            _log.warning(repr(error))
            if not ignore_errors:
                raise error from None

    def pull(self, pkg_dic, apk_name=None):
        pkg_name = list(pkg_dic)

        try:
            self._exec_command(f" pull {pkg_dic[pkg_name[0]]}")
        except AdbError as error:
            _log.error(repr(error))
        else:
            if os.path.exists("base.apk"):
                os.rename("base.apk", f"{pkg_name[0]}.apk")

    def list_device(self, flag: AdbFlag):
        """Lists installed apk  packages on android device.

        Results can be filtered with PKG_FILTER to get only apk packages
        you are interested. Defaults to list 3d party apps.
            """

        output = self._exec_command(f"shell pm list packages {flag.value}")

        # adb returns packages name  in the form
        # package:com.skype.raider
        # we need to strip "package:" prefix
        return [
            line.split(":")[1].strip()
            for line in output.splitlines()
            if line.startswith("package:")
        ]
