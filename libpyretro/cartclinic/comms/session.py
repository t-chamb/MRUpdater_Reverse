Unsupported argument found for LIST_EXTEND
Unsupported opcode: LIST_TO_TUPLE (102)
Warning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
# Source Generated with Decompyle++
# File: session.pyc (Python 3.10)

import logging
import queue
import time
import typing
from enum import IntEnum
from functools import wraps
from libpyretro.cartclinic.cart_api import NUM_FRAM_BANKS, CartAPI_Builder, CartAPI_Parser
from libpyretro.cartclinic.comms import CommandProperty, Transporter
from libpyretro.cartclinic.comms.exceptions import BankSwitchTimeOut, InvalidWriteBankSize, WriteBlockAddressError, WriteBlockDataError
from libpyretro.cartclinic.protocol import CartFlashInfo, CmdId, ReplyPayloadLen
from libpyretro.cartclinic.protocol.common import SCREEN_PIXEL_HEIGHT, SCREEN_PIXEL_WIDTH, ChromaticBitmap
VERBOSE_DEBUG = False
logger = logging.getLogger('cartclinic.session')
logger.setLevel(logging.DEBUG if VERBOSE_DEBUG else logging.INFO)
BANKSIZE = 16384
BYTES_PER_BLOCK = 256
BLOCKS_PER_BANK = BANKSIZE // BYTES_PER_BLOCK
FRAM_BANK_SIZE = 8192
BLOCKS_PER_FRAM_BANK = FRAM_BANK_SIZE // BYTES_PER_BLOCK

class Session:
    
    def __init__(self = None, tporter = None):
        """
        Establishes a session to the underlying Transporter. The transporter
        needs to know about what commands and their expected reply payload
        lengths are.

        Args:
            tporter (Transporter): The Transporter instance responsible for
            handling communication.

        Note:
            Keep the 'properties' list up to date as new command types are
            added.
        """
        self.tporter = tporter
        self.exception_queue = queue.Queue()
        properties = [
            (CmdId.Loopback, ReplyPayloadLen.Loopback),
            (CmdId.ReadCartByte, ReplyPayloadLen.ReadCartByte),
            (CmdId.WriteCartByte, ReplyPayloadLen.WriteCartByte),
            (CmdId.WriteCartFlashByte, ReplyPayloadLen.WriteCartFlashByte),
            (CmdId.DetectCart, ReplyPayloadLen.DetectCart),
            (CmdId.SetFrameBufferPixel, ReplyPayloadLen.SetFrameBufferPixel),
            (CmdId.SetPSRAMAddress, ReplyPayloadLen.SetPSRAMAddress),
            (CmdId.WritePSRAMData, ReplyPayloadLen.WritePSRAMData),
            (CmdId.ReadPSRAMData, ReplyPayloadLen.ReadPSRAMData),
            (CmdId.StartAudioPlayback, ReplyPayloadLen.StartAudioPlayback),
            (CmdId.StopAudioPlayback, ReplyPayloadLen.StopAudioPlayback)]
        for cmd_id, reply_len in properties:
            p = CommandProperty(cmd_id, reply_len, **('command_id', 'response_len'))
            self.tporter.add_command_props(p)

    
    def check_transport(method):
        '''Decorates a function to ensure that all calls contain a valid transporter.'''
        
        def _impl(self = None, *args, **kwargs):
            if self.tporter is None:
                raise AttributeError('Transport missing')
        # WARNING: Decompyle incomplete

        _impl = None(None(_impl))
        return _impl

    check_transport = typing.no_type_check(check_transport)
    
    def get_transporter_exception_if_any(self = None):
        '''Checks the transporter threads for exceptions. Return an exception if found,
        otherwise None.
        '''
        
        try:
            exc = self.tporter.exception_queue.get_nowait()
        finally:
            return None
            return None


    
    def _switch_bank(self = None, bank_index = None):
        '''
        Switches to a different 16KB bank on the cartridge. All I/O is limited
        to 16KB so read and write operations must switch.

        Args:
            bank_index: The zero-indexed bank number.

        Returns:
            True: When the bank switch was successful.
            False: When the bank switch operation timed out.
        '''
        tx_buffer = bytearray()
        msg_list = CartAPI_Builder.set_bank(bank_index)
        for msg in msg_list:
            tx_buffer.extend(msg)
        rq = self.tporter.add_listener([
            CmdId.WriteCartByte])
        self.tporter.send(bytes(tx_buffer))
        exp_msg_count = len(msg_list)
        timed_out = False
        BANK_SWITCH_TIMEOUT_S = 5
        start_time = time.monotonic()
   Warning: block stack is not empty!
     if exp_msg_count > 0:
            _ = rq.get()
            exp_msg_count -= 1
            if time.monotonic() - start_time > BANK_SWITCH_TIMEOUT_S:
                logger.error(f'''Bank switch request to {bank_index} took longer than {BANK_SWITCH_TIMEOUT_S} seconds''')
                timed_out = True
            elif not exp_msg_count > 0:
                self.tporter.remove_listener([
                    CmdId.WriteCartByte])
                if timed_out:
                    return False
                None.debug(f'''Bank switched to {bank_index}''')
                return True

    
    def read_bank(self = None, bank_index = None):
        '''
        Reads 16KB bank of data to flash memory.

        This method sends a serial sequence of `ReadCartByte` commands for each
        byte in the bank, accumulating the confirmed written data for return.

        Args:
            bank_index: The zero-indexed bank number.

        Returns:
            The bytearray containing read bank data.
        '''
        if not self._switch_bank(bank_index):
            raise BankSwitchTimeOut()
        bank_data = bytearray(BANKSIZE)
        tx_buffer = bytearray(BYTES_PER_BLOCK * 4)
        rq = self.tporter.add_listener([
            CmdId.ReadCartByte])
        start = time.monotonic()
        for block in range(BLOCKS_PER_BANK):
            for byte in range(BYTES_PER_BLOCK):
                msg = CartAPI_Builder.read_byte(block, byte, bank_index, **('block', 'byte_offset', 'bank_index'))
                tx_buffer[byte * 4:byte * 4 + 4] = msg
            self.tporter.send(tx_buffer)
            for _ in range(BYTES_PER_BLOCK):
                reply = rq.get()
                (addr, data_byte) = CartAPI_Parser.byte_read(reply)
                bank_data[addr] = data_byte
        self.tporter.remove_listener([
            CmdId.ReadCartByte])
        logger.debug(f'''Bank Read Elapsed {time.monotonic() - start}''')
        return bank_data

    read_bank = None(read_bank)
    
    def write_bank(self = None, bank_index = None, data_to_write = check_transport):
        '''
        Writes 16KB bank of data to flash memory.

        This method sends a serial sequence of `WriteCartFlashByte` commands for each
        byte in the bank, verifies the written response, and accumulates the
        confirmed written data for return.

        Args:
            bank_index (int): The target bank index to write to.
            data_to_write (bytearray): The 16KB data payload to write.

        Returns:
            bytearray: A copy of the verified data written, reconstructed from
            successful responses.

        Raises:
            BankSwitchTimeout: The bank switch took too long.
            InvalidWriteBankSize: If the input data is not exactly BANKSIZE bytes.
            WriteBlockAddressError: If the response address does not match.
            WriteBlockDataError: If the response written byte does not match.
        '''
        if len(data_to_write) != BANKSIZE:
            raise InvalidWriteBankSize(len(data_to_write))
        if not self._switch_bank(bank_index):
            raise BankSwitchTimeOut()
        bank_data = bytearray(BANKSIZE)
        tx_buffer = bytearray(BYTES_PER_BLOCK * 4)
        rq = self.tporter.add_listener([
            CmdId.WriteCartFlashByte])
        
        try:
            start = time.monotonic()
            for block in range(BLOCKS_PER_BANK):
                for byte in range(BYTES_PER_BLOCK):
                    address = block * BYTES_PER_BLOCK + byte
                    msg = CartAPI_Builder.write_flash_byte(block, byte, bank_index, data_to_write[address], **('block', 'offset', 'bank_index', 'data_byte'))
                    tx_buffer[byte * 4:byte * 4 + 4] = msg
                self.tporter.send(tx_buffer)
                error = None
                for i in range(BYTES_PER_BLOCK):
                    reply = rq.get()
                    (written_address, data_byte) = CartAPI_Parser.byte_write_flash(reply)
                    logger.debug(f'''[Bank {bank_index}] Wrote to {written_addreWarning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
ss:04x} with value {data_byte:02x}''')
                    if error is not None:
                        continue
                    exp_address_in_bank = block * BYTES_PER_BLOCK + i
                    if exp_address_in_bank != written_address:
                        error = WriteBlockAddressError(exp_address_in_bank, written_address, **('expected', 'actual'))
                        continue
                    if data_byte != data_to_write[exp_address_in_bank]:
                        error = WriteBlockDataError(exp_address_in_bank, data_byte, data_to_write[exp_address_in_bank], **('addr', 'expected', 'actual'))
                        continue
                    bank_data[exp_address_in_bank] = data_byte
                if error is not None:
                    raise error
        finally:
            pass
        self.tporter.remove_listener([
            CmdId.WriteCartFlashByte])
        raise 
        self.tporter.remove_listener([
            CmdId.WriteCartFlashByte])
        logger.debug(f'''Bank Write Elapsed {time.monotonic() - start}''')
        return bank_data


    write_bank = None(write_bank)
    
    def detect_mr_cart(self = None):
        '''
        Detects a ModRetro cartridge. This is expected to be called with
        regularity.

        Returns:
            (True, CartFlashInfo) if a MR cartridge is detected.
            (False, None) if either no cartridge is detected, or a cartridge
            from another vendor is detected.
        '''
        
        try:
            pass
        finally:
            return None
            return (False, None)


    detect_mr_cart = None(detect_mr_cart)
    
    def erase_flash_sector(self = None, sector_num = None, sector_size_bytes = None):
        '''
        Performs a sector flash erase and waits for completion confirmation.
        If you want to erase all sectors, use erase_flash_all().

        Args:
            sector_num: The sector number to erase.
            sector_size: The size (in bytes) of the sector.

        Returns:
            True if the flash erase was successfully confirmed.
            False if it timed out or verification failed.

        Raises:
            RuntimeError: If an unknown state is encountered during erase verification.
        '''
        sector_addr = sector_size_bytes * sector_num
        bank_index = sector_addr // BANKSIZE
        offset = sector_addr & 16383
        if not self._switch_bank(bank_index):
            raise BankSwitchTimeOut()
        status_addr = offset >> 8
        if bank_index > 0:
            status_addr |= 64
        ERASE_SECTOR_TIMEOUT_S = 10
        erase_msg_buffer = CartAPI_Builder.erase_sector(sector_num, sector_size_bytes)
        if self._erase_flash_common_start_erase(erase_msg_buffer, status_addr, ERASE_SECTOR_TIMEOUT_S, **('tx_buffer', 'status_addr', 'erase_wait_timeout_s')):
            
            try:
                rq = self.tporter.add_listener([
                    CmdId.ReadCartByte])
            finally:
                self.tporter.remove_listener([
                    CmdId.ReadCartByte])
                return None
                self.tporter.remove_listener([
                    CmdId.ReadCartByte])
                return False


    
    def erase_flash_all(self = None):
        '''
        Performs a full chip flash erase and waits for completion confirmation.
        If you want to do this by section, use erase_flash_sector().

        Returns:
            True if the flash erase was successfully confirmed.
            False if it timed out or verification failed.

        Raises:
            RuntimeError: If an unknown state is encountered during erase verification.
        '''
        erase_msg_buffer = CartAPI_Builder.erase_flash_all()
        ERASE_ALL_TIMEOUT_S = 100
        if self._erase_flash_common_start_erase(erase_msg_buffer, 0, ERASE_ALL_TIMEOUT_S, **('tx_buffer', 'status_addr', 'erase_wait_timeout_s')):
            
            try:
                rq = self.tporter.add_listener([
                    CmdId.ReadCartByte])
            finally:
 Warning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
               self.tporter.remove_listener([
                    CmdId.ReadCartByte])
                return None
                self.tporter.remove_listener([
                    CmdId.ReadCartByte])
                return False


    erase_flash_all = None(erase_flash_all)
    
    def get_flash_type(self = None):
        '''
        Detects and returns the flash chip type present in the cartridge.

        It sends read commands to extract identification data from the flash,
        parses this data to identify the chip, and then resets the flash
        controller to its normal operational mode.

        Returns:
            CartFlashInfo: An object containing information about the detected
            flash chip.

        Raises:
            RuntimeError: If the flash chip cannot be identified from the
            response.

        Notes:
           - Listeners for `ReadCartByte` and `WriteCartByte` are cleaned up at
             the end.
        '''
        
        try:
            flashtype_buffer = bytearray(32)
            rq_rcb = self.tporter.add_listener([
                CmdId.ReadCartByte])
            rq_wcb = self.tporter.add_listener([
                CmdId.WriteCartByte])
            tx_buffer = CartAPI_Builder.get_flash_type()
            self.tporter.send(tx_buffer)
            for i in range(32):
                tx_buffer = CartAPI_Builder.read_byte(0, i, 0)
                self.tporter.send(tx_buffer)
                reply = rq_rcb.get()
                (_, flashtype_buffer[i]) = CartAPI_Parser.byte_read(reply)
            cart_flash_info = CartAPI_Parser.flash_type(flashtype_buffer)
            if cart_flash_info is None:
                raise RuntimeError('Cart flash could not be identified')
            tx_buffer = CartAPI_Builder.reset_flash_controller()
            self.tporter.send(tx_buffer)
            expected_msgs = len(tx_buffer) // 4
            observed = 0
            RESET_FLASH_CTLR_TIMEOUT_S = 5
            
            try:
                rq_wcb.get_nowait()
                continue
            start_time = time.monotonic()
            if observed != expected_msgs:
                _ = rq_wcb.get()
                observed += 1
                if time.monotonic() - start_time >= RESET_FLASH_CTLR_TIMEOUT_S:
                    logger.error(f'''Get flash type timed out after {RESET_FLASH_CTLR_TIMEOUT_S}''')
                elif not observed != expected_msgs:
                    pass
                self.tporter.remove_listener([
                    CmdId.ReadCartByte,
                    CmdId.WriteCartByte])
                return None



    get_flash_type = None(get_flash_type)
    
    def set_frame_buffer(self = None, image = None):
        '''
        Write a full bitmap to the Chromatic screen

        Args:
            image: A 160x144 2D list of RGB values representing an image.
        '''
        tx_buffer = bytearray(SCREEN_PIXEL_WIDTH * SCREEN_PIXEL_HEIGHT * 5)
        start = time.monotonic()
        msg_count = 0
        for y in range(SCREEN_PIXEL_HEIGHT):
            for x in range(SCREEN_PIXEL_WIDTH):
                msg = CartAPI_Builder.set_frame_buffer_pixel(x, y, image.get_pixel(x, y), **('x', 'y', 'color888'))
                tx_buffer[msg_count * 5:msg_count * 5 + 5] = msg
                msg_count += 1
        self.tporter.send(tx_buffer)
        logger.debug(f'''Set Frame Buffer Elapsed {time.monotonic() - start}''')

    set_frame_buffer = None(set_frame_buffer)
    
    def detect_fram(self = None):
        '''
        Detects if the cartridge has FRAM by writing and reading back a value.

        Returns:
            True if FRAM is detected, False otherwise.
        '''
        
        try:
            rq = self.tporter.add_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
            self._enable_ram(rq)
            tx_buffer = CartAPI_Builder.set_bank_fram(NUM_FRAM_BANKS - 1)
            self.tporter.send(tx_buffer)
            rq.get()
            tx_buffer = CartAPI_Builder.read_byte_fram(BLOCKS_PER_FRAM_BANK -Warning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
 1, BYTES_PER_BLOCK - 1)
            self.tporter.send(tx_buffer)
            (_, original_byte) = CartAPI_Parser.byte_read(rq.get())
            overwrite_byte = original_byte + 1
            if overwrite_byte > 255:
                overwrite_byte = 0
            tx_buffer = CartAPI_Builder.write_byte_fram(BLOCKS_PER_FRAM_BANK - 1, BYTES_PER_BLOCK - 1, overwrite_byte)
            self.tporter.send(tx_buffer)
            rq.get()
            tx_buffer = CartAPI_Builder.set_bank_fram(NUM_FRAM_BANKS - 1)
            self.tporter.send(tx_buffer)
            rq.get()
            tx_buffer = CartAPI_Builder.read_byte_fram(BLOCKS_PER_FRAM_BANK - 1, BYTES_PER_BLOCK - 1)
            self.tporter.send(tx_buffer)
            (_, verify_byte) = CartAPI_Parser.byte_read(rq.get())
            tx_buffer = CartAPI_Builder.write_byte_fram(BLOCKS_PER_FRAM_BANK - 1, BYTES_PER_BLOCK - 1, original_byte)
            self.tporter.send(tx_buffer)
            rq.get()
            self._disable_ram(rq)
            self.tporter.remove_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
        finally:
            return None
            e = None
            
            try:
                logger.error(f'''Error detecting FRAM: {e}''')
                self.tporter.remove_listener([
                    CmdId.WriteCartByte,
                    CmdId.ReadCartByte])
                raise 
                e = None
                del e



    detect_fram = None(detect_fram)
    
    def read_fram(self = None):
        '''
        Read game save data from FRAM into a bytearray

        Returns:
            The 32KB bytearray containing FRAM data
        '''
        
        try:
            rq = self.tporter.add_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
            self._enable_ram(rq)
            fram_data = bytearray(FRAM_BANK_SIZE * NUM_FRAM_BANKS)
            for bank_index in range(NUM_FRAM_BANKS):
                tx_buffer = CartAPI_Builder.set_bank_fram(bank_index)
                self.tporter.send(tx_buffer)
                rq.get()
                for block in range(BLOCKS_PER_FRAM_BANK):
                    tx_buffer = bytearray()
                    for i in range(BYTES_PER_BLOCK):
                        tx_buffer.extend(CartAPI_Builder.read_byte_fram(block, i))
                    self.tporter.send(tx_buffer)
                    for i in range(BYTES_PER_BLOCK):
                        reply = rq.get()
                        (_, data_byte) = CartAPI_Parser.byte_read(reply)
                        fram_data[bank_index * FRAM_BANK_SIZE + block * BYTES_PER_BLOCK + i] = data_byte
            self._disable_ram(rq)
            self.tporter.remove_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
        finally:
            return None
            e = None
            
            try:
                logger.error(e)
                self.tporter.remove_listener([
                    CmdId.WriteCartByte,
                    CmdId.ReadCartByte])
                raise 
                e = None
                del e



    read_fram = None(read_fram)
    
    def write_fram(self = None, data_to_write = None):
        '''
        Writes game save data to FRAM

        Args:
            data_to_write (bytearray): The 32KB data payload to write.

        Returns:
            True if the write was successful
            False if an error occurred
        '''
        
        try:
            rq = self.tporter.add_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
            self._enable_ram(rq)
            for bank_index in range(NUM_FRAM_BANKS):
                tx_buffer = CartAPI_Builder.set_bank_fram(bank_index)
                self.tporter.send(tx_buffer)
                rq.get()
                for block in range(BLOCKS_PER_FRAM_BANK):
                    tx_buffer = bytearray()
                    for i in range(BYTES_PER_BLOCK):
                        byte_to_write = data_to_write[bank_index * FRAM_BWarning: Stack history is not empty!
Warning: block stack is not empty!
PycBuffer::getByte(): Unexpected end of stream
ANK_SIZE + block * BYTES_PER_BLOCK + i]
                        tx_buffer.extend(CartAPI_Builder.write_byte_fram(block, i, byte_to_write))
                    self.tporter.send(tx_buffer)
                    for _ in range(BYTES_PER_BLOCK):
                        rq.get()
            self._disable_ram(rq)
            self.tporter.remove_listener([
                CmdId.WriteCartByte,
                CmdId.ReadCartByte])
        finally:
            return True
            e = None
            
            try:
                logger.error(e)
            finally:
                e = None
                del e
                return False
                e = None
                del e



    write_fram = None(write_fram)
    
    def _erase_flash_common_start_erase(self = None, tx_buffer = None, status_addr = None, erase_wait_timeout_s = ('tx_buffer', bytes, 'status_addr', int, 'erase_wait_timeout_s', int, 'return', bool)):
        '''
        Initiates an erase sequenced. This is shared by the erase all and sector
        erase.

        Returns:
            True if the flash erase was started. False if it timed out or
            failed.
        '''
        expected_msgs = len(tx_buffer) // 4
        rq = self.tporter.add_listener([
            CmdId.WriteCartByte])
        self.tporter.send(tx_buffer)
        observed = 0
        start_time = time.monotonic()
        START_ERASE_TIMEOUT_S = 5
        timed_out = False
        if observed != expected_msgs:
            _ = rq.get()
            observed += 1
            if time.monotonic() - start_time >= START_ERASE_TIMEOUT_S:
                logger.error(f'''Erase all flash request timed out after {START_ERASE_TIMEOUT_S}''')
                timed_out = True
            elif not observed != expected_msgs:
                self.tporter.remove_listener([
                    CmdId.WriteCartByte])
                if timed_out:
                    return False
                None.debug('Erase initiated')
                return True

    
    def _erase_flash_common_wait_for_erase(self = None, reply_queue = None, status_addr = None, erase_wait_timeout_s = ('reply_queue', queue.Queue, 'status_addr', int, 'erase_wait_timeout_s', int, 'return', bool)):
