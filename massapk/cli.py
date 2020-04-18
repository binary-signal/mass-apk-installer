import os
import shutil
import sys
from time import sleep
import pathlib
from typing import List, Optional, Union

import click

from massapk import __version__
from massapk import _logger as log
from massapk import adb
from massapk.adb import Adb
from massapk.apk import AdbError, map_apk_paths
from massapk.exceptions import MassApkFileNotFoundError
from massapk.helpers import elapsed_time
from massapk.ziptools import unzipify, zipify


# def parse_args() -> argparse.Namespace:
#     """Argument parser for mass-apk"""
#     parser = argparse.ArgumentParser(prog="mass-apk")
#     subparsers = parser.add_subparsers(
#         title="commands", dest="command", required=True, help="help for commands"
#     )
#
#     # create sub parser for "backup" command
#     backup_sub = subparsers.add_parser("backup", help="backup help")
#     backup_sub.add_argument(
#         "-f",
#         "--flag",
#         type=adb.PackageFlag,
#         default=adb.PackageFlag.USER,
#         help="Specify which apks to backup. Defaults to  user apks.",
#     )
#
#     backup_sub.add_argument(
#         "-p",
#         "--path",
#         type=str,
#         default=os.getcwd(),
#         help="Folder or Path on filesystem for saving back up",
#     )
#     backup_sub.add_argument(
#         "-a",
#         "--archive",
#         action="store_true",
#         help="compress back up folder into zip file",
#     )
#
#     # create the parser for "restore" command
#     restore_sub = subparsers.add_parser("restore", help="help for restore")
#     restore_sub.add_argument(
#         "-p",
#         "--path",
#         type=str,
#         required=True,
#         help="Back up File or Folder to restore from",
#     )
#
#     restore_sub.add_argument(
#         "-c",
#         "--clean",
#         action="store_true",
#         help="remove back up File or Folder defined in --path after restoring",
#     )
#
#     return parser.parse_args()


def main():
    """Main function"""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(1)


@click.group()
@click.pass_context
def cli(ctx):
    """
    A CLI for ProtonVPN.
    Usage:
        massapk (b | backup) [<path>] [-l <list_flag>] [-a | --archive]
        massapk (r | restore) [<path>]  [-c | --clean]
        massapk (-h | --help)
        massapk (-v | --version)
    Options:
        -a, --archive       Convert back folder into zip archive.
        -r, --random        Select a random ProtonVPN server.
        --cc CODE           Determine the country for fastest connect.
        --sc                Connect to the fastest Secure-Core server.
        --p2p               Connect to the fastest torrent server.
        --tor               Connect to the fastest Tor server.
        -p PROTOCOL         Determine the protocol (UDP or TCP).
        -h, --help          Show this help message.
        -v, --version       Display version.
    Commands:
        b, backup          Make Android backup.
        r, restore         Restore back to Android device.
    Arguments:
        <servername>        Servername (CH#4, CH-US-1, HK5-Tor).
    """
    pass


@click.option(
    "--list_flag",
    "-l",
    default="3",
    type=click.Choice(["3", "S"], case_sensitive=True),
    help="Indicates which APK file to add to the backup",
)
@click.option(
    "--archive",
    "-a",
    is_flag=True,
    help="Store backup into a zip archive  instead of a directory",
)
@click.argument("path")
@cli.command("backup")
def backup(path: os.PathLike, list_flag: str, archive: bool):
    """
    Back up android device
    """
    if isinstance(path, pathlib.Path) is False:
        path = pathlib.Path(path)

    with Adb() as adb_session:
        # wait for adb-server to detect phone
        while adb_session.state is not adb_session.ConnectionState.CONNECTED:
            sleep(1)

        log.info("Phone device connected")

        # get user installed packages
        apks = adb_session.list_device(list_flag)

        log.info("Discovering apk paths, this may take a while...")
        # get full path on the android filesystem for each installed package

        parsed_paths = map_apk_paths(apks)

        log.info(f"Found {len(parsed_paths)} installed packages")

        try:
            os.makedirs(path)
        except FileExistsError:
            log.error("Back up destination already exists")
            sys.exit(-1)

        for progress, item in enumerate(parsed_paths, 1):
            log.info(f"[{progress:4}/{len(parsed_paths):4}] pulling ... {item.name}")
            try:
                adb_session.pull(item.fullpath)  # get apk from device
            except AdbError:
                log.error(f"Meow here is a warning for `{item.name}` apk")
                continue

            # all apks retrieved with adb are saved under the same name,  `base.apk`
            # time to use a handy AbsPath named tuple to set correct name to apk pulled with adb
            # this is the correct name of the apk relative to the filesystem
            dest = os.path.join(path, f"{item.name}.apk")
            shutil.move(f"base.apk", dest)

    if archive:
        log.info(f"Creating zip archive: {path}.zip, this may take a while")
        zipify(path, path.parent / (path.name + ".zip"))
        shutil.rmtree(path)

    log.info("Back up done.")


@click.option(
    "--clean", is_flag=True, help="Remove files after finish restoring the backup"
)
@click.argument("path", type=click.Path(exists=True))
@cli.command("restore")
def restore(path: Union[os.PathLike, str], clean: bool):
    """

    :param path:
    :param clean:bool delete folder or files used by restore command before function returns
    :return: None

    :raises MassApkFileNotFoundError
    """
    try:
        os.path.exists(path)
    except FileNotFoundError as error:
        raise MassApkFileNotFoundError(
            f"Oups, the path for back file or folder ` {path}` is missing !"
        )

    with Adb() as adb_session:

        # wait for adb-server to detect phone
        while adb_session.state is not adb.ConnectionState.CONNECTED:
            sleep(1)

        cleanup_todo = list()  # keep track of files/dir to delete before returning

        if os.path.isdir(path):  # restore a folder back up
            log.info(f"Restoring back up from path `{path}` *  *Folder*")
            root_dir_back_up = path

        elif (
                os.path.isfile(path) and os.path.splitext(path)[1] == ".zip"
        ):  # restore a zip archive back up
            log.info(f"Restoring back up from path {path} *  *Zip*")
            extract_to = os.path.splitext(path)[0]
            unzipify(zip_file=path, dest_dir=extract_to)
            root_dir_back_up = extract_to  # set as path root the folder with apk extracted from zip file
            cleanup_todo = list([extract_to, path])

        apks = [file for file in os.listdir(root_dir_back_up) if file.endswith(".apk")]

        # calculate total installation size
        size = [os.path.getsize(os.path.join(root_dir_back_up, apk)) for apk in apks]

        log.info(
            "Total Installation Size: {0:.2f} MB".format(sum(size) / (1024 * 1024))
        )

        for progress, apk in enumerate(apks, 1):
            log.info(f"[{progress}/{len(apks)}] Installing {apk}")
            # adb_session.push(os.path.join(root_dir_back_up, apk))

        if clean:
            map(
                lambda f: shutil.rmtree(f) if os.path.isdir(f) else os.remove(f),
                cleanup_todo,
            )

    log.info("Restore  done")
