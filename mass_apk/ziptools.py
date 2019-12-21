import os
import zipfile

__all__ = ["extract_zip", "make_zip"]


def print_info(archive_name):
    zf = zipfile.ZipFile(archive_name)
    for info in zf.infolist():
        print(info.filename)


def zipdir(path, zipf):
    if os.path.isdir(path):
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
        abs_src = os.path.abspath(path)
        apks = []
        for file in files:
            if file.endswith(".apk"):
                apks.append(file)

        iteration = len(apks)

        count = 0

        for apk in apks:
            # don't preserver folder structure inside zip file
            absname = os.path.abspath(os.path.join(path, apk))
            arcname = absname[len(abs_src) + 1 :]
            zipf.write(os.path.join(path, apk), arcname)

            # update progress bar
            count += 1


def make_zip(path, output):
    zipf = zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED)
    zipdir(path, zipf)
    zipf.close()


def extract_zip(zip_file, output):
    if zipfile.is_zipfile(zip_file):
        zip = zipfile.ZipFile(zip_file, "r")

        # create output directory if doesn't exist
        if not os.path.exists(output):
            os.makedirs(output)

        iteration = len(zip.namelist())

        count = 0

        # extract files
        for filename in zip.namelist():
            try:
                zip.extract(filename, output)

                # update progress bar
                count += 1

            except KeyError:
                print("ERROR: Did not find {} in zip file".format(filename))
