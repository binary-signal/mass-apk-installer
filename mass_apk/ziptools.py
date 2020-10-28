"""Compression related functions."""

import os
import zipfile
from typing import Optional, Union
from pathlib import Path

__all__ = ["unzipify", "zipify"]


def zipify(src_path: Union[str, os.PathLike], dest_path: Union[str, os.PathLike]):
    """Compress a folder into a zip archive."""
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zip_file:

        def dir_to_zip(path, out_file: zipfile.ZipFile = zip_file):
            abs_src = os.path.abspath(path)

            if os.path.isdir(abs_src):
                apks = [
                    item
                    for item in os.listdir(abs_src)
                    if os.path.isfile(item) and item.endswith(".apk")
                ]

                for apk in apks:
                    # don't preserver folder structure inside zip file
                    abs_path = Path(os.path.join(abs_src, apk))
                    apk_name = abs_path.parts[-1]
                    out_file.write(os.path.join(path, apk), apk_name)

        dir_to_zip(src_path, zip_file)


def unzipify(
    file: Union[str, os.PathLike],
    dest_dir: Optional[Union[str, os.PathLike]] = None,
):
    """Decompress zip file into `dest_dir` path.

    If `dest_dir` is None use current working directory as `dest_dir`
    to extract data .

    raises ValueError if `file` arg is not a zip file.
    """
    if zipfile.is_zipfile(file):
        # create output directory if doesn't exist
        if dest_dir is None:
            dest_dir = os.getcwd()
        else:
            os.makedirs(dest_dir)

        with zipfile.ZipFile(file, "r") as zip_handle:
            zip_handle.extractall(dest_dir)

    raise ValueError(f"Not a zip file {file}")
