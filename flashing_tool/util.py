Unsupported Node type: 12
Unsupported Node type: 12
Unsupported Node type: 12
Unsupported Node type: 12
Unsupported node type 48 in NODE_JOINEDSTR
# Source Generated with Decompyle++
# File: util.pyc (Python 3.10)

import os
import platform
import re
import sys
from config import __env__
from enum import Enum
from dataclasses import dataclass
CONFIG_FILE_NAME = 'config.ini'
CPU_TYPES = {
    'AMD64': 'x86_64',
    'x86_64': 'x86_64',
    'arm64': 'arm64',
    'aarch64': 'arm64' }

class FlashOperation(Enum):
    BOTH = 1
    FPGA = 2
    MCU = 3
    CART = 4

S3FirmwareInfo = dataclass(<NODE:12>)
ChromaticFirmwarePackage = dataclass(<NODE:12>)
CartClinicFirmwarePackage = dataclass(<NODE:12>)
MRUpdaterManifestData = dataclass(<NODE:12>)

def resolve_path(path = None):
    """Returns the absolute for the specified relative path

    The value specified in @param path should be relative to the application's
    entry point, not the module calling resolve_path.
    """
    exec_path = getattr(sys, '_MEIPASS', os.getcwd())
    resolved_path = os.path.abspath(os.path.join(exec_path, path))
    return resolved_path


def split_version_string(aggregate_version):
    '''
    Splits an aggregate version string into its FPGA/MCU components

    :param aggregate_version: Combined version string eg v18.0_0.12.3
    :return:
    '''
    fw_search = re.match('v(\\d+\\.\\d+)_(\\d+\\.\\d+\\.\\d+)', aggregate_version)
    if not fw_search:
        return aggregate_version
    return f'''{fw_search.group(1)}, MCU: {fw_search.group(2)}'''


def is_env_manufacturing():
    return __env__ == 'manufacturing'


def is_env_dev():
    return __env__ == 'dev'


def get_openfpga_loader_bin_path():
    '''Gets and returns the path to the openFPGALoader executable

    The path to the executable depends on the current execution
    environment. When the app is in bundled form, only a single
    binary is available. However, for development purposes, there
    are multiple binaries - one for each of the supported platforms
    and CPU architectures
    '''
    binary_name = 'openFPGALoader'
    cpu_type = CPU_TYPES.get(platform.machine(), '')
    if sys.platform == 'win32':
        binary_name += '.exe'
    elif sys.platform == 'linux':
        binary_name += f'''-{cpu_type}.AppImage'''
    platform_path = ''
    if hasattr(sys, '_MEIPASS') is False:
        if sys.platform == 'darwin':
            platform_path = os.path.join(sys.platform, cpu_type)
        else:
            platform_path = sys.platform
    relative_path = os.path.join('lib', 'openFPGALoader', platform_path, binary_name)
    return resolve_path(relative_path)

