# from __future__ import annotations

from typing import List, Union
import logging
import os
import pathlib
import subprocess
from enum import Enum, unique

from massapk import pkg_root, runtime_platform
from massapk.exceptions import MassApkError
from massapk.helpers import PLATFORM


log = logging.getLogger(__name__)


class AdbError(MassApkError):
    """Exception raised when interacting with adb executable."""


class ApkAlreadyExists(AdbError):
    """Exception raised when apk exist in device."""


class Adb(object):
    """Interface to adb server."""

    @unique
    class ConnectionState(Enum):
        """Define adb-server state enum."""

        CONNECTED = True
        DISCONNECTED = False

    @classmethod
    def _get_adb_path(cls) -> os.PathLike:
        """Return adb path based on operating system detected during import."""
        if runtime_platform == PLATFORM.OSX:
            path = os.path.join(pkg_root, "bin", "osx", "adb")
        elif runtime_platform == PLATFORM.WIN:
            path = os.path.join(pkg_root, "bin", "win", "adb.exe")
        elif runtime_platform == PLATFORM.LINUX:
            path = os.path.join(pkg_root, "bin", "linux", "adb")
        else:
            raise RuntimeError("Unsupported runtime platform")

        return pathlib.Path(path)

    def __init__(self, auto_connect=False):
        self._path = self._get_adb_path()
        self._state = self.__class__.ConnectionState.DISCONNECTED
        if auto_connect:
            self.start_server()

    def __enter__(self):
        try:
            self.start_server()
        except AdbError:
            self.stop_server()
            self.start_server()
        return self

    def __exit__(self, exc_type, exc, exc_tb):
        self.stop_server()

    @property
    def path(self):
        """Get access to detected adb path."""
        return self._path

    @property
    def state(self) -> ConnectionState:
        """
        Get connection state of adb server.

        If `adb-server` state is `device` then phone is connected
        """
        return self._update_state()

    def _update_state(self) -> ConnectionState:
        """Check if an android phone is connected to adb-server via cable."""
        command_output = self.exec_command(
            "get-state", return_stdout=True, silence_errors=True
        )

        if command_output and "error" not in command_output:
            log.warning("No phone connected waiting to connect phone")
            self._state = self.__class__.ConnectionState.CONNECTED

        return self._state

    def start_server(self):
        """Start adb-server process."""
        log.info("Starting adb server...")
        self.exec_command("start-server")

    def stop_server(self):
        """Kill adb server."""
        log.info("Killing adb server...")
        self.exec_command("kill-server")

    def exec_command(
        self, cmd, return_stdout=False, case_sensitive=False, silence_errors=False
    ) -> Union[str, None]:
        """Low level function to send command to running adb-server process.

        :raises AdbError if executed command returns non zero exit code and command output
        is empty string.
        """
        cmd = f"{self._path} {cmd}"
        log.info("Executing %s", cmd)
        return_code, output = subprocess.getstatusoutput(cmd)

        if return_code:
            if silence_errors:
                log.error(output)
                return ""

            if output == "":
                log.warning(
                    "command returned error code %s, but no output, %s",
                    return_code,
                    cmd,
                )
                raise AdbError(f"Command returned error code {cmd}")

            raise AdbError(output + f" {cmd}")

        if return_stdout:
            return output.lower() if case_sensitive else output

        return None

    def push(self, source_path, ignore_errors=True) -> None:
        """Pushes apk package to android device.

        Before calling `push` function make sure function `connect` has been
        called earlier and `self.state` value is set to `connected`

        extra parameters are passed to adb-server in order to  avoid errors like
        the following faulty error messages:
            `operation failed apk is already installed on the device`
            `operation failed apk version is lower than the one currently installed
            on the device`

         -d allow apk version down grade
         -r reinstall apk if already installed on device
        """
        try:
            self.exec_command(f"install -d -r {source_path}")
        except AdbError as error:
            log.warning(repr(error))
            if not ignore_errors:
                raise error

    def pull(self, apk_path: str) -> None:
        """Pull an apk from the following path in the android device."""
        self.exec_command(cmd=f" pull {apk_path}")

    def list_device(self, flag: str) -> List[str]:
        """Return a list with installed apk  packages on the android device.

        Results can be filtered with PKG_FILTER to get only apk packages
        you are interested. Defaults to list 3d party apps.


        list packages [-f] [-d] [-e] [-s] [-3] [-i] [-l] [-u] [-U]
              [--show-versioncode] [--apex-only] [--uid UID] [--user USER_ID] [FILTER]
            Prints all packages; optionally only those whose name contains
            the text in FILTER.  Options are:
              -f: see their associated file
              -a: all known packages (but excluding APEXes)
              -d: filter to only show disabled packages
              -e: filter to only show enabled packages
              -s: filter to only show system packages
              -3: filter to only show third party packages
              -i: see the installer for the packages
              -l: ignored (used for compatibility with older releases)
              -U: also show the package UID
              -u: also include uninstalled packages

        """
        log.info("Listing installed apk's in the device ...")
        output = self.exec_command(
            f"shell pm list packages -{flag}",
            return_stdout=True,
            case_sensitive=True,
        )

        # adb returns packages name in the form
        # package:com.skype.raider
        # we need to strip "package:" prefix
        if output is None:
            raise ValueError("Output is None")

        return [
            line.split(":", maxsplit=1)[1].strip()
            for line in output.splitlines()
            if line.startswith("package:")
        ]
