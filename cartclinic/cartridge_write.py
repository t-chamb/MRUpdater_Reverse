Warning: Stack history is not empty!
Warning: block stack is not empty!
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
    
    try:
        cart_flash_info = session.get_flash_type()
        flashing_tool_logger.info(f'''{cart_flash_info}''')
    finally:
        pass
    e = None
    
    try:
        flashing_tool_logger.error(e)
        raise InvalidCartridgeError()
        e = None
        del e
        if cart_flash_info is None:
            flashing_tool_logger.error('Could not identify cartridge flash')
            raise InvalidCartridgeError()
        SECTOR_ERASE_CADENCE = int(cart_flash_info.sector_size_kb // BANK_SIZE / 1024)
        if SECTOR_ERASE_CADENCE == 0:
            raise ValueError('Sectors must be erased every N banks. SECTOR_ALIGNMENT_IN_BANK=0 is invalid')
        if game_save_settings is not None and game_save_settings.saves_to_rom:
            pass
        stop_erasing_after_game = game_save_settings.save_compatible
        num_total_banks = cart_flash_info.total_size_kb * 1024 // BANK_SIZE
        num_game_banks = len(game_data) // BANK_SIZE
        if stop_erasing_after_game:
            num_game_banks = game_save_settings.offset_kb * 1024 // BANK_SIZE
            flashing_tool_logger.info(f'''Game saves to ROM, erasing will skip after {num_game_banks} game banks''')
        if len(game_data) % BANK_SIZE != 0:
            raise ValueError(f'''Game data must be aligned to BANK_SIZE={BANK_SIZE!r}''')
        if num_game_banks > num_total_banks:
            flashing_tool_logger.error(f'''Cartrige is too small num_total_banks={num_total_banks!r}, num_game_banks={num_game_banks!r}''')
            raise CartridgeTooSmallError(num_game_banks, num_total_banks, **('game_banks', 'cart_banks'))
        op_start = time.monotonic()
        for bank in range(num_total_banks):
            flashing_tool_logger.info(f'''Bank {bank} of {num_total_banks - 1}''')
            animation_thread.run_once()
            detection_thread.run_once()
            if bank % SECTOR_ERASE_CADENCE == 0:
                if not stop_erasing_after_game or bank >= num_game_banks:
                    flashing_tool_logger.info(f'''Erasing sector starting at bank {bank}''')
                    if cart_flash_info.part_id == CartFlashChip.Infineon_S29JL032J70 and bank == 0:
                        for i in range(8):
                            if not session.erase_flash_sector(i, 8192):
                                flashing_tool_logger.error(f'''Erasing S29JL032J70TFI320 on 8K sector num {i} failed''')
                                return False
                            None.info(f'''Erased 8K sector number {i} OK''')
                    elif not session.erase_flash_sector(bank // SECTOR_ERASE_CADENCE, SECTOR_ERASE_CADENCE * BANK_SIZE):
                        flashing_tool_logger.error(f'''Erasing {cart_flash_info.part_number} on 8K sector num {bank} failed''')
                        return False
                    flashing_tool_logger.info(f'''Erased sector number {bank} OK''')
            if bank < num_game_banks:
                chunk = game_data[bank * BANK_SIZE:bank * BANK_SIZE + BANK_SIWarning: Stack history is not empty!
Warning: block stack is not empty!
ZE]
                write_single_flash_bank(session, bank, chunk)
            emit_progress(((bank + 1) / num_total_banks) * 100)
        flashing_tool_logger.info(f'''Sector Erase, Write, Verify Elapsed {time.monotonic() - op_start}''')
        return True




def write_single_flash_bank(session = None, bank = None, data = None):
    '''Writes and verifies a single 16K bank to the cartridge flash.
    Make sure to erase before writing.
    '''
    write_tries = 1
    if write_tries <= NUM_WRITE_RETRIES:
        
        try:
            bank_readback = session.write_bank(bank, data)
            if len(bank_readback) != BANK_SIZE:
                raise CartridgeWriteError(f'''[Bank {bank}] Failed to write back all data, expected={BANK_SIZE}, actual={len(bank_readback)}''')
            flashing_tool_logger.info(f'''[Bank {bank}] Write amount OK''')
            for og, wrote in enumerate(zip(data, bank_readback)):
                if og != wrote:
                    raise CartridgeWriteError(f'''[Bank {bank}] Write failed at offset {i} for {og} !={wrote}''')
        finally:
            return True
            e = None
            
            try:
                flashing_tool_logger.error(f'''[Bank {bank}] [Attempt {write_tries}/{NUM_WRITE_RETRIES}] Write failed with exception: {e}''')
                write_tries += 1
                time.sleep(0.1)
            finally:
                e = None
                del e
            e = None
            del e
            if not write_tries <= NUM_WRITE_RETRIES:
                flashing_tool_logger.error(f'''[Bank {bank}] Write failed too many times''')
                raise CartridgeWriteError(f'''[Bank {bank}] Write failed too many times''')



