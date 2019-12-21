import os
import sys
import platform
import logging

from mass_apk.helpers import OS

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
handler.setFormatter(
    logging.Formatter(fmt="%(name)s :: %(levelname)-8s :: %(message)s")
)
logging.getLogger(__name__).addHandler(handler)
massapk_log = __name__


__all__ = ["massapk_log"]
