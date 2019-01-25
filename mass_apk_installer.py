#!/usr/bin/env python

"""
 Name:        apk_mass_install

 Author:      Evan
 Created:     19/10/2011
 Last Modified: 12/02/2018
 Copyright:   (c) Evan 2018
 Licence:
 Copyright (c) 2018, Evan
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the <organization> nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 vWARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 """

from timeit import default_timer as timer
from platform import system
from datetime import datetime
import time
import subprocess
import argparse
import shutil
import sys
import os
import zipfile

import progressbar as pb

from tools.encryption import AesEncryption

INSTALL_FAILURE = -1
INSTALL_OK = 1
INSTALL_EXISTS = 2

# Flags for adb list packages
pkg_flags = {
    "all": "",  # list all packages
    "user": "-3",  # list 3d party packages only (default)
    "system": "-S",
}  # list system packages only


def detect_os():
    """
    Detect running operating system
    """
    system_ = system()

    if "posix" in os.name and "Darwin" in system_:
        return "osx"
    elif "posix" in os.name and "Linux" in system_:
        return "linux"
    elif "nt" in os.name and "Windows" in system_:
        return "win"
    else:
        raise RuntimeError("Unsupported OS")


os_platform = detect_os()


class ZipTools:
    @staticmethod
    def print_info(archive_name):
        zf = zipfile.ZipFile(archive_name)
        for info in zf.infolist():
            print(info.filename)

    @staticmethod
    def zipdir(path, zipf):
        if os.path.isdir(path):
            files = [
                f
                for f in os.listdir(path)
                if os.path.isfile(os.path.join(path, f))
            ]
            abs_src = os.path.abspath(path)
            apks = []
            for file in files:
                if file.endswith(".apk"):
                    apks.append(file)

            iteration = len(apks)

            # initialize widgets
            widgets = [
                "progress: ",
                pb.Percentage(),
                " ",
                pb.Bar(),
                " ",
                pb.ETA(),
            ]
            # initialize timer
            timer = pb.ProgressBar(widgets=widgets, maxval=iteration).start()
            count = 0

            for apk in apks:
                # don't preserver folder structure inside zip file
                absname = os.path.abspath(os.path.join(path, apk))
                arcname = absname[len(abs_src) + 1 :]
                zipf.write(os.path.join(path, apk), arcname)

                # update progress bar
                count += 1
                timer.update(count)
            timer.finish()

    @staticmethod
    def make_zip(path, output):
        zipf = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
        ZipTools.zipdir(path, zipf)
        zipf.close()

    @staticmethod
    def extract_zip(zip_file, output):
        if zipfile.is_zipfile(zip_file):
            zip = zipfile.ZipFile(zip_file, "r")

            # create output directory if doesn't exist
            if not os.path.exists(output):
                os.makedirs(output)

            iteration = len(zip.namelist())

            # initialize widgets
            widgets = [
                "progress: ",
                pb.Percentage(),
                " ",
                pb.Bar(),
                " ",
                pb.ETA(),
            ]
            # initialize timer
            timer = pb.ProgressBar(widgets=widgets, maxval=iteration).start()
            count = 0

            # extract files
            for filename in zip.namelist():
                try:
                    zip.extract(filename, output)

                    # update progress bar
                    count += 1
                    timer.update(count)
                except KeyError:
                    print(
                        "ERROR: Did not find {} in zip file".format(filename)
                    )
            timer.finish()


def pull_apk(pkg_dic):
    """
    Pulls apk specified in pkgDic variable from android device using adb
    renames extracted apk to filename specified in pkgDic key value pair.
    """

    pkg_name = list(pkg_dic)

    if os_platform is "osx":
        path = os.path.join("adb", "osx", "adb")
        cmd = f"{path} shell cat {pkg_dic[pkg_name[0]]} > base.apk"
        # cmd = "./osx/adb pull " + pkgDic[pkg_name[0]] doesn't work anymore after nougat update
    elif os_platform is "win":
        path = os.path.join("adb", "win", "adb.exe")
        cmd = f"{path} pull {pkg_dic[pkg_name[0]]}"
    elif os_platform is "linux":
        path = os.path.join("adb", "linux", "adb")
        cmd = f"{path} shell cat {pkg_dic[pkg_name[0]]} > base.apk"

    exit_code, output = subprocess.getstatusoutput(cmd)
    if exit_code == 0:
        if os.path.exists("base.apk"):
            os.rename("base.apk", pkg_name[0] + ".apk")


def package_management(PKG_FILTER):
    """
    Lists all packages installed  in android device. Results can be
    filtered with PKG_FILTER to get only apk packages you are interested. By
    default listing only 3d party apps.
    """

    state = adb_command(f"shell pm list packages {PKG_FILTER}")

    pkg = []

    # adb returns packages name  in the form
    # package:com.skype.raider
    # we need to strip "package:" prefix
    for i in state.splitlines():
        if i.startswith("package:"):
            y = [x.strip() for x in i.split(":")]
            pkg.append(y[1])

    return pkg


def get_package_full_path(pkg_name):
    """
    Returns the full path of a package in android device storage
    """

    state = adb_command(f"shell pm path {pkg_name}")

    # adb returns packages name  in the form
    # package:/data/app/com.dog.raider-2/base.apk
    # we need to strip package: prefix in returned string

    pkg_path = [x.strip() for x in state.split(":")]
    return pkg_path[1]


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

    if "error" in state:
        return False

    return True


def adb_command(cmd, ignore_return_code=False):
    """
    Executes a command in the adb shell
    """

    if os_platform is "osx":
        prefix = os.path.join("adb", "osx", "adb")
    elif os_platform is "win":
        prefix = os.path.join("adb", "win", "adb.exe")
    elif os_platform is "linux":
        prefix = os.path.join("adb", "linux", "adb")

    cmd = prefix + " " + cmd

    exit_code, output = subprocess.getstatusoutput(cmd)
    if ignore_return_code:
        return output
    if exit_code == 0:
        return output
    else:
        print(f"Exit code {exit_code}, an error occurred\n{output}")
        sys.exit(-1)


def adb_install(source_path):
    """
    Installs package to android device
    """

    # -d is to allow downgrade of apk
    # -r is to reinstall existing apk
    state = adb_command(f"install -d  -r {source_path}")

    if "Success" in state:  # apk installed
        return INSTALL_OK

    # when here, means something strange is happening
    if "Failure" or "Failed" in state:
        return INSTALL_FAILURE


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


def human_time(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print(
        "Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(
            int(hours), int(minutes), seconds
        )
    )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Simple Backup / Restore  of Android apps"
    )
    subparsers = parser.add_subparsers(
        required=True, dest="command", help="command help"
    )
    parser_restore = subparsers.add_parser(
        "restore", help="restore a back up to device from path"
    )
    parser_restore.add_argument(
        "path", help="path to folder, zip file or encrypted archive backup"
    )

    parser_backup = subparsers.add_parser(
        "backup", help="perform device back up"
    )
    parser_backup.add_argument(
        "-o", "--outdir", help="save backup  to path", default="."
    )
    parser_backup.add_argument(
        "-a", "--archive", help="create  a zipped backup", action="store_true"
    )
    parser_backup.add_argument(
        "-e",
        "--encrypt",
        help="create an encrypted backup",
        action="store_true",
    )
    args = parser.parse_args()
    args = vars(args)
    command = args.pop("command")
    return command, args


def summary(install_state):
    success = 0
    fail = 0

    print("\n\nSummary: ")
    for s in install_state:
        if s == INSTALL_FAILURE:
            fail = fail + 1
        elif s == INSTALL_OK:
            success = success + 1
    print(f"Installed:{success} |  Failed:{fail}")


def back_up(archive=False, encrypt=False):
    # generate filename from current date time
    backup_file = (
        str(datetime.utcnow())
        .split(".")[0]
        .replace(" ", "_")
        .replace(":", "-")
    )
    try:
        os.rmdir(backup_file)
        os.mkdir(backup_file)
    except FileNotFoundError:
        pass

    print("Listing installed apk's in device...\n")
    # get user installed packages
    pkgs = package_management(pkg_flags["user"])

    num_apk = len(pkgs)

    print("Discovering apks paths this may take a while...")
    # get full path on the android filesystem for each installed package
    paths = [get_package_full_path(pkg) for pkg in pkgs]

    # combine apk name and apk path into dictionary object
    pkgs_paths = [{pkg: paths} for pkg, path in zip(pkgs, paths)]

    print(f"\nFound {num_apk} installed packages\n")

    space = len(str(num_apk))  # calculate space for progress bar
    progress = 0
    for i in pkgs_paths:  # i is dict {package name: package path}
        progress += 1
        print(
            "[{0:{space}d}/{1:{space}d}] pulling ... {2}".format(
                progress, num_apk, i[list(i)[0]], space=space
            )
        )
        pull_apk(i)  # get apk from device

        shutil.move(
            list(i)[0] + ".apk",  # move apk to back up directory
            os.path.join(backup_file, list(i)[0] + ".apk"),
        )

    if archive:
        print(f"\nCreating zip archive: {backup_file}.zip")
        ZipTools.make_zip(backup_file, backup_file + ".zip")
        if os.path.exists(backup_file):
            shutil.rmtree(backup_file)

    if encrypt:

        key = input("Enter password for encryption:")
        a = AesEncryption(key)
        print(
            f"\nEncrypting archive {backup_file}.zip this may take a while..."
        )
        a.encrypt(backup_file + ".zip", backup_file + ".aes")

        try:
            os.remove(backup_file + ".zip")
        except FileNotFoundError:
            pass

    print("\nBack up finished")


def restore(backup_path):
    clean_up = []  # list of files, dirs to delete after install

    if not os.path.exists(backup_path):
        print(f"File or folder doesn't exist {backup_path}")
        return

    if os.path.isdir(backup_path):  # install from folder
        print(f"\nRestoring back up from folder: {backup_path}")
        apk_path = backup_path

    elif os.path.isfile(backup_path):  # install from file
        filename, file_extension = os.path.splitext(backup_path)

        if ".zip" in file_extension:  # install from zip archive
            print(f"\nRestoring back up from zip file: {backup_path}")
            print(f"\nUnzipping {backup_path} ...")
            ZipTools.extract_zip(backup_path, filename)
            apk_path = filename
            clean_up.append(filename)

        # install from encrypted archive
        elif ".aes" in file_extension:

            key = input("Enter password for decryption:")
            a = AesEncryption(key)
            print(
                f"\nDecrypting back up {backup_path} this may take a while..."
            )
            a.decrypt(backup_path, filename + ".zip")
            print("Unzipping archive this may take also a while...")
            ZipTools.extract_zip(filename + ".zip", filename)
            apk_path = filename
            clean_up.append(filename + ".zip")
            clean_up.append(filename)

    try:
        rename_fix(apk_path)
        apks = [file for file in os.listdir(apk_path) if file.endswith(".apk")]
    except NotADirectoryError:
        print(f"isn't a dir {apk_path}")
        return

    # calculate total installation size
    size = [os.path.getsize(os.path.join(apk_path, apk)) for apk in apks]

    print(
        "\nTotal Installation Size: {0:.2f} MB\n{}".format(
            sum(size) / (1024 * 1024), "-" * 10
        )
    )
    state = []
    progress = 0

    space = len(str(len(apks)))  # calculate space for progress bar
    for apk in apks:
        progress += 1
        print(
            "[{0:{space}d}/{1:{space}d}] Installing {2}".format(
                progress, len(apks), str(apk), space=space
            )
        )
        s = adb_install(os.path.join(apk_path, apk))
        state.append(s)

    summary(state)

    for f in clean_up:
        if os.path.exists(f):
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
    print("\nRestore  finished")


def main(command, args):
    print("Apk Mass Installer Utility \nVersion: 3.1\n")

    adb_kill()  # kill any instances of adb before starting if any

    # wait for adb to detect phone
    while True:
        if adb_state():
            break
        print("No phone connected waiting to connect phone")
        time.sleep(1)

    print("Starting adb server...")
    adb_start()  # start an instance of adb server

    t_start = timer()

    if "backup" in command:
        archive = args.pop("archive", False)
        encrypt = args.pop("encrypt", False)
        back_up(archive, encrypt)

    elif "restore" in command:
        path = args.pop("path")
        restore(path)

    human_time(t_start, timer())

    adb_kill()


if __name__ == "__main__":
    command, args = parse_args()
    try:
        main(command, args)
    except KeyboardInterrupt:
        print("Received Interrupt")
