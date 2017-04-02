# mass-apk-installer

Read me file for apk install 
Last Update 2/4/2017

# Table of contents:

	
0x0: Support Information<br>
0x1: Software Description<br>
0x2: How to use this software<br>
0x3: Command Line Arguemnts<br>
0x4: Change Log<br>


## 0x0: Support Information
You can sent requests, bugs and anything you want at: mvaggelis@gmail.com
    Support for the software is provided through xda developers forum see link below
    http://forum.xda-developers.com/showthread.php?t=1310742

## 0x1: Software Description
This software automates the installation and backing up of apk's, Android applications to your Android phone. It 
    uses the adb interface provided by Google to install application via command line prompt to the 
    phone. 

## 0x2: How to use this software

	To do...

## 0x3: Command Line Arguemnts


	Full list of command line arguments available
	-m', '--mode', help='mode can be install or backup ' 
	-s', '--source', help='source folder' 
	-d', '--destination', help='destination folder ' 
	-a', '--archive', help='make a zip archive from backup' 
	-e', '--encryption', help='encrypt archive with AES' 
	-v', '--verbose', help='Print verbose messages during execution' 

## 0x4: Change Log
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
                        
