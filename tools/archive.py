#!/usr/bin/env python

"""
 Name:        archive.py

 Author:      Evan
 Created:     19/10/2011
 Last Modified: 12/02/2018
 Copyright:   (c) Evan  2018
 Licence:
 Copyright (c) 2018, Evan
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
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 """

from os import listdir
from os.path import isfile, join, isdir, exists, abspath
from os import makedirs
import zipfile
import progressbar as pb


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print(info.filename)


def zipdir(path, zipf):
    if isdir(path):
        files = [f for f in listdir(path) if isfile(join(path, f))]
        abs_src = abspath(path)
        apks = []
        for file in files:
            if file.endswith(".apk"):
                apks.append(file)

        iteration = len(apks)

        # initialize widgets
        widgets = ["progress: ", pb.Percentage(), " ", pb.Bar(), " ", pb.ETA()]
        # initialize timer
        timer = pb.ProgressBar(widgets=widgets, maxval=iteration).start_server()
        count = 0

        for apk in apks:
            # don't preserver folder structure inside zip file
            absname = abspath(join(path, apk))
            arcname = absname[len(abs_src) + 1 :]
            zipf.write(join(path, apk), arcname)

            # update progress bar
            count += 1
            timer.update(count)
        timer.finish()


def make_zip(path, output):
    zipf = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()


def extract_zip(zip_file, output):
    if zipfile.is_zipfile(zip_file):
        zip = zipfile.ZipFile(zip_file, "r")

        # create output directory if doesn't exist
        if not exists(output):
            makedirs(output)

        iteration = len(zip.namelist())

        # initialize widgets
        widgets = ["progress: ", pb.Percentage(), " ", pb.Bar(), " ", pb.ETA()]
        # initialize timer
        timer = pb.ProgressBar(widgets=widgets, maxval=iteration).start_server()
        count = 0

        # extract files
        for filename in zip.namelist():
            try:
                zip.extract(filename, output)

                # update progress bar
                count += 1
                timer.update(count)
            except KeyError:
                print("ERROR: Did not find {} in zip file".format(filename))
        timer.finish()
