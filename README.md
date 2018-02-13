# mass-apk-installer

Read me file for apk install 
Last Update 12/02/2018

# Table of contents:

0x0: Support Information<br>
0x1: Software Description<br>
0x2: How to use this software<br>
0x3: Command Line Arguemnts<br>
0x4: Change Log<br>


## 0x0: Support Information
You can sent requests, bugs and anything you want at: mvaggelis@gmail.com
    Support for the software is provided through xda developers forum 
    http://forum.xda-developers.com/showthread.php?t=1310742

## 0x1: Software Description
This software automates the installation and back up of APK's, Android applications to your Android phone. It 
    uses the adb interface provided by Google to install apk's via command line prompt to the phone. 

## 0x2 First
You will need to have python 3 to run this software.
Also in odrer to use mass-apk-installer you have to install two python depedencies py3-progressbar and pycrypto you can do that by opening a terminal and typing the following command

pip install -r depedencies.txt

## 0x2: How to use this software

	# back up to folder created automaticaly
	$python3 mass-apk-installer.py -b
	
	# back up to a zip file created automaticaly 
	$python3 mass-apk-installer.py -b -a
	
	# back up to encrypted zp file created automaticaly
	$python3 mass-apk-installer.py -b -a -e
	
	#restore from folder 
	$python3 mass-apk-installer.py -i 2018-02-12_04-47-25
	
	#restore from zip file
	$python3 mass-apk-installer.py -i2018-02-12_04-47-25.zip
	
	#restore from encrypted zip file
	$python3 mass-apk-installer.py -i2018-02-12_04-47-25.aes
	

## 0x3: Command Line Arguemnts
    -b, --backup  | Perform device back up
    -i, --install | Restore back up to device from path. Path can be a folder, zip file or encrypted archive   
    -a, --archive | Create  zip archive after back up, used with -b flag
    -e, --encrypt | Encrypt  zip archive after backup used with -b -a flags
    -v, --verbose | Print verbose messages during execution


## 0x4: Change Log
### v 3.0 Major Update
Now mass-apk-installer is using python version 3, bug fixes in encryption 

### v 2.2 Cleaned code, added support for android nougat

### v 2.0 New features
New version of mass-apk-installer comes with support for osx operating system.Also the command line argumenes are 	  parsed with a new way. Now applicatiion can install apk to android devices and make back of apks from android               devices. 	Backup can be exported to single folder or zip into archives. Archives can also be encrypted with AES 256 	  if user wants to.

### v 1.5 Code maintenance
Fixed a bug when trying to create a directory already existed returned errors Added some new future's overide the adb check state and refactored the dummy install process for apk's.In the new version the new future's will be added and manipulated via command line arguments. For now the new futures are experiemental and not available to stable realese only on beta release
	  
	
### v 1.4 
Fixed an error about naming of apk'files containing space 
character. Now the non valid apk names are fixed auto
matically and space character is replaced with '_' character before installation.

### v 1.3 
Fixed some errors in messages while program was runnning
      Now the apk folder ins't nesseceray to have only apk files, The program automatically seperates
      the apk's in the folder and installs them.It will skip non apks files
      Installation size info is available now 
      Removed some unnecesaty dll files from root folder
      Wait for adb server a few seconds before try to install anything just to make sure the phone is connected
      Wait for user input (Enter) to exit program
      Update documentation

### v 1.2 
Now it is able to install apk's to /system partition. This future is extremly dangerous use it at  your own rick
      Update messages during runtime
### v 1.1 
Update Documentation, Minnor bug fixes
                        