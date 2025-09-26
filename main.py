# Source Generated with Decompyle++
# File: main.pyc (Python 3.10)

import logging
import math
import sys
import time
from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt, QEvent, QObject, QUrl
from PySide6.QtGui import QIcon, QMovie, QPixmap, QFontDatabase, QFontMetrics, QDesktopServices, QShortcut, QKeySequence, QTransform
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QDialog, QWidget, QInputDialog
from cartclinic.gui import CartClinic
from config import __version__, __version_sha__
from flashing_tool.chromatic import Chromatic, ChromaticError
from flashing_tool.chromatic_subprocess import ProcessManifest, WaitForTime, DownloadFirmware, DetectVersionSubprocess, reset_fpga
from flashing_tool.config_parser import ConfigParser
from flashing_tool.constants import APP_NAME, CHROMATIC_MANUAL_LINK, MRUpdaterFeature
from flashing_tool.gui import ChangelogDialog, ConsentDialog, ErrorDialog
from flashing_tool.gui.generated import Ui_SystemTab, Ui_CartClinicTab, Ui_AboutScreen, Ui_SystemConnectScreen, Ui_SystemCheckScreen, Ui_SystemErrorScreen, Ui_SystemInternetScreen, Ui_SystemUpdateScreen, Ui_SystemUpdatingScreen, Ui_SystemUpToDateScreen, Ui_SystemSuccessScreen
from flashing_tool.initializer import configure_usb_backend, configure_logging, check_os_permissions, ApplicationStartupError, GowinDriverIsMissingError, install_gowin_driver, PrivilegeEscalationError
from flashing_tool.ui_flasher_form import Ui_FlasherForm
from flashing_tool.ui_util import UITab
from flashing_tool.util import ChromaticFirmwarePackage, MRUpdaterManifestData, S3FirmwareInfo, is_env_dev, get_openfpga_loader_bin_path
from flashing_tool.features import FeatureManager
from libpyretro.feature_api import FeatureAPIClient
flashing_tool_logger = logging.getLogger('mrupdater')
if is_env_dev():
    FEATURE_API_URL = 'https://8xlzcdo2o6.execute-api.us-east-1.amazonaws.com'
else:
    FEATURE_API_URL = 'https://7hcmw5socl.execute-api.us-east-1.amazonaws.com'
feature_manager = FeatureManager(FeatureAPIClient(FEATURE_API_URL))
# WARNING: Decompyle incomplete
