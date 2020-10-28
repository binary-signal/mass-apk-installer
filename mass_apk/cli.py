import os
import shutil
import sys
from time import sleep
import pathlib
from typing import  Union

import click

from mass_apk import __version__
from mass_apk import _logger as log
from mass_apk import adb
from mass_apk.adb import Adb
from mass_apk.apk import AdbError, map_apk_paths
from mass_apk.exceptions import MassApkFileNotFoundError, MassApkError
from mass_apk.helpers import elapsed_time
from mass_apk.ziptools import unzipify, zipify


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
    """Invoke main entry point for mass apk."""
    try:
        cli()
    except KeyboardInterrupt:
        print("\nQuitting...")
        sys.exit(1)


@click.group()
def cli():
    """
    Usage:\n
        mass-apk (b | backup) [<path>] [-l <list_flag>] [-a | --archive]\n
        mass-apk (r | restore) [<path>]  [-c | --clean]\n
        mass-apk (-h | --help)\n
        mass-apk (-v | --version)\n
    Options:\n
        -a, --archive       Convert back folder into zip archive.\n
        -r, --random        Select a random ProtonVPN server.\n
        --cc CODE           Determine the country for fastest connect.\n
        --sc                Connect to the fastest Secure-Core server.\n
        --p2p               Connect to the fastest torrent server.\n
        --tor               Connect to the fastest Tor server.\n
        -p PROTOCOL         Determine the protocol (UDP or TCP).\n
        -h, --help          Show this help message.\n
        -v, --version       Display version.\n
    Commands:\n
        b, backup          Make Android backup.\n
        r, restore         Restore back to Android device.\n
    Arguments:\n
        <servername>        Servername (CH#4, CH-US-1, HK5-Tor).\n
    """
    pass


@click.option(
    "--list_flag",
    "-l",
    default="3",
    type=click.Choice(["3", "S"], case_sensitive=True),
    show_default=True,
    help="Indicates which APK file to add to the backup",
)
@click.option(
    "--archive",
    "-a",
    is_flag=True,
    help="Store backup into a zip archive  instead of a directory",
)
@click.argument("path", metavar="PATH", type=click.Path())
@cli.command("backup")
def backup(path: os.PathLike, list_flag: str, archive: bool):
    """Back up android device."""
    if isinstance(path, pathlib.Path) is False:
        path = pathlib.Path(path)
        if path.exists():
            click.echo("Back up path already exists")
            sys.exit(0)

    server = Adb(auto_start=True)

    if server.state is not server.ConnectionState.CONNECTED:
        click.echo("Device not connected.")
        server.stop_server()
        sys.exit(0)
    log.info("Device connected")

    # get user installed packages
    apks = server.list_device(list_flag)

    log.info("Discovering apk paths, this may take a while...")
    # get full path on the android filesystem for each installed package

    parsed_paths = map_apk_paths(apks)

    log.info("Found %s installed packages", len(apks))

    try:
        os.makedirs(path)
    except FileExistsError:
        click.echo("Back up destination already exists", err=True)
        sys.exit(-1)

    for progress, item in enumerate(parsed_paths, 1):
        msg = f"[{progress:4}/{len(parsed_paths):4}] pulling ... {item.name}"
        log.info(msg)
        try:
            server.pull(item.fullpath)  # get apk from device
        except AdbError as error:
            click.echo("Error during pulling {0}\n{1}".format(item, str(error)), err=True)
            server.stop_server()
            sys.exit(-1)

        # all apks retrieved with adb are saved under the same name,  `base.apk`
        # time to use a handy AbsPath named tuple to set correct name to apk
        # pulled with adb this is the correct name of the apk relative to the filesystem
        dest = os.path.join(path, f"{item.name}.apk")
        shutil.move("base.apk", dest)

    if archive:
        log.info(f"Creating zip archive: {path}.zip, this may take a while")
        zipify(path, path.parent / (path.name + ".zip"))
        shutil.rmtree(path)

    server.stop_server()
    log.info("Back up done.")


@click.option(
    "--clean", is_flag=True, help="Remove files after finish restoring the backup"
)
@click.argument("path", type=click.Path(exists=True))
@cli.command("restore")
def restore(path: Union["os.PathLike[str]", str], clean: bool):
    """
    Restore command for mass apk installer

    :param path:
    :param clean:bool delete folder or files used by restore command before function returns
    :return: None

    :raises MassApkFileNotFoundError
    """
    try:
        os.path.exists(path)
    except FileNotFoundError:
        raise MassApkFileNotFoundError(
            f"Oups, the path for back file or folder ` {path}` is missing !"
        )

    server = Adb(auto_start=True)

    # wait for adb-server to detect phone
    if server.state is not server.ConnectionState.CONNECTED:
        click.echo("Device not connected.")
        server.stop_server()
        sys.exit(0)
    log.info("Device connected")

    cleanup_todo = []  # keep track of files/dir to delete before returning

    if os.path.isdir(path):  # restore a folder back up
        log.info(f"Restoring back up from path `{path}` *  *Folder*")
        root_dir_back_up = path

    elif (
        os.path.isfile(path) and os.path.splitext(path)[1] == ".zip"
    ):  # restore a zip archive back up
        log.info(f"Restoring back up from path {path} *  *Zip*")
        extract_to = os.path.splitext(path)[0]
        unzipify(file=path, dest_dir=extract_to)
        root_dir_back_up = extract_to  # set as path root the folder with apk extracted from zip file
        cleanup_todo = [extract_to, path]

    apks = [file for file in os.listdir(root_dir_back_up) if file.endswith(".apk")]

    # calculate total installation size
    size = [os.path.getsize(os.path.join(root_dir_back_up, apk)) for apk in apks]

    log.info(
        "Total Installation Size: {0:.2f} MB".format(sum(size) / (1024 * 1024))
    )

    for progress, apk in enumerate(apks, 1):
        msg = f"[{progress}/{len(apks)}] Installing {apk}"
        log.info(msg
                 )
        try:
            server.push(os.path.join(root_dir_back_up, apk))
        except AdbError as error:
            click.echo("Error during pulling {0}\n{1}".format(apk, str(error)), err=True)
            server.stop_server()
            sys.exit(-1)

    if clean:
        for item in cleanup_todo:
            if os.path.isdir(item):
                shutil.rmtree(item)
            else:
                os.remove(item)

    server.stop_server()
    log.info("Restore  done")
