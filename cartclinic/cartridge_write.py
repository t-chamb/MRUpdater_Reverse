# Source Generated with Decompyle++
# File: cartridge_write.pyc (Python 3.10)

import logging
import time
from cartclinic.consts import BANK_SIZE, NUM_WRITE_RETRIES
from cartclinic.exceptions import CartridgeTooSmallError, CartridgeWriteError, InvalidCartridgeError
from cartclinic.mrpatcher import GameSaveSettings
from libpyretro.cartclinic.cart_api import CartFlashChip
from libpyretro.cartclinic.comms import Session
from flashing_tool.chromatic_subprocess import PauseableSubprocess
flashing_tool_logger = logging.getLogger('mrupdater')

def write_cartridge_helper(session, game_data, game_save_settings = None, animation_thread = None, detection_thread = None, emit_progress = ('session', Session, 'game_data', bytearray, 'game_save_settings', GameSaveSettings | None, 'animation_thread', PauseableSubprocess, 'detection_thread', PauseableSubprocess, 'emit_progress', callable, 'return', bool)):
    '''CC helper function for writing game_data to the cartridge while
    continuously checking for cartridge presence and animating the
    Chromatic screen.
    '''
    pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
def write_single_flash_bank(session = None, bank = None, data = None):
    '''Writes and verifies a single 16K bank to the cartridge flash.
    Make sure to erase before writing.
    '''
    write_tries = 1
        # Assignment completed