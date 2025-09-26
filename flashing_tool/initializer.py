# Source Generated with Decompyle++
# File: initializer.pyc (Python 3.10)

import ctypes
import glob
import logging
import logging.handlers as logging
import os
import pathlib
import shutil
import stat
import subprocess
import sys
from flashing_tool.util import resolve_path
_LIBUSB_DLL = 'libusb-1.0.dll'
LOG_FORMAT = '[%(asctime)s] [%(module)s.%(funcName)s:%(lineno)d] - %(levelname)s -- %(message)s'
LOG_FILE_MAX_SIZE = 5242880
exec_path = getattr(sys, '_MEIPASS', pathlib.Path(__file__).parent.parent.absolute())

class ApplicationStartupError(Exception):
    '''Exception class for when the application cannot start up
    because of an unmet pre-requisite'''
    pass


class GowinDriverIsMissingError(ApplicationStartupError):
    '''Exception raised the Gowin driver cannot be found'''
    pass


class PrivilegeEscalationError(ApplicationStartupError):
    '''Exception class for when privilege escalation to run as Administrator on
    Windows fails'''
    pass


def configure_logging():
    if hasattr(sys, '_MEIPASS') and 'MRUPDATER_DEBUG' not in os.environ:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    logger = logging.getLogger('mrupdater')
    logger.setLevel(log_level)
        # Incomplete decompilation - manual review needed
        pass
def configure_usb_backend():
    '''When the app is in packaged form (bundle or EXE), the default libusb
    search behavior is modified by the `pyi_rth_usb` PyInstaller USB hook.
    which sets the search path to the root path.

    This function therefore ensures that the libusb library is always accessible
    when the app is running in both local dev and consumer mode
    '''
    search_path = os.path.join(exec_path, 'lib', sys.platform)
    if not os.path.isdir(search_path) and os.environ['PATH'].startswith(search_path):
        os.environ['PATH'] = f'''{search_path};{os.environ['PATH']}'''
    if hasattr(sys, '_MEIPASS') or sys.platform == 'win32':
        src_path = os.path.join(search_path, _LIBUSB_DLL)
        dest_path = os.path.join(exec_path, _LIBUSB_DLL)
        if not os.path.exists(dest_path):
            shutil.copy(src_path, dest_path)
            return None
        return None
    return None


def check_os_permissions():
    '''Check the os and verify the app has elevated permissions'''
    if hasattr(sys, '_MEIPASS') is False:
        return None
    if None.platform == 'win32':
        run_as_admin()
        _ensure_gowin_driver_is_installed()
        return None
    if None.platform == 'darwin':
        exit_if_mounted_volume()
        return None
    if None.platform == 'linux':
        ensure_udev_rules_exist()
        return None


def run_as_admin():
    '''Relaunch the script with administrative privileges if not already elevated'''
    if sys.platform != 'win32':
        return None
    if None.windll.shell32.IsUserAnAdmin():
        return None
    script = None.executable
    params = ' '.join((lambda .0: [ f'''"{arg}"''' for arg in .0 ])(sys.argv))
        # Assignment completed
def exit_if_mounted_volume():
    '''Make sure the app is not running from a mounted volume'''
    app_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
    if app_dir.startswith('/Volumes'):
        raise ApplicationStartupError('The application cannot be run from .dmg file.  Please move it to your Applications folder and relaunch.')


def ensure_udev_rules_exist():
    '''
    Verify that ALL the udev rules are installed

    This involves the following:

    - Checking for presence of the .rules files in /etc/udev/rules.d
    - Ensuring that the permissions are properly set to 644 on these
      files
    '''
    if sys.platform != 'linux':
        return None
    source_dest_map = None
    for rule in glob.glob(f'''{exec_path}/resources/linux/*.rules'''):
        filename = pathlib.Path(rule).name
        dest_file = f'''/etc/udev/rules.d/{filename}'''
        if os.path.exists(dest_file) is False:
            source_dest_map[rule] = dest_file
    if len(source_dest_map) == 0:
        return None
    if None.getuid() != 0:
        raise ApplicationStartupError(f'''The required udev rules are missing.\nTo ensure they are installed, please run the application as the root user. \n\nYou will only need to do this once. This can be done from the terminal as follows:\nsudo {os.path.realpath(sys.argv[0])}''')
    for src, dest in source_dest_map.items():
        shutil.copy(src, dest)
        os.chmod(dest, stat.S_IWUSR | stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
    subprocess.call('udevadm control --reload-rules && udevadm trigger', True, **('shell',))


def _ensure_gowin_driver_is_installed():
    '''Verifies that the Gowin driver has been installed

    This method is only relevant for Windows systems and is NOT
    mean for use outside of this module
    '''
    pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
def install_gowin_driver():
    '''Installs the Gowin driver

    Once the driver is installed, additional verification is performed
    to determine whether the installation was successful. If this check
    fails, an ApplicationStartupError exception will be raised. However,
    this exception is thrown away and the function returns False. Otherwise,
    the return value is True
    '''
    installer_path = resolve_path('lib/GowinUSBCableDriverV5_for_win7+.exe')
        # Assignment completed