"""Module holds all possible exceptions mass apk can raise."""


class MassApkError(BaseException):
    """Base exception for massapk."""


class MassApkFileNotFoundError(MassApkError):
    """Exception raised when apk file not found in device."""
