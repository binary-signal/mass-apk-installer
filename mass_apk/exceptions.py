class MassApkError(Exception):
    pass


class AdbError(MassApkError):
    pass


class AdbInstallError(AdbError):
    pass
