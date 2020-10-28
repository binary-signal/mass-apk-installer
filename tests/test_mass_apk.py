"""Test module for mass apk."""
import  pytest
from click.testing import CliRunner
from mass_apk import __version__
from mass_apk import cli


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


@pytest.fixture(scope="module")
def runner():
    return CliRunner()


def test_backup_command_no_params(runner):

    response = runner.invoke(cli.backup, input="")
    assert response.exit_code == 2


def test_restore_command_no_params(runner):

    response = runner.invoke(cli.restore, input="")
    assert response.exit_code == 2
