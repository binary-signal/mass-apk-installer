#-------------------------------------------------------------------------------
# Name:        apk_mass_install
#
# Purpose:  This module automates the installation of multiple apk's, apk is the
#           standard executable in Android platform made by Google
#
# How to:   The module works with 2 command arguments the first is the filepath
#           of the adb executable which is the bridge connecting an android phone
#           and a pc. The second argument is the directory of the apk to be installed
#           in this directory must be only apk files.
#           example: python apk_mass_install C:\Android\bin\ C:\Downloads\apks
#
# Author:      Evaggelos Mouroutsos
#
# Created:     19/10/2011
# Last Modified: 20/9/2012
# Copyright:   (c) Evaggelos Mouroutsos 2011
# Licence:
##Copyright (c) 2011, Evaggelos Mouroutsos
##All rights reserved.
##
##Redistribution and use in source and binary forms, with or without
##modification, are permitted provided that the following conditions are met:
##    * Redistributions of source code must retain the above copyright
##      notice, this list of conditions and the following disclaimer.
##    * Redistributions in binary form must reproduce the above copyright
##      notice, this list of conditions and the following disclaimer in the
##      documentation and/or other materials provided with the distribution.
##    * Neither the name of the <organization> nor the
##      names of its contributors may be used to endorse or promote products
##      derived from this software without specific prior written permission.
##
##THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
##ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
##WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
##DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
##DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
##(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
##LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
##ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
##(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
##SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#-------------------------------------------------------------------------------
#!/usr/bin/env python
import os
import sys
import time
import shutil

#enable debug messages
DEBUG = 0
#dummy install
D_INSTALL = 0
#overides adb state check
ADB_OVERIDE = 0

# define arguments states

ARGV_LOW = -1
ARGV_HIGH = -2
ARGV_ERROR =-3
ARGV_NONE = 0

MODE_SYS = 0
MODE_NORMAL = 1


#version check
##if(sys.version_info != 'sys.version_info(major=3, minor=2, micro=2, releaselevel=\'final\', serial=0)'):
##    print('The version of python installed isn\'t compatible !')
##    exit(1)

#starts an instance of adb server
def adb_start(adb_path):
    print('Changing working directory to adb excutable...')
    os.chdir(adb_path) #change current directory to the adb executable
    print('Starting adb server...')
    cmd ='adb.exe start-server' #command to adb
    state = os.system(cmd) # execute the command in terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd) )
        sys.exit(1)
    print('Make sure your Android phone is connected and debug mode is enabled !')

#kill an instance of adb server
def adb_kill():
    print('Killing adb server...')
    cmd = 'adb.exe kill-server' #command to adb
    state = os.system(cmd) #execute command to terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd) )
        sys.exit(1)

#install apk
def adb_install(source_path):
    #print (os.getcwd())
    if DEBUG == 1:
        print(source_path)

    cmd = 'adb install ' + str(source_path)
    print('Installing ' + str(source_path))
    if D_INSTALL != 1 :
        state = os.system(cmd) #execute command to terminal
        if state:
            print ('%s: running %s failed' % (sys.argv[0], cmd) )
            return -1
        else:
            return 0


#install apk in system partition
def adb_install_sys(source_path):
    cmd = "adb push " + str(source_path) + " /system/app"
    #debug
    if DEBUG == 1:
        print(cmd)
    print("Installing " + str(source_path))
    state = os.system(cmd) #execute command to terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd) )
        return -1
    else:
        return 0
#get the state of adb server
def adb_state():
    if ADB_OVERIDE == 1:
        return True
    cmd = 'adb get-state'
    output = os.popen(cmd) #command to run
    res = output.readlines() #res: output from running cmd
    state = output.close()
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd) )
        if DEBUG != 1:
            raw_input("Press Enter to exit")
        sys.exit(1)
    for line in res:
        if(str.rstrip(line) == "device"):
            return True
        else:
            return False

#modify permission on /system partition
def adb_perm():
    cmd0 ="adb remount" #mount as read write command
    cmd = "adb shell chmod 777 /system" #change permissions

    #debug
    if DEBUG == 1:
        print(cmd0)
        print(cmd)

    print("Mount /system as read-write partition...")
    state = os.system(cmd0) #execute command to terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd0) )
        if DEBUG != 1:
            raw_input("Press Enter to exit")
        sys.exit(1)

    print("Change /system permissions...")
    state = os.system(cmd) #execute command to terminal
    if state:
        print ('%s: running %s failed' % (sys.argv[0], cmd) )
        if DEBUG != 1:
            raw_input("Press Enter to exit")
        sys.exit(1)

def rename_fix(old_name_list, apk_path):
    new_name_list = []
    for index in range( len( old_name_list)):
        if old_name_list[index].find(' '):
            new_name_list.append( old_name_list[index].replace(' ', '_'))
            print("Fixing name: " + str(old_name_list[index]) + " -> " + str(new_name_list[index]))
        else:
            new_name_list.append( old_name_list[index])
    #rename files
    for index in range(len(old_name_list)):
        os.rename(apk_path+os.sep+old_name_list[index], apk_path+os.sep+new_name_list[index])
    return new_name_list

def start_up_msg():
    print('Apk Mass install Utility for Windows\nVersion: 1.5\n')
    print('Author: Evaggelos Mouroutsos\nContact: mvaggelis@gmail.com')

def prog_usage_msg():
    if (len(os.sys.argv) == 1):
        print("Usage:n")
        print("apk_mass_install argv[1]-dir argv[2]-dir argv[3]-mode")
        print("argv[1] - directory of adb executable")
        print("argv[2] - directory of apk's to be installed")
        print("argv[3] - mode can be \"n\" normal mode or \"s\" for system install")
        print("\n")

#checks the lengths of the arguments and return a code according to each length
def argv_check():
    if (len(os.sys.argv) < 4) :
        return ARGV_LOW
    elif(len(os.sys.argv) > 7):
        return ARGV_HIGH
    elif (len(os.sys.argv) == 1):
        return ARGV_NONE
def argv_parse():
    if(os.sys.argv[3] == 'n'):
        return MODE_NORMAL
    elif(os.sys.argv[3] == 's'):
        return MODE_SYS
    else:
        return ARGV_ERROR

def curr_dir_fix():
    print("Current dir is:" + os.curdir);
    if(os.curdir.find(" ") == -1):
        print("No need for current directory fix !\m");
    else:
        print("Current directory needs a fix\n");



################################################################################
################################################################################
################################################################################
################################################################################
################################################################################
def main():
    #print start into messages
    start_up_msg()

    #check arguments length
    if argv_check() == ARGV_HIGH:
        print("Too many arguments !")
        sys.exit(ARGV_HIGH)
    elif argv_check() == ARGV_LOW:
        print("Too less arguments !")
        sys.exit(ARGV_LOW)
    elif argv_check() == ARGV_NONE:
        prog_usage_msg()
        sys.exit(ARGV_NONE)

    #debug print number of arguments
    if DEBUG ==1 :
        print("Number of argv: " + str(len(os.sys.argv)))
    #parse the arguments
    raw_adb_path = os.sys.argv[1]
    raw_apk_path = os.sys.argv[2]

    mode = ""

    if argv_parse() == MODE_NORMAL:
        mode = "normal"
    elif argv_parse() == MODE_SYS:
        mode == 'system'
        print("WARNING: Installing apk in system partition isn't safe !!!")
        if DEBUG != 1:
            raw_input("Press Enter to Continue !!!")

    #debug cur dir fix
    if DEBUG == 1 :
        curr_dir_fix();
    #debug
    if DEBUG == 1 :
        print('Raw adb path: ' + raw_adb_path)
        print('Raw apk path: ' + raw_apk_path)
        print("Mode: " + mode)



    #make the source and target paths good
    adb_path = os.path.abspath(raw_adb_path)
    apk_path = os.path.abspath(raw_apk_path)

    #debug
    if DEBUG ==1 :
        print('Raw adb path: ' + adb_path)
        print('Raw apk path: ' + apk_path)

    #check if the adb and apk paths exists
    adb_ex =os.path.exists(adb_path)
    if adb_ex == False:
        print("Adb directory doesn't exitsts !")
        if DEBUG != 1:
            raw_input("Press Enter to exit")
        sys.exit(1)
    apk_ex =os.path.exists(apk_path)
    if apk_ex == False:
        print("Apk directory doesn't exitsts !")
        if DEBUG != 1:
            raw_input("Press Enter to exit")
        sys.exit(1)

    #check if the adb and apk paths are directories

    adb_type = os.path.isdir(adb_path)
    apk_type = os.path.isdir(apk_path)


    if adb_type != True:
        print('The specified Adb path isn\'t a directory')
        sys.exit(1)
    #debug
    if DEBUG ==1 :
        print("Adb type: directory !")
    if apk_type != True:
        print('The specified apk path isn\'t a directory')
        sys.exit(1)
    #debug
    if DEBUG ==1 :
        print("Apk type: dorectory !")

    #extension for apk's
    extension = ".apk"

    #change the current directory to adb path directory and start a server
    adb_start(adb_path)

    #wait for 5 seconds
    print("Wait for 5 seconds...")
    time.sleep(5)

    #get the state of adb server
    if D_INSTALL != 1 :
        if adb_state() == False:
            print("Adb Server isn\'t running or phone isn'\t connected !")
            time.sleep(2)
            sys.exit(1)
        else:
            print('Device Mode, phone is connected')

    file_list = os.listdir(apk_path) # list all files in apk directory
    list_of_apk = [] #list holds the apk found in directory
    for file in file_list:
        if file.endswith(extension): #seperate the apk file by extension in an other list
            list_of_apk.append(file)
    #list holds the size of each apk file
    list_of_size = []

    #fix apk name replace space character with '_'
    fixed_name_list = rename_fix(list_of_apk, apk_path)

    ############################################
    for file in fixed_name_list: #use the fixed name list
        list_of_size.append(os.path.getsize(apk_path+os.sep+file)) #calculate file size for each apk and store the results in a list

    #print the apk in apk directory
    print()
    print('Apk\'s found on directory: ' + apk_path)
    print('----------')
    for index in range(len(fixed_name_list)):
       print("Apk: " + fixed_name_list[index] +" Size: %0.2f mb" %(int(list_of_size[index])/(1024*1024))) #print the name of the apk and the size of it
    print('----------')

    #find the total size of installation
    sum =0
    for size in list_of_size:
        sum = sum +int(size)
    sumUp = sum/(1024*1024) #convert bytes to mb

    print('Total Installation Size: %0.2f mb'%(sumUp))
    print('----------')

    #wait for 2 seconds
    time.sleep(2)

    #move installed apk to new folder
    if DEBUG == 1:
        print(os.getcwd)


    if mode == 'system':
        adb_perm()
    install_state = []
    apkinstalling = 1
    print('Installing apk\'s')
    for apkinstall in fixed_name_list:
        print("Installing %d... %d" % (apkinstalling, len(fixed_name_list)))
        if mode == 'system':
                install_state.append( instinstadb_install_sys(apk_path+'\\'+apkinstall))
        else:
            install_state.append( adb_install(apk_path+'\\'+apkinstall))
            apkinstalling = apkinstalling + 1

    #change directory to apk folder and move succesfull installed files in /apk/installed
    cmd = "cd .."
    state = os.system(cmd)
    if state:
        print("Can't change directory to root program folder")
        time.sleep(2)
        sys.exit(-5)
    cmd1 = "cd apk"
    if state:
        print("Can't change directory to apk")
        time.sleep(2)
        sys.exit(-5)
    #make the new directory
    ###
    if os.access("installed", os.F_OK) :
        print("Directory installed already exists")
    else :
        print("Creating installed directory")
        os.mkdir("installed")


    ####
    for index in range(len(install_state)):
        if install_state[index] == 0:
            shutil.move(fixed_name_list[index], "installed"+os.sep)
    print("Installation Completed !!!")
    adb_kill()

    #wait for user to press enter to exit
    time.sleep(1)
    if DEBUG != 1:
        raw_input("Press Enter to exit")
    print("Bye Bye")

if __name__ == '__main__':
    main()








