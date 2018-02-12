#!/usr/bin/env bash

# restore from zip file
./apk_mass_install -i archive.zip

# restore from folder
./apk_mass_install -i folder/path

# restore from encrypted zip file
./apk_mass_install -i encrypted.zip
