# Source Generated with Decompyle++
# File: constants.pyc (Python 3.10)

from enum import Enum
import os
import subprocess
from platformdirs import user_data_dir
APP_NAME = 'MRUpdater'
APP_AUTHOR = 'ModRetro'
APP_DATA_DIR = user_data_dir(APP_NAME, APP_AUTHOR)
SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
CHROMATIC_MANUAL_LINK = 'https://modretro.com/pages/chromatic-manual'

class MRUpdaterFeature(Enum, str):
    PREVIEW_FIRMWARE = 'mrupdater.system:preview-firmware'
    ROLLBACK_FIRMWARE = 'mrupdater.system:rollback-firmware'

