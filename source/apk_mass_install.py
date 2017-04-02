#!/usr/bin/env python

"""
 Name:        apk_mass_install

Purpose:  This module automates the installation of multiple apk's, apk is the
           standard executable in Android platform made by Google

 How to:   The module works with 2 command arguments the first is the filepath
           of the adb executable which is the bridge connecting an android phone
           and a pc. The second argument is the directory of the apk to be installed
           in this directory must be only apk files.
           example: python apk_mass_install C:\Android\bin\ C:\Downloads\apks

 Author:      Evaggelos Mouroutsos

 Created:     19/10/2011
 Last Modified: 24/11/2016
 Copyright:   (c) Evaggelos Mouroutsos 2016
 Licence:
 Copyright (c) 2016, Evaggelos Mouroutsos
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
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.   """""

import os
from platform import system
import sys
import time
import shutil
import subprocess
from sqlite_support import db_init, db_connect, db_insert, db_empty_apk_table
from archive_support import extractZip, make_zip
import argparse
from encryption_support import encryption_support



ARCHIVE_NAME = "apk_archive"  # archive options
ARCHIVE_OUTPUT_DIR = "uncompressed"
ARCHIVE_CREATE = True
ARCHIVE_ENCRYPT = True

ENC_SOURCE = None
ENC_DEST = None
AES_KEY = None
BLOCK_SIZE = None

# Flags used for adb package listing
pkg_flags = {'all': "",         # list all packages
             'user': "-3",      # list 3d party packages only (default)
             'system': "-S"}    # list system packages only
BACKUP = 2  # application operation mode
INSTALL = 3
INSTALL_FORCE = False
INSTALL_FAILURE = -1
INSTALL_OK = 1
INSTALL_EXISTS = 2

MODE = 2

os_platform = 'osx'


def get_apk_version(apk):
    cmd = "./aapt dump badging " + apk
    state = subprocess.check_output(cmd, shell=True)
    firstLine = state.splitlines()[0]
    list = firstLine.split(" ")
    list2 = []
    for i in list:
        list2.append(i.split("="))

    # store apk information in dict
    # 'versionCode': "'35'",
    # 'platformBuildVersionName': "'5.1.1-1819727'",
    # 'name': "'cz.google'",
    # 'versionName': "'4.1'"}
    dict = {}
    for i in list2:
        if i[0] == "package:":
            continue
        dict[i[0]] = i[1]

    return dict


def pull_apk(pkgDic):
    """
    Pulls apk specified in pkgDic variable from android device using adb
    renames extracted apk to filename specified in pkgDic key value pair
    pkgDic is an one value dictionary.
    :param pkgDic: {package name : package path}
    :return: None
    """

    pkg_name = pkgDic.keys()

    if os_platform == 'osx':
        cmd ='adb shell cat '+pkgDic[pkg_name[0]]+ ' > ' +"base.apk"
        #cmd = "./adb pull " + pkgDic[pkg_name[0]]
    elif os_platform == 'win':
        cmd = "adb.exe pull " + pkgDic[pkg_name[0] ]
    print(cmd)
    state = subprocess.check_output(cmd,  shell=False)
    print (state)
    if os.path.isfile("base.apk"):
        os.rename("base.apk", pkg_name[0] + ".apk")


def package_managment(PKG_FILTER):
    """
    list all packages installed installed in android device. Results can be
    filtered with PKG_FILTER to get only apk packages you are interested. By default
    listing only 3d party apps.
    :param PKG_FILTER:
    :return:
    """


    if os_platform == 'osx':
        cmd = "./adb shell pm list packages " + PKG_FILTER
    elif os_platform == 'win':
        cmd = "adb.exe shell pm list packages " + PKG_FILTER
    state = subprocess.check_output(cmd, shell=True)
    pkg_raw = state.splitlines()
    pkg = []

    """
    adb returns packages name  in the form
    package:com.skype.raider
    we need to strip package: prefix
    """
    for i in pkg_raw:
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
        cmd = "./adb shell pm path " + pkg_name
    elif os_platform == 'win':
        cmd = "adb.exe shell pm path " + pkg_name

    state = subprocess.check_output(cmd, shell=True)

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
        cmd = './adb start-server'  # command to adb
    elif os_platform == 'win':
        cmd = 'adb.exe start-server'  # command to adb
    state = os.system(cmd)  # execute the command in terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd))
        sys.exit(1)
    print('Make sure your Android phone is connected and debug mode is enabled !')


def adb_kill():
    """
    kills adb server
    """

    print('Killing adb server...')
    if os_platform == 'osx':
        cmd = './adb kill-server'  # command to adb
    elif os_platform == 'win':
        cmd = 'adb.exe kill-server'  # command to adb
    state = os.system(cmd)  # execute command to terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd))
        sys.exit(1)


def adb_state():
    """
    gets the state of adb server if state is device then phone is connected
    """

    if os_platform == 'osx':
        cmd = './adb get-state'
    elif os_platform == 'win':
        cmd = 'adb.exe get-state'

    output = os.popen(cmd)  # command to run
    res = output.readlines()  # res: output from running cmd
    state = output.close()
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd))
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
        cmd = './adb install -d -r ' + str(source_path)
    elif os_platform == 'win':
        cmd = 'adb.exe install -d -r ' + str(source_path)
    print('Installing ' + str(source_path))

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
            print("Fixing name: " + str(old_name_list[index]) + " -> " + str(new_name_list[index]))
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
    print("Current dir is:" + os.curdir)
    if os.curdir.find(" ") == -1:
        print("No need for current directory fix !\m")
    else:
        print("Current directory needs a fix\n")


def start_up_msg():
    print('Apk Mass install Utility \nVersion: 2.0\n')
    print('Author: Evaggelos Mouroutsos\nContact: mvaggelis@gmail.com')


def main():
    start_up_msg()

    # parse arguments
    parser = argparse.ArgumentParser(description='Description of your program')
    parser.add_argument('-m', '--mode', help='mode can be install or backup ', required=True)

    parser.add_argument('-b', '--backup', help='Back apk from device', required=False)
    parser.add_argument('-s', '--source', help='source', required=False)
    parser.add_argument('-d', '--destination', help='destination ', required=False)

    parser.add_argument('-a', '--archive', help='make a zip archive from backup', required=False)
    parser.add_argument('-e', '--encryption', help='encrypt archive with AES', required=False)
    parser.add_argument('-i', '--install', help='install apks device', required=False)
    parser.add_argument('-v', '--verbose', help='Print verbose messages during execution', required=False)

    args = vars(parser.parse_args())

    # detect platform OSX, WIN , LINUX
    if os.name == 'posix' and system() == 'Darwin':
        os_platform = 'osx'
    elif os.name == 'posix' and system() == 'Linux':
        os_platform = 'linux'
    else:
        os_platform = 'win'

    # kill any instance of adb before starting
    adb_kill()

    # start an instance of adb server
    adb_start()

    if args['mode'] == 'backup':
        # create destination folder if doesn't exist on the filesystem
        if args['destination'] != None:
            if not os.access(args['destination'], os.F_OK):
                os.mkdir(args['destination'])
        else:  # make a temp backup/ dir used for archiving
            if not os.access('backup/', os.F_OK):
                os.mkdir("backup/")
        print "Starting back up process..."
        print "Listing installed apk's in device...",
        pkgs = package_managment(pkg_flags['user'])  # get user installed packages

        pkg_path = []
        for i in pkgs:  # get full path on the android filesystem for each package
            pkg_path.append(get_package_full_path(i))

        print "OK"
        # pkgStruct = dict(zip(device_packages, pkg_path))
        p = []  # list with dictionaries
        n = len(pkgs)
        for i in range(0, n):
            p.append({pkgs[i]: pkg_path[i]})
            print "\t" + pkgs[i] + ":" + pkg_path[i]
        print
        app_no = len(p)
        print "Found {0} installed packages".format(app_no)

        # open database to store backed up apk versions
        print
        print "Connecting to database...",
        con = db_connect("backup.db")
        print "OK"

        # reset apl table in database
        db_empty_apk_table(con)

        progress = 1
        for i in p:  # i is dict {package name: package path}
            print "[{}/{}]...pulling".format(progress, app_no) + " " + i[i.keys()[0]]
            pull_apk(i)
            apk_info = get_apk_version(i.keys()[0] + ".apk")
            # print apk_info
            # move to back up directory
            if args['destination'] != None:
                shutil.move(i.keys()[0] + ".apk", args['destination'] + os.sep + i.keys()[0] + ".apk")
            else:
                shutil.move(i.keys()[0] + ".apk", "backup/" + os.sep + i.keys()[0] + ".apk")
            # insert info into database
            db_insert(con, apk_info)
            progress += 1
        if args['archive'] != None:
            print "Creating compressed back up output file" + args['archive']
            make_zip('backup/', args['archive'])
            print "cleaning up"
            shutil.rmtree("backup/")
        if args['encryption'] != None:
            key = raw_input("Enter password for encryption:")
            print('\nEncrypting ...'),
            a = encryption_support(key)
            a.encrypt_aes("archive.zip", "encrypted_aes.aes")
            print "OK"

    if args['mode'] == 'install':
        if args['source'] != None:
            if os.path.isdir(args['source']):  # install from folder specified by user
                print "Installing from folder {}".format(args['source'])
            if os.path.isfile(args['source']):
                if args['source'].endswith(".aes"):  # install from encrypted arcv
                    password = raw_input("Enter password for decryption:")
                    a = encryption_support(password)
                    print "Decrypting....",
                    a.decrypt_aes("encrypted_aes.aes", "decrypted.zip")
                    print "OK"
                    # install from apk folder

        # install from zip file
        raw_apk_path = args['source']
        mode = "normal"

        # debug cur dir fix
        # curr_dir_fix();

        # make the source and target paths good
        apk_path = os.path.abspath(raw_apk_path)

        # change the current directory to adb path directory and start a server
        adb_start()

        print("Wait for 2 seconds...")
        time.sleep(2)

        # get the state of adb server
        if adb_state():
            print('Device Mode, phone is connected')
        else:
            print("Adb Server isn\'t running or phone isn'\t connected !")
            time.sleep(2)
            sys.exit(1)

        file_list = os.listdir(apk_path)  # list all files in apk directory
        list_of_apk = []  # list holds the apk found in directory
        for file in file_list:
            if file.endswith(".apk"):  # separate the apk file by extension in an other list
                list_of_apk.append(file)
        # list holds the size of each apk file
        list_of_size = []

        # fix apk name replace space character with '_'
        fixed_name_list = rename_fix(list_of_apk, apk_path)

        for file in fixed_name_list:  # use the fixed name list
            list_of_size.append(os.path.getsize(
                apk_path + os.sep + file))  # calculate file size for each apk and store the results in a list

        # print the apk in apk directory
        print()
        print('Apk\'s found on directory: ' + apk_path)
        print('----------')
        for index in range(len(fixed_name_list)):
            print("Apk: " + fixed_name_list[index] + " Size: %0.2f mb" % (
                int(list_of_size[index]) / (1024 * 1024)))  # print the name of the apk and the size of it
        print('----------')

        # convert bytes to mb
        print('Total Installation Size: %0.2f mb' % (sum(list_of_size) / (1024 * 1024)))
        print('----------')

        # wait for 2 seconds
        time.sleep(1)

        install_state = []
        apkinstalling = 1
        print('Installing apk\'s')
        for apkinstall in fixed_name_list:
            print("Installing %d... %d" % (apkinstalling, len(fixed_name_list)))
            install_state.append(adb_install(apk_path + os.sep + apkinstall))
        print("\n\nInstallation Completed !!!")
        print "Summary: ",
        # check install state and report failures
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
        print "Installed: {} | Not Changed:{} | Failed:{}".format(success_count, not_changed, fail_count)
        if args['verbose'] != None:
            for index in range(len(install_state)):
                if install_state[index] == INSTALL_FAILURE:
                    print "\t" + fixed_name_list[index] + " failed to install"

        # pull logs from device
        adb_kill()

        # wait for user to press enter to exit
        time.sleep(1)
    print("Bye Bye")


if __name__ == '__main__':
    main()
