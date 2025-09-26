# Source Generated with Decompyle++
# File: esp_util.pyc (Python 3.10)

import sys
import time
from itertools import cycle, repeat, chain
from typing import Tuple, IO
import serial
import usb
from esptool.bin_image import intel_hex_to_bin
from esptool.loader import ESPLoader
from esptool.targets import CHIP_DEFS
from esptool.util import FatalError
from serial.tools import list_ports
import logging
flashing_tool_logger = logging.getLogger('mrupdater')

def create_address_filename_pair(address = None, filepath = None):
    '''
    Given an address and the filepath to a binary file, creates and
    returns a tuple object with the address and file object.

    The binary file also undergoes sanity checks to ensure that it
    is properly encoded

    :param address:
    :param filepath:
    :return:
    '''
    io_stream = open(filepath, 'rb')
    argfile = intel_hex_to_bin(io_stream, address)
    return (address, argfile)


def esp_connect_loop(port, initial_baud = None, chip = None, max_retries = None, trace = (False, 'default_reset'), before = ('port', str, 'initial_baud', int, 'chip', str, 'max_retries', int, 'trace', bool, 'before', str, 'return', ESPLoader)):
    '''
    This is directly from https://github.com/espressif/esptool/blob/v4.8.0/esptool/__init__.py#L1132
    because it is not advertised in the list of exports (via __all__)
    for the esptool module

    The main (ModRetro) addition is a type hint for the return type

    :param port:
    :param initial_baud:
    :param chip:
    :param max_retries:
    :param trace:
    :param before:
    :return:
    '''
    chip_class = CHIP_DEFS[chip]
    esp = None
    first = True
    ten_cycle = cycle(chain(repeat(False, 9), (True,)))
    retry_loop = chain(repeat(False, max_retries - 1), (True,) if max_retries else cycle((False,)))
        # Assignment completed
def get_mcu_port(vendor_id = None, product_id = None):
    if list_ports is None:
        raise FatalError('Listing all serial ports is currently not available. Please try to specify the port when running esptool.py or update the pyserial package to the latest version')
    port = None
    for entry in list_ports.comports():
        if sys.platform == 'darwin' and entry.device.endswith(('Bluetooth-Incoming-Port', 'wlan-debug')):
            continue
        if entry.vid == vendor_id:
            port = entry.device
            return port
        return port


def find_usb_device(vendor_id = None, product_id = None):
    '''Given a vendor and product id, this function returns a
    `usb.core.Device` object'''
    device = usb.core.find(vendor_id, product_id, **('idVendor', 'idProduct'))
    return device

