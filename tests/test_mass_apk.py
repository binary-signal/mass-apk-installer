from unittest import TestCase

from massapk import __version__


def test_version():
    assert __version__ == '0.1.0'


class TestAdb(TestCase):
    def test_start_server(self):
        from massapk import adb

        try:
            adb.stop_server()
            adb.start_server()
            adb.stop_server()
        except Exception:
            self.fail()
