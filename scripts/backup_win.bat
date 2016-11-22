::Run.bat
::Automates installation for apk files
ADB\adb kill-server
apk_mass_install -m backup -d backup
