::Run.bat
::Automates installation for apk files
ADB\adb kill-server
apk_mass_install ADB\ apk\ n