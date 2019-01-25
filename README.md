# mass-apk-installer

![capture](https://i.imgur.com/J48eToL.jpg)


Automate back up or restore of APK's, Android applications to your Android phone. 

## Table of contents:

0x0: Support Information<br>
0x1: How to run the software<br>
0x2: Use cases <br>
0x3: Command Line Arguments<br>






## 0x0: Support Information
Support for the software is provided through the dedicated XDA developers forum post [here](http://forum.xda-developers.com/showthread.php?t=1310742)

## 0x1 How to run the software
You will need to have python 3 installed plus two python dependencies py3-progressbar and pycrypto. You can do that by opening a terminal and typing one of the following commands

    pip install -r requirements.txt
    pipenv install 

Also you can you download precompiled binaries for Windows, Linux, MacOS from [here](https://github.com/binary-signal/mass-apk-installer/releases)


## 0x2: Use cases 

	# back up to folder created automaticaly
	$python3 mass-apk-installer.py backup
	
	# back up to a zip file created automaticaly 
	$python3 mass-apk-installer.py backup -a
	
	# back up to encrypted zip file created automaticaly
	$python3 mass-apk-installer.py backup -a -e
	
	#restore from folder 
	$python3 mass-apk-installer.py restore  2018-02-12_04-47-25
	
	#restore from zip file
	$python3 mass-apk-installer.py restore  2018-02-12_04-47-25.zip
	
	#restore from encrypted zip file
	$python3 mass-apk-installer.py restore 2018-02-12_04-47-25.aes


## 0x3: Command Line Arguments
    backup  [-a] [-e] | make  back up
        -a, --archive | Create  zip archive after back up, used with -b flag
        -e, --encrypt | Encrypt  zip archive after backup used with -b -a flags
    restore [path]    | restore back up to device, path can be a folder, zip file or encrypted archive   
   


