import os
import zipfile

from massapk import _logger as log

__all__ = ["unzippify", "zipify"]


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print(info.filename)


def zipify(src_path, dest_path):
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

        def dir_to_zip(path, ofile: zipfile.ZipFile = zip_file):
            if os.path.isdir(path):
                files = [
                    file
                    for file in os.listdir(path)
                    if os.path.isfile(file) and file.endswith(".zip")
                ]
                abs_src = os.path.abspath(path)

                apks = [file for file in os.listdir(abs_src) if file.endswith(".apk")]

                for apk in apks:

                    # don't preserver folder structure inside zip file
                    absname = os.path.abspath(os.path.join(abs_src, apk))
                    arcname = absname[len(abs_src) + 1 :]

                    log.info("Extracting path "  + path)
                    ofile.write(os.path.join(path, apk), arcname)

        dir_to_zip(src_path, zip_file)


def unzippify(zip_file, output):
    if zipfile.is_zipfile(zip_file):
        zip = zipfile.ZipFile(zip_file, "r")

        # create output directory if doesn't exist
        if not os.path.exists(output):
            os.makedirs(output)

        class ZipItemsIter:
            def __init__(self, zip_obj):
                self.zip_obj = zip_obj

            def __iter__(self):
                iter_abl = iter(self.zip_obj.namelist())
                yield from iter_abl

        for item in ZipItemsIter(zip):
            try:
                zip.extract(item, output)
            except KeyError:
                log.error("Didn't find {} in zip file".format(item))
