"""Test module for mass apk."""

from mass_apk import __version__


def test_version():
    assert __version__ == '0.3.1'



def test_start_server():
    from mass_apk import adb
    from mass_apk.exceptions import MassApkError

    errored = False
    try:
        adb.stop_server()
        adb.start_server()
        adb.stop_server()
    except MassApkError:
        errored = True
    assert not errored

def test_platform():
    import mass_apk

    assert mass_apk.detect_platform().value == "osx"


def test_exec_command():
    from mass_apk.adb import Adb

    output = Adb().exec_command("help")