#!/usr/bin/env python

"""
 Name:        apk_mass_install

Purpose:  This module automates back or restoration of multiple apk's, apk is the
           standard executable in Android platform made by Google



 Author:      Evangelos Mouroutsos

 Created:     19/10/2011
 Last Modified: 12/02/2018
 Copyright:   (c) Evangelos Mouroutsos 2018
 Licence:
 Copyright (c) 2018, Evangelos Mouroutsos
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
import subprocess
import argparse
import shutil
import sys
import os

from archive import extract_zip, make_zip
from encryption import AesEncryption

INSTALL_FAILURE = -1
INSTALL_OK = 1
INSTALL_EXISTS = 2

# Flags used for adb package listing
pkg_flags = {'all': "",  # list all packages
             'user': "-3",  # list 3d party packages only (default)
             'system': "-S"}  # list system packages only


def detect_os():
    # detect platform
    if os.name == 'posix' and system() == 'Darwin':
        os_platform = 'osx'
    elif os.name == 'posix' and system() == 'Linux':
        os_platform = 'linux'
    elif os.name == 'win':
        os_platform = 'win'
    else:
        raise ValueError("Unsupported OS")

    return os_platform


os_platform = detect_os()


def pull_apk(pkg_dic):
    """
    Pulls apk specified in pkgDic variable from android device using adb
    renames extracted apk to filename specified in pkgDic key value pair
    pkgDic is an one value dictionary.
    :param pkg_dic: {package name : package path}
    :return: None
    """

    pkg_name = list(pkg_dic)

    if os_platform == 'osx':
        cmd = './adb_osx/adb shell cat {} > base.apk'.format(pkg_dic[pkg_name[0]])
        # cmd = "./adb_osx/adb pull " + pkgDic[pkg_name[0]] doesn't work anymore after nougat update
    elif os_platform == 'win':
        cmd = "adb_win/adb.exe pull {}".format(pkg_dic[pkg_name[0]])

    state = subprocess.check_output(cmd, shell=True)

    if os.path.isfile("base.apk"):
        os.rename("base.apk", pkg_name[0] + ".apk")


def package_management(PKG_FILTER):
    """
    list all packages installed installed in android device. Results can be
    filtered with PKG_FILTER to get only apk packages you are interested. By default
    listing only 3d party apps.
    :param PKG_FILTER:
    :return:
    """

    if os_platform == 'osx':
        cmd = "./adb_osx/adb shell pm list packages {}".format(PKG_FILTER)
    elif os_platform == 'win':
        cmd = "/adb_win/adb.exe shell pm list packages {}".format(PKG_FILTER)

    state = subprocess.check_output(cmd, shell=True)
    pkg_raw = state.splitlines()
    pkg = []

    """
    adb returns packages name  in the form
    package:com.skype.raider
    we need to strip package: prefix
    """
    for i in pkg_raw:
        # convert binary string to string
        i = i.decode('ascii', 'ignore')
        if i.startswith("package:"):
            y = [x.strip() for x in i.split(':')]
            pkg.append(y[1])

    return pkg


def get_package_full_path(pkg_name):
    """
     Returns full path of package in android device storage specified by argument
    :param pkg_name:
    :return:
    """
    if os_platform == 'osx':
        cmd = "./adb_osx/adb shell pm path {}".format(pkg_name)
    elif os_platform == 'win':
        cmd = "adb/win/adb.exe shell pm path {}".format(pkg_name)

    state = subprocess.check_output(cmd, shell=True)
    state = state.decode('ascii', 'ignore')

    """
    adb returns packages name  in the form
    package:/data/app/com.dog.raider-2/base.apk
     we need to strip package: prefix in returned string
    """

    pkg_path = [x.strip() for x in state.split(':')]
    return pkg_path[1]


def adb_start():
    """
    starts an instance of adb server
    """

    print('Starting adb server...')
    if os_platform == 'osx':
        cmd = './adb_osx/adb start-server'  # command to adb
    elif os_platform == 'win':
        cmd = 'adb_win/adb.exe start-server'  # command to adb
    state = os.system(cmd)  # execute the command in terminal
    if state:
        print('{}: running {} failed'.format(sys.argv[0], cmd))
        sys.exit(1)
    print('Make sure your Android phone is connected and debug mode is enabled !')


def adb_kill():
    """
    kills adb server
    """

    print('Killing adb server...')
    if os_platform == 'osx':
        cmd = './adb_osx/adb kill-server'  # command to adb
    elif os_platform == 'win':
        cmd = 'adb_win/adb.exe kill-server'  # command to adb
    state = os.system(cmd)  # execute command to terminal
    if state:
        print('{}: running {} failed'.format(sys.argv[0], cmd))
        sys.exit(1)


def adb_state():
    """
    gets the state of adb server if state is device then phone is connected
    """

    if os_platform == 'osx':
        cmd = './adb_osx/adb get-state'
    elif os_platform == 'win':
        cmd = 'adb_win/adb.exe get-state'

    output = os.popen(cmd)  # command to run
    res = output.readlines()  # res: output from running cmd
    state = output.close()
    if state:
        print('{}: running {} failed'.format(sys.argv[0], cmd))
        sys.exit(1)
    for line in res:
        if str.rstrip(line) == "device":  # found a connected device
            return True
        else:
            return False


def adb_install(source_path):
    """
    Install package to android device
    :param source_path: local path of the app
    :return:
    """

    # -d is to allow downgrade of apk
    # -r is to reinstall existing apk
    if os_platform == 'osx':
        cmd = './adb_osx/adb install -d -r {}'.format(source_path)
    elif os_platform == 'win':
        cmd = 'adb_win/adb.exe install -d -r {}'.format(source_path)
    print('Installing {}'.format(source_path))

    state = subprocess.check_output(cmd, shell=True)
    state_strings = state.splitlines()

    # get the last line from the stdout usually adb produces a lot lines of output
    if state_strings[-1] == "Success":  # apk installed
        return INSTALL_OK

    # when here, means something strange is happening
    if "Failure" in state_strings[-1]:
        if "[INSTALL_FAILED_ALREADY_EXISTS]" in state_strings[-1]:  # apk already exists
            return INSTALL_EXISTS
        else:
            return INSTALL_FAILURE  # general failure


def rename_fix(old_name_list, apk_path):
    """
    replaces whitespaces from app name with underscores
    :param old_name_list:
    :param apk_path:
    :return:
    """
    new_name_list = []
    n = len(old_name_list)
    for index in range(n):
        if old_name_list[index].find(' '):
            new_name_list.append(old_name_list[index].replace(' ', '_'))
            # print("Fixing name: {} -> {}".format(old_name_list[index], new_name_list[index]))
        else:
            new_name_list.append(old_name_list[index])
    # rename files
    for index in range(n):
        os.rename(apk_path + os.sep + old_name_list[index], apk_path + os.sep + new_name_list[index])
    return new_name_list


def curr_dir_fix():
    """
    checks if whitespace are in the path
    :return:
    """
    print("Current dir is: {}".format(os.curdir))
    if os.curdir.find(" ") == -1:
        print("No need for current directory fix !")
    else:
        print("Current directory needs a fix\n")


def start_up_msg():
    print('Apk Mass install Utility \nVersion: 2.0\n')
    print('Author: Evangelos Mouroutsos\nContact: mvaggelis@gmail.com\n\n')


def human_time(start, end):
    hours, rem = divmod(end - start, 3600)
    minutes, seconds = divmod(rem, 60)
    print("Elapsed time {:0>2}:{:0>2}:{:05.2f}".format(int(hours), int(minutes), seconds))


def parse_args():
    # parse arguments
    parser = argparse.ArgumentParser(description='Simple Backup / Restore  of Android apps')
    parser.add_argument('-b', '--backup', help='perform device back up', action='store_true')
    parser.add_argument('-i', '--install', type=str,
                        help='restore back up to device from path. Path can be a folder, zip file or encrypted archive',
                        required=False)
    parser.add_argument('-a', '--archive', help='create  zip archive after back up, used with -b flag',
                        action='store_true')
    parser.add_argument('-e', '--encrypt', help='encrypt  zip archive after backup used with -b -a flags',
                        action='store_true')
    parser.add_argument('-v', '--verbose', help='Print verbose messages during execution', action='store_true')

    args = parser.parse_args()
    return args.backup, args.install, args.archive, args.encrypt, args.verbose


def summary(install_state):
    # check install state and report failures
    print("\n\nSummary: ")
    success_count = 0
    fail_count = 0
    not_changed = 0
    for index in range(len(install_state)):
        if install_state[index] == INSTALL_FAILURE:
            fail_count = fail_count + 1
        elif install_state[index] == INSTALL_EXISTS:
            not_changed = not_changed + 1
        elif install_state[index] == INSTALL_OK:
            success_count = success_count + 1
    print("Installed: {} | Not Changed:{} | Failed:{}".format(success_count, not_changed, fail_count))


def main():
    start_up_msg()
    backup, install, archive, encrypt, verbose = parse_args()

    adb_kill()  # kill any instances of adb before starting if any
    adb_start()  # start an instance of adb server

    t_start = timer()

    if backup:
        # generate filename from current time
        backup_file = str(datetime.utcnow()).split('.')[0].replace(' ', '_').replace(':', '-')
        if not os.path.exists(backup_file):
            os.mkdir(backup_file)
        else:
            raise ValueError("Folder {} already exists".format(backup_file))

        print("Listing installed apk's in device...\n")
        pkgs = package_management(pkg_flags['user'])  # get user installed packages

        # get full path on the android filesystem for each installed package
        pkg_path = []
        for i in pkgs:
            path = get_package_full_path(i)
            print("{:40.40} Path: {:60.60}".format(i, path))
            pkg_path.append(path)

        p = []  # list with dictionaries
        for i in range(0, len(pkgs)):
            p.append({pkgs[i]: pkg_path[i]})

        num_apk = len(p)
        print("\nFound {} installed packages\n".format(num_apk))

        progress = 0
        for i in p:  # i is dict {package name: package path}
            progress += 1
            print("[{:3d}/{:3d}]  pulling ... {}".format(progress, num_apk, i[list(i)[0]]))

            # get apk from device
            pull_apk(i)

            # move apk to back up directory
            shutil.move(list(i)[0] + ".apk", os.path.join(backup_file, list(i)[0] + ".apk"))

        if archive:
            print("\nCreating zip archive: {}.zip".format(backup_file))
            make_zip(backup_file, backup_file + ".zip")
            if os.path.exists(backup_file):
                shutil.rmtree(backup_file)

        if encrypt:
            key = input("Enter password for encryption:")
            a = AesEncryption(key)
            print('\nEncrypting archive {} this may take a while...'.format(backup_file + ".zip"))
            a.encrypt(backup_file + ".zip", backup_file + ".aes")

            if os.path.exists(backup_file + ".zip"):
                os.remove(backup_file + ".zip")

        print("\nBack up finished")

    if install:
        clean_up = []  # list of file names to delete after operation
        if os.path.exists(install):
            if os.path.isdir(install):  # install from folder
                print("\nRestoring back from folder: {}".format(install))
                apk_path = install
            elif os.path.isfile(install):  # install from file
                filename, file_extension = os.path.splitext(install)
                if file_extension == '.zip':  # install from zip archive
                    print("\nRestoring back up from zip archive: {}".format(install))
                    print("\nUnzipping {} ...".format(install))
                    extract_zip(install, filename)

                    apk_path = filename

                    clean_up.append(filename)

                elif file_extension == '.aes':  # install from encrypted archive
                    print("\nRestoring back up from encrypted archive: {}".format(install))
                    key = input("Enter password for decryption:")
                    a = AesEncryption(key)
                    print('\nDecrypting back up {} this may take a while...'.format(install))
                    a.decrypt(install, filename + ".zip")
                    print("Unzipping archive this may take also a while...")
                    extract_zip(filename + ".zip", filename)

                    apk_path = filename

                    clean_up.append(filename + ".zip")
                    clean_up.append(filename)
        else:
            raise ValueError("File doesn't exist")

        files = os.listdir(apk_path)  # list all files in apk directory
        apk = []  # list holds the apk found in directory
        for file in files:
            if file.endswith(".apk"):  # separate the apk file by extension in an other list
                apk.append(file)

        # fix apk name replace space character with '_'
        fixed_name_list = rename_fix(apk, apk_path)

        # find total installation size of apk's
        size = []
        for file in fixed_name_list:
            size.append(  # find file size for each apk
                os.path.getsize(os.path.join(apk_path, file))
            )

        print('\nTotal Installation Size: {0:.2f} MB'.format(sum(size) / (1024 * 1024)))
        print('-' * 10)

        install_state = []
        progress = 0

        for apk in fixed_name_list:
            progress += 1
            print("[{:3d}/{:3d}] Installing {} ...".format(progress, len(fixed_name_list), apk))
            s = adb_install(apk_path + os.sep + apk)
            install_state.append(s)

        summary(install_state)

        try:
            clean_up
        except NameError:
            pass
        else:
            for f in clean_up:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.isfile(f):
                    os.remove(f)

        print("\nRestore  finished")

    human_time(t_start, timer())

    adb_kill()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("Received Interrupt")
