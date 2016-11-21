"""
 Name:        archive_support

Purpose:  This module automates the installation of multiple apk's, apk is the
           standard executable in Android platform made by Google

 How to:   The module works with 2 command arguments the first is the filepath
           of the adb executable which is the bridge connecting an android phone
           and a pc. The second argument is the directory of the apk to be installed
           in this directory must be only apk files.
           example: python apk_mass_install C:\Android\bin\ C:\Downloads\apks

 Author:      Evaggelos Mouroutsos

 Created:     19/10/2011
 Last Modified: 22/11/2016
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
import zipfile


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print info.filename
       # print '\tModified:\t', datetime.datetime(*info.date_time)

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))

def make_zip(path, output):
    zipf = zipfile.ZipFile(output+'.zip', 'w', zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()

def extractZip(filaname="apk_archive.zip", outputDir="uncompressed"):
    if zipfile.is_zipfile(filaname):
        zip = zipfile.ZipFile(filaname, 'r')
        # list zip contents
        #print_info(arch_path)
        print zip.namelist()

        #create output directory if doesn't exist
        if not os.path.isdir(outputDir):
            os.makedirs(outputDir)

        #extract zip files
        print "extracting files..."
        for filename in zip.namelist():
            if filename.endswith(".apk") == False: #skip non apk files
                continue
            try:
                #data = zip.read(filename)
                zip.extract(filename,outputDir)
            except KeyError:
                print 'ERROR: Did not find %s in zip file' % filename
            else:
                print filename,

            print



