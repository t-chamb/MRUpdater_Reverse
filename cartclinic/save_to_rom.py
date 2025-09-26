# Source Generated with Decompyle++
# File: save_to_rom.pyc (Python 3.10)

import logging
from cartclinic.cartridge_read import read_single_flash_bank
from cartclinic.cartridge_write import write_single_flash_bank
from cartclinic.consts import BANK_SIZE
from cartclinic.mrpatcher import MRPatcherGameInfo
from libpyretro.cartclinic.comms import Session
flashing_tool_logger = logging.getLogger('mrupdater')

class GameHandler:
    
    def __init__(self = None, session = None, game_info = None):
        self._session = session
        self._game_info = game_info
        self._start_bank = self._game_info.save_settings.offset_kb * 1024 // BANK_SIZE

    
    def get_save(self = None):
        '''Returns the save data in bytes. The default handler uses the 32KB directly
        after the game data.
        '''
        save_data = read_single_flash_bank(self._session, self._start_bank)
        save_data += read_single_flash_bank(self._session, self._start_bank + 1)
        return save_data

    
    def restore_save(self = None, save_data = None):
        '''Writes the save data back to the cartridge. The default handler writes the
        32KB directly after the game data.
        '''
        self.erase_save()
        if not write_single_flash_bank(self._session, self._start_bank, save_data[:BANK_SIZE]):
            return False
        return None(self._session, self._start_bank + 1, save_data[BANK_SIZE:2 * BANK_SIZE])

    
    def erase_save(self = None):
        '''Erases the save data on the cartridge. The default handler erases the first
        sector directly after the game data.
        '''
        cart_flash_info = self._session.get_flash_type()
        SECTOR_ERASE_CADENCE = int(cart_flash_info.sector_size_kb // BANK_SIZE / 1024)
        flashing_tool_logger.info(f'''Erasing cartridge bank {self._start_bank}''')
        if not self._session.erase_flash_sector(self._start_bank // SECTOR_ERASE_CADENCE, SECTOR_ERASE_CADENCE * BANK_SIZE):
            flashing_tool_logger.error(f'''Erasing bank {self._start_bank} failed''')
            return False



class TetrisHandler(GameHandler):
    '''Handler for Tetris game save extraction and writing. Save is stored as follows:
    0x40000: 256 bytes
    0x50100: 8192 - 256 bytes
    0x60000: 8192 bytes
    0x70000: 8192 bytes
    0x80000: 8192 bytes
    '''
    
    def __init__(self = None, session = None, game_info = None):
        super().__init__(session, game_info)

    
    def get_save(self = None):
        '''Returns the save data spliced down to 32KB.'''
        flashing_tool_logger.info('Using Tetris logic to get save data')
        save_data = read_single_flash_bank(self._session, self._start_bank)[:256]
        save_data += read_single_flash_bank(self._session, self._start_bank + 4)[256:8192]
        save_data += read_single_flash_bank(self._session, self._start_bank + 8)[:8192]
        save_data += read_single_flash_bank(self._session, self._start_bank + 12)[:8192]
        save_data += read_single_flash_bank(self._session, self._start_bank + 16)[:8192]
        return save_data

    
    def restore_save(self = None, save_data = None):
        '''Converts standard 32KB save data back into save-to-rom format and writes
        it back to the cartridge.
        '''
        self.erase_save()
        flashing_tool_logger.info('Using Tetris logic to restore save data')
        if not write_single_flash_bank(self._session, self._start_bank, save_data[:256] + bytes([
            255] * (BANK_SIZE - 256))):
            return False
        if not None(self._session, self._start_bank + 4, bytes([
            255] * 256) + save_data[256:8192] + bytes([
            255] * 8192)):
            return False
        if not None(self._session, self._start_bank + 8, save_data[8192:16384] + bytes([
            255] * 8192)):
            return False
        if not None(self._session, self._start_bank + 12, save_data[16384:24576] + bytes([
            255] * 8192)):
            return False
        return None(self._session, self._start_bank + 16, save_data[24576:32768] + bytes([
            255] * 8192))

    
    def erase_save(self = None):
        '''Erases the save data on the cartridge. For Tetris, we need to erase all the
        sectors following the game data.
        '''
        flashing_tool_logger.info('Using Tetris logic to erase save data')
        cart_flash_info = self._session.get_flash_type()
        SECTOR_ERASE_CADENCE = int(cart_flash_info.sector_size_kb // BANK_SIZE / 1024)
        NUM_BANKS = cart_flash_info.total_size_kb * 1024 // BANK_SIZE
        flashing_tool_logger.info(f'''Erasing cartridge from bank {self._start_bank} to end of cartridge''')
        for bank in range(self._start_bank, NUM_BANKS):
            if bank % SECTOR_ERASE_CADENCE != 0:
                continue
            if not self._session.erase_flash_sector(bank // SECTOR_ERASE_CADENCE, SECTOR_ERASE_CADENCE * BANK_SIZE):
                flashing_tool_logger.error(f'''Erasing {cart_flash_info.part_number} on 8K sector num {bank} failed''')
                return False
            None.info(f'''Erased sector number {bank} OK''')
        return True

    __classcell__ = None


def map_game_title(session = None, game_info = None):
    GAME_MAP = {
        'tetris': TetrisHandler }
    if game_info.game_title in GAME_MAP:
        return GAME_MAP[game_info.game_title](session, game_info)
    return None(session, game_info)

