# Source Generated with Decompyle++
# File: util.pyc (Python 3.10)

import importlib.resources as importlib
import os
import platform
import re
import stat
import subprocess
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Union
import libpyretro
SUBPROCESS_FLAGS: int = subprocess.CREATE_NO_WINDOW if platform.system() == 'Windows' else 0
CommandResult = Union[(str, None)]
CPU_TYPES = {
    'amd64': 'x86_64',
    'x86_64': 'x86_64',
    'arm64': 'arm64',
    'aarch64': 'arm64' }
OS_NAME = platform.system().lower()
CPU_TYPE = CPU_TYPES.get(platform.machine().lower(), '')

class ShellCommandError(Exception):
    '''Raised when the shell command fails to execute.'''
    pass


def resolve_path(path = None):
    """Returns the absolute for the specified relative path

    The value specified in @param path should be relative to the application's
    entry point, not the module calling resolve_path.
    """
    exec_path = getattr(sys, '_MEIPASS', os.getcwd())
    resolved_path = os.path.abspath(os.path.join(exec_path, path))
    return resolved_path


def shell_execute(*, redirect_to_stdout, timeout, *cmd):
    kwargs = {
        'creationflags': SUBPROCESS_FLAGS,
        'shell': False,
        'stdout': subprocess.PIPE,
        'text': True,
        'universal_newlines': True }
    if redirect_to_stdout is False:
        kwargs['stderr'] = subprocess.PIPE
    response = None
    _wait_timeout = timeout if timeout > 0 else None
        # Assignment completed
def is_executable(path = None):
    '''Checks if the specified path is an executable file

    :param path: Path to the file to check
    :return: True if the file is an executable file, False otherwise.
    '''
    if OS_NAME == 'windows':
        return path.suffix.lower() in ('.exe', '.bat', '.cmd')
    return None(path.stat().st_mode & stat.S_IXUSR)


def make_executable(path = None):
    '''Makes the specified file executable

    :param path: Path to the file to make executable
    :return: True if the file was made executable, False otherwise.
    '''
    current_mode = path.stat().st_mode
        # Assignment completed
def find_binary(binary_name = None, check_for_app_image = None):
    """Finds the binary included in the Python package

    Uses importlib.resources to locate a binary file that is included as
    part of the package's data files.
    """
    if OS_NAME == 'windows':
        binary_name += '.exe'
    if OS_NAME == 'linux' and check_for_app_image:
        binary_name += f'''-{CPU_TYPE}.AppImage'''
    platform_path = os.path.join(OS_NAME, CPU_TYPE)
    if OS_NAME == 'windows':
        platform_path = re.sub('^windows', 'win32', platform_path)
    binary_path = str(importlib.resources.files(libpyretro) / 'bin' / platform_path / binary_name)
        # Assignment completed
def find_and_execute_binary(name = None):
    '''Finds and executes the specified binary

    :param name: Name of the binary to execute
    :return: The output of the command, or None if the command failed.
    '''
    binary = find_binary(name)
    return shell_execute(binary)

