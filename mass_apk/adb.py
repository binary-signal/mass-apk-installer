from typing import List, Dict, Union, NoReturn
import os
import functools
import subprocess
import logging
from enum import Enum, unique

from mass_apk.helpers import MASSAPK_OS, OS
from mass_apk.exceptions import MassApkError
from mass_apk import AbsPath


log = logging.getLogger(__name__)


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
        ALL = ""  # list all packages
        USER = "-3"  # list 3d party packages only (default)
        SYSTEM = "-S"  # list system packages only
        # fmt:on

    def compatibility(func):
        """Decorator for making `pull` commands compatible with linux and osx"""

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                cmd: str = kwargs.pop("cmd")
            except KeyError:
                pass
            else:
                if "pull" in cmd and Adb._os != OS.WIN:
                    cmd = cmd.replace("pull", "shell cat")
                    cmd = f"{cmd} > base.apk"
                    kwargs.update({"cmd": cmd})

            return func(*args, **kwargs)

        return functools.update_wrapper(wrapper, func)

    @classmethod
    def _get_adb_path(cls) -> os.path:
        """Return adb path based on operating system detected during import"""

        if MASSAPK_OS == OS.OSX:
            return os.path.join("bin", "osx", "adb")

        elif MASSAPK_OS == OS.WIN:
            return os.path.join("bin", "win", "adb.exe")

        elif MASSAPK_OS == OS.LINUX:
            return os.path.join("bin", "linux", "adb")

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
        command_output = self._exec_command("get-state", return_stdout=True)

        if "error" not in command_output:
            log.warning("No phone connected waiting to connect phone")
            self._state = self.__class__.AdbState.CONNECTED

        return self._state

    def start_server(self):
        """Starts adb-server process."""
        log.info("Starting adb server...")
        self._exec_command("start-server")

    def stop_server(self):
        """Kills adb server."""
        log.info("Killing adb server...")
        self._exec_command("kill-server")

    # TODO install and restore apks with generator

    # @compatibility
    def _exec_command(
        self, cmd, return_stdout=False, case_sensitive=False
    ) -> Union[NoReturn, str]:
        """Low level function to send shell commands to running adb-server process.

        :raises AdbError
        """

        cmd = f"{self._path} {cmd}"
        return_code, output = subprocess.getstatusoutput(cmd)
        # FIXME maybe need to remove lower case to preserve package names

        if return_code:
            if output:
                raise AdbError(output)

            log.warning(f"command returned error code {return_code}, but no output")

        if return_stdout:
            return output.lower() if not case_sensitive else output

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
            log.warning(repr(error))
            if not ignore_errors:
                raise error from None

    def pull(self, apk_path: str):

        self._exec_command(cmd=f" pull {apk_path}")

    def list_device(self, flag: AdbFlag):
        """Lists installed apk  packages on android device.

        Results can be filtered with PKG_FILTER to get only apk packages
        you are interested. Defaults to list 3d party apps.
            """

        log.info("Listing installed apk's in device...")
        output = self._exec_command(
            f"shell pm list packages {flag.value}",
            return_stdout=True,
            case_sensitive=True,
        )

        # adb returns packages name  in the form
        # package:com.skype.raider
        # we need to strip "package:" prefix
        return [
            line.split(":", maxsplit=1)[1].strip()
            for line in output.splitlines()
            if line.startswith("package:")
        ]
