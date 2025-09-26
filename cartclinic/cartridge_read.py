# Source Generated with Decompyle++
# File: cartridge_read.pyc (Python 3.10)

import logging
import time
from cartclinic.consts import BANK_SIZE
from cartclinic.exceptions import InvalidCartridgeError
from libpyretro.cartclinic.comms import Session
from flashing_tool.chromatic_subprocess import PauseableSubprocess
flashing_tool_logger = logging.getLogger('mrupdater')

def read_cartridge_helper(session = None, animation = None, detection_thread = None, emit_progress = ('session', Session, 'animation', PauseableSubprocess, 'detection_thread', PauseableSubprocess, 'emit_progress', callable, 'return', bytearray)):
    '''CC helper for reading back the full cartridge data while continuously
    checking for cartridge presence and animating the Chromatic screen.
    '''
    animation.run_once()
        # Incomplete decompilation - manual review needed
        pass
def read_single_flash_bank(session = None, bank = None):
    '''Reads a single 16K bank from the cartridge flash.'''
    flashing_tool_logger.info(f'''Reading bank {bank} from cartridge''')
    return session.read_bank(bank)

