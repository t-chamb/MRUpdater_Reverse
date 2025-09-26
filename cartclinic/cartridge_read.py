Warning: block stack is not empty!
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
    
    try:
        cart_flash_info = session.get_flash_type()
        flashing_tool_logger.info(f'''{cart_flash_info}''')
    finally:
        pass
    raise InvalidCartridgeError()
    if cart_flash_info is None:
        flashing_tool_logger.error('Could not identify cartridge flash')
        raise InvalidCartridgeError()
    num_bytes_to_read = cart_flash_info.total_size_kb * 1024
    cart_data = bytearray(num_bytes_to_read)
    op_start = time.monotonic()
    num_total_banks = num_bytes_to_read // BANK_SIZE
    for bank in range(num_total_banks):
        flashing_tool_logger.info(f'''Reading bank {bank} of {num_total_banks}''')
        detection_thread.run_once()
        animation.run_once()
        bank_data = session.read_bank(bank)
        cart_data[bank * BANK_SIZE:bank * BANK_SIZE + BANK_SIZE] = bank_data
        emit_progress(((bank + 1) / num_total_banks) * 100)
    flashing_tool_logger.info(f'''Read Bytes Elapsed {time.monotonic() - op_start}''')
    return cart_data



def read_single_flash_bank(session = None, bank = None):
    '''Reads a single 16K bank from the cartridge flash.'''
    flashing_tool_logger.info(f'''Reading bank {bank} from cartridge''')
    return session.read_bank(bank)

