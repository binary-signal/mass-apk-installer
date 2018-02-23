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
You will need to have python 3 installed plus two python dependencies py3-progressbar and pycrypto. You can do that by opening a terminal and typing the following command

    pip install -r requirements.txt
    or
    pip install  py3-progressbar && pip install pycrypto

Also you can you download precompiled binaries for Windows, Linux, MacOS from [here](https://github.com/binary-signal/mass-apk-installer/releases)


## 0x2: Use cases 

## For python (All OS's supported)

	# back up to folder created automaticaly
	$python3 mass-apk-installer.py -b
	
	# back up to a zip file created automaticaly 
	$python3 mass-apk-installer.py -b -a
	
	# back up to encrypted zip file created automaticaly
	$python3 mass-apk-installer.py -b -a -e
	
	#restore from folder 
	$python3 mass-apk-installer.py -i 2018-02-12_04-47-25
	
	#restore from zip file
	$python3 mass-apk-installer.py -i 2018-02-12_04-47-25.zip
	
	#restore from encrypted zip file
	$python3 mass-apk-installer.py -i 2018-02-12_04-47-25.aes

## For Binaries (Linux, MacOS)
	# back up to folder created automaticaly
	$./mass-apk-installer.py -b
	
	# back up to a zip file created automaticaly 
	$./mass-apk-installer.py -b -a
	
	# back up to encrypted zip file created automaticaly
	$./mass-apk-installer.py -b -a -e
	
	#restore from folder 
	$./mass-apk-installer.py -i 2018-02-12_04-47-25
	
	#restore from zip file
	$./mass-apk-installer.py -i 2018-02-12_04-47-25.zip
	
	#restore from encrypted zip file
	$./mass-apk-installer.py -i 2018-02-12_04-47-25.aes
	
## For Binaries (Windows)
	# back up to folder created automaticaly
	mass-apk-installer.exe -b
	
	# back up to a zip file created automaticaly 
	mass-apk-installer.exe -b -a
	
	
	#restore from folder 
	mass-apk-installer.exe -i 2018-02-12_04-47-25
	
	#restore from zip file
	mass-apk-installer.exe -i 2018-02-12_04-47-25.zip

Notice: For Mass Apk Installer Windows binaries encryption of back up's isn't supported. If you run Mass Apk installer on a Windows machine and want to use encryption run the software as python code.
	

## 0x3: Command Line Arguments
    -b, --backup  | Perform device back up
    -i, --install | Restore back up to device from path. Path can be a folder, zip file or encrypted archive   
    -a, --archive | Create  zip archive after back up, used with -b flag
    -e, --encrypt | Encrypt  zip archive after backup used with -b -a flags


