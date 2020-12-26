"""Mass Apk Installer.

Automate back up of android devices

 Author:      Evan
 Created:     19/10/2011
 Last Modified: 13/03/2020
 Licence:   MIT

 Copyright (c) 2021, Evan
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions are met:
     * Redistributions of source code must retain the above copyright
       notice, this list of conditions and the following disclaimer.
     * Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions, and the following disclaimer in the
       documentation and/or other materials provided with the distribution.
     * Neither the name of the <organization> nor the
       names of its contributors may be used to endorse or promote products
       derived from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
 ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 vWARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
 DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
 (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
 ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 """

__title__ = "mass-apk"
__version__ = "0.3.1"
__author__ = "Evan @binary-signal"
__license__ = "MIT"

import logging
import os
import sys
from pathlib import Path


def init_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure logging in mass apk package.

    Create a module wide logger instance.
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(fmt="%(name)-17s :: %(levelname)-7s - %(message)s")
    )
    _logger = logging.getLogger(__name__)
    _logger.setLevel(level)
    _logger.addHandler(handler)

    return _logger


logger = init_logging()


pkg_root = Path(os.path.abspath(__file__)).parent


# make platform variable available during import time
from .helpers import detect_platform  # noqa: E402

runtime_platform = detect_platform()

from .adb import Adb  # noqa: E402

adb = Adb()
