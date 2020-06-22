import os
import zipfile

__all__ = ["unzipify", "zipify"]


def zipify(src_path, dest_path):
    """
    Compress a folder into a zip archive
    """

    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

        def dir_to_zip(path, out_file: zipfile.ZipFile = zip_file):
            if os.path.isdir(path):
                # FIXME: should keep files ?
                files = [item for item in os.listdir(path) if os.path.isfile(item) and item.endswith(".zip")]
                abs_src = os.path.abspath(path)

                apks = [item for item in os.listdir(abs_src) if os.path.isfile(item) and item.endswith(".apk")]

                for apk in apks:
                    # don't preserver folder structure inside zip file
                    absname = os.path.abspath(os.path.join(abs_src, apk))
                    arcname = absname[len(abs_src) + 1 :]

                    out_file.write(os.path.join(path, apk), arcname)

        dir_to_zip(src_path, zip_file)


def unzipify(zip_file, dest_dir=None):
    """
    Decompress zip file into folder

    If no destination directory is specified,
    use the current working directory.
    """

    if dest_dir is None:
        dest_dir = os.getcwd()
    if zip_file.is_zipfile(zip_file):
        # create output directory if doesn't exist
        os.makedirs(dest_dir)
        with zipfile.ZipFile(zip_file, "r") as zip_handle:
            zip_handle.extractall(dest_dir)
