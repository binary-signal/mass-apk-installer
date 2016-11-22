# mass-apk-installer

Read me file for apk install 
Last Update 22/11/2016 @ 6:50am (UTC +3:00)

Table of contents:

0x0: Contact Information
0x1: Software Description
0x2: How to use this software
0x3: Command Line Arguemnts
0x4: Change Log


0x0: Contact Information

    You can sent requests, bugs and anything you want at: mvaggelis@gmail.com

0x1: Software Description

    This software automates the installation of apk's, Android applications to your Android phone. It 
    uses the adb interface provided by Google to install application via command line prompt to the 
    phone

0x2: How to use this software

    After downloading the rar file apkinstall.rar extract the contents of the archive in your desired
    directory, for example C:\Users\User\Desktop\apkinstall. Then then open the newly creates directory.
    You will notice there are a couple of file and some folders.Put tou apk's into tha apk folder and 
    then double click the run.bat if tou want an ordinary install or double click run_sys.bat to install
    to /system partition. A console will appear and install automatically every apk you put in
    the apk folder. After install the console will exit and you are done. Unplug your phone and enjoy
    your new apps.
    
    Important Notice: In order the program work succesfully you MUST have installed the usb drivers
    for your phone model ! For sony erricson just install pc companion. This sofware was tested in
    Windows Vista x86/x86_x64 & Windows 7 x86/x86_x64, propably Windows Xp SP2 and above is supported.

    Important Notice 2: Installing apk's into /system partition is dangerous !!! use it at your own risk

0x3: Command Line Arguemnts

   	-m', '--mode', help='mode can be install or backup ' 
	-b', '--backup', help='Back apk from device' 
	-s', '--source', help='source' 
	-d', '--destination', help='destination ' 
	-a', '--archive', help='make a zip archive from backup' 
	-e', '--encryption', help='encrypt archive with AES' 
	-i', '--install', help='install apks device' 
	-v', '--verbose', help='Print verbose messages during execution' 

0x4: Change Log

v 2.0 New features

	New version of mass-apk-installer comes with support for osx operating system.Also the command line argumenes are 	  parsed with a new way. Now applicatiion can install apk to android devices and make back of apks from android               devices. 	Backup can be exported to single folder or zip into archives. Archives can also be encrypted with AES if     	   user wants to.

v 1.5 Code maintenance
	  Fixed a bug when trying to create a directory already existed returned errors
	  Added some new future's overide the adb check state and refactored the dummy install process for apk's
	  In the new version the new future's will be added and manipulated via command line arguments
	  For now the new futures are experiemental and not available to stable realese only on beta release
	  
	
v 1.4 Fixed an error about naming of apk'files containing space 
      character. Now the non valid apk names are fixed auto
      matically and space character is replaced with '_' character
      before installation.

v 1.3 Fixed some errors in messages while program was runnning
      Now the apk folder ins't nesseceray to have only apk files, The program automatically seperates
      the apk's in the folder and installs them.It will skip non apks files
      Installation size info is available now 
      Removed some unnecesaty dll files from root folder
      Wait for adb server a few seconds before try to install anything just to make sure the phone is connected
      Wait for user input (Enter) to exit program
      Update documentation

v 1.2 Now it is able to install apk's to /system partition. This future is extremly dangerous use it at  your own rick
      Update messages during runtime
v 1.1 Update Documentation, Minnor bug fixes
                        
