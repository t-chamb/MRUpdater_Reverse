# Source Generated with Decompyle++
# File: cart_api.pyc (Python 3.10)

'''
read_block (get_block)
erase_flash
erase_sector
set_bank
write_block
dump_cart
detect_cart
updateFrameBuffer
connection_test
'''
from libpyretro.cartclinic.protocol.common import SCREEN_PIXEL_WIDTH, PixelRGB555, PixelRGB888
from .protocol import CartFlashChip, CartFlashInfo, CmdDetectCart, CmdReadCartByte, CmdSetFrameBufferPixel, CmdWriteCartByte, CmdWriteCartFlashByte, ReplyDetectCart, ReplyReadCartByte, ReplySetFrameBufferPixel, ReplyWriteCartByte, ReplyWriteCartFlashByte
MAX_CART_SIZE_KB = 8388608
MAX_BANK_SIZE_KB = 16384
NUM_BANKS = MAX_CART_SIZE_KB // MAX_BANK_SIZE_KB
NUM_FRAM_BANKS = 4

class CartAPI_Builder:
    
    def set_bank(bank_num = None):
        if bank_num > NUM_BANKS:
            raise ValueError(f'''Bank number {bank_num} exceeds the maximum of NUM_BANKS={NUM_BANKS}''')
        high_bank = CmdWriteCartByte(12288, bank_num >> 8 & 1)
        low_bank = CmdWriteCartByte(8448, bank_num & 255)
        return [
            high_bank.encode(),
            low_bank.encode()]

    set_bank = staticmethod(set_bank)
    
    def set_bank_fram(bank_num = None):
        if bank_num > NUM_FRAM_BANKS:
            raise ValueError(f'''Bank number {bank_num} exceeds the maximum of NUM_FRAM_BANKS={NUM_FRAM_BANKS}''')
        return CmdWriteCartByte(16384, bank_num).encode()

    set_bank_fram = staticmethod(set_bank_fram)
    
    def read_byte(block = None, byte_offset = None, bank_index = None):
        byte_offset &= 255
        block &= 255
        if bank_index > 0:
            block |= 64
        addr = byte_offset | block << 8
        return CmdReadCartByte(addr).encode()

    read_byte = staticmethod(read_byte)
    
    @staticmethod
    def read_byte_fram(block, byte_offset):
        byte_offset &= 255
        block = 160 | block & 255
        addr = byte_offset | block << 8
        return CmdReadCartByte(addr).encode()

    @staticmethod
    def write_byte(block, offset, bank_index, data_byte):
        offset &= 255
        block &= 255
        if bank_index > 0:
            block |= 64
        addr = offset | block << 8
        return CmdWriteCartByte(addr, data_byte).encode()

    @staticmethod
    def write_byte_fram(block, offset, data_byte):
        offset &= 255
        block = 160 | block & 255
        addr = offset | block << 8
        return CmdWriteCartByte(addr, data_byte).encode()
    
    def erase_flash_all():
        '''
        Constructs a message to erase the entire flash contents. Magic numbers
        are a part of the JEDEC standard that most (if not all) flash chips
        follow.
        '''
        return CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(2730, 128).encode() + CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(2730, 16).encode()

    erase_flash_all = staticmethod(erase_flash_all)
    
    def erase_sector(sector_num = None, sector_size = None):
        '''
        Constructs a message to erase a specific sector within flash. Magic numbers
        are a part of the JEDEC standard that most (if not all) flash chips
        follow.
        '''
        if sector_size == 0:
            raise ValueError('The sector must have a non-zero size')
        sector_start_addr = sector_num * sector_size
        bank = sector_start_addr // MAX_BANK_SIZE_KB
        offset = sector_start_addr & 16383
        sector = offset >> 8
        if bank > 0:
            sector |= 64
        sector <<= 8
        return CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(2730, 128).encode() + CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(sector, 48).encode()

    erase_sector = staticmethod(erase_sector)
    
    def get_flash_type():
        '''
        Constructs a message to place the device into identification mode in
        order to obtain the manufacturing and chip specific codes. Magic numbers
        are a part of the JEDEC standard that most (if not all) flash chips
        follow.
        '''
        return CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(2730, 144).encode()

    get_flash_type = staticmethod(get_flash_type)
    
    def reset_flash_controller():
        '''
        Constructs a message to reset the device into normal mode. This is
        useful for cases where the device was placed into alternative mode such
        as identification mode. Magic numbers are a part of the JEDEC standard
        that most (if not all) flash chips follow.
        '''
        return CmdWriteCartByte(2730, 170).encode() + CmdWriteCartByte(1365, 85).encode() + CmdWriteCartByte(0, 240).encode()

    reset_flash_controller = staticmethod(reset_flash_controller)
    
    @staticmethod
    def write_flash_byte(block, offset, bank_index, data_byte):
        offset &= 255
        block &= 255
        if bank_index > 0:
            block |= 64
        addr = offset | block << 8
        return CmdWriteCartFlashByte(addr, data_byte).encode()
    
    def detect_cart():
        return CmdDetectCart().encode()

    detect_cart = staticmethod(detect_cart)
    
    @staticmethod
    def set_frame_buffer_pixel(x, y, color888):
        '''
        Constructs a message to set the pixel at (x,y) to the specified color.
        Color is expected in RGB888 and gets converted to RGB555.

        Args:
            x: The x offset of the pixel (0-159)
            y: The y offset of the pixel (0-143)
            color: PixelRGB888 object containing the color channels
        '''
        addr = y * SCREEN_PIXEL_WIDTH + x
        (r, g, b) = PixelRGB555.from_rgb888(color888).value
        return CmdSetFrameBufferPixel(addr, r, g, b).encode()
    
    def enable_ram():
        '''
        Constructs a message to enable RAM access
        '''
        return CmdWriteCartByte(0, 10).encode()

    enable_ram = staticmethod(enable_ram)
    
    @staticmethod
    def disable_ram():
        '''
        Constructs a message to disable RAM access
        '''
        return CmdWriteCartByte(0, 0).encode()

    disable_ram = staticmethod(disable_ram)


class CartAPI_Parser:
    
    def byte_read(response = None):
        '''
        Returns the address and data byte that was requested to read from. If a
        write was not successful, the address and data byte will differ from the
        original request.
        '''
        reply = ReplyReadCartByte()
        msg = reply.decode(response)
        msg['addr'] &= 16383
        return (msg['addr'], msg['data'])

    byte_read = staticmethod(byte_read)
    
    def cart_detection_status(response = None):
        '''
        For first edition, the cart detection status bits inform if a cart is
        actively inserted (the limit switch is engaged) or if the cartridge was
        removed (the hardware limit switch changed state). This physical state
        change does not necessarily persist across reads depending on the rate
        at which the detect message is sent.

        :return:
            When inserted, the expected state is (true, false). When removed,
            the expected is (false, true), and later (false, false).
        '''
        reply = ReplyDetectCart().decode(response)
        return (reply['inserted'] == 1, reply['removed'] == 1)

    cart_detection_status = staticmethod(cart_detection_status)
    
    def byte_write(response = None):
        '''
        Returns the address and data byte that was written to. If a write was
        not successful, the address and data byte will differ from the original
        request.
        '''
        reply = ReplyWriteCartByte().decode(response)
        return (reply['addr'], reply['data'])

    byte_write = staticmethod(byte_write)
    
    def byte_write_flash(response = None):
        '''
        Returns the address and data byte that was written to. If a write was
        not successful, the address and data byte will differ from the original
        request.
        '''
        reply = ReplyWriteCartFlashByte()
        msg = reply.decode(response)
        msg['addr'] &= 16383
        return (msg['addr'], msg['data'])

    byte_write_flash = staticmethod(byte_write_flash)
    
    def flash_type(flash_info_data = None):
        """
        Identifies the flash chip type based on the provided flash information
        data.

        This method analyzes specific byte patterns in the `flash_info_data` to
        determine which known flash memory chip is present. It uses fixed
        signature checks corresponding to supported flash chips and returns a
        `CartFlashInfo` object containing the chip's details if a match is
        found.

        Args:
            flash_info_data (bytes): A byte array read from the flash chip in
            identification/auto mode, containing manufacturer and chip-specific
            codes.

        Returns:
            A CartFlashInfo object describing the flash chip if identified;
            otherwise, None.
        """
        flash_chips = {
            CartFlashChip.ISSI_IS29GL032: CartFlashInfo(CartFlashChip.ISSI_IS29GL032, 'IS29GL032-70TLET-TR', 'ISSI', 4096, 64, 'sector', 64, **('part_id', 'part_number', 'vendor', 'total_size_kb', 'sector_size_kb', 'grouping', 'recovery_offset_kb')),
            CartFlashChip.Infineon_S29JL032J70: CartFlashInfo(CartFlashChip.Infineon_S29JL032J70, 'S29JL032J70TFI320', 'Infineon', 4096, 64, 'sector', 8, **('part_id', 'part_number', 'vendor', 'total_size_kb', 'sector_size_kb', 'grouping', 'recovery_offset_kb')),
            CartFlashChip.Microchip_SST39VF1682: CartFlashInfo(CartFlashChip.Microchip_SST39VF1682, 'SST39VF1682-70-4C-EKE', 'Microchip', 2048, 64, 'sector', 64, **('part_id', 'part_number', 'vendor', 'total_size_kb', 'sector_size_kb', 'grouping', 'recovery_offset_kb')),
            CartFlashChip.Microchip_SST39VF1681: CartFlashInfo(CartFlashChip.Microchip_SST39VF1681, 'SST39VF1681-70-4C-EKE', 'Microchip', 2048, 64, 'sector', 64, **('part_id', 'part_number', 'vendor', 'total_size_kb', 'sector_size_kb', 'grouping', 'recovery_offset_kb')) }
        if flash_info_data[0] == 157 and flash_info_data[2] == 126 and flash_info_data[28] == 29 and flash_info_data[30] == 1:
            return flash_chips[CartFlashChip.ISSI_IS29GL032]
        if flash_info_data[0] == 1 and flash_info_data[2] == 83 and flash_info_data[4] == 0 and flash_info_data[6] == 2:
            return flash_chips[CartFlashChip.Infineon_S29JL032J70]
        if flash_info_data[0] == 191 and flash_info_data[1] == 200:
            return flash_chips[CartFlashChip.Microchip_SST39VF1681]
        if flash_info_data[0] == 191 and flash_info_data[1] == 201:
            return flash_chips[CartFlashChip.Microchip_SST39VF1682]
        
        return None  # Unknown flash chip

    flash_type = staticmethod(flash_type)
    
    def set_frame_buffer_pixel_confirmation(response = None):
        '''
        Returns True if response is received with the expected cmd_id
        '''
        ReplySetFrameBufferPixel().decode(response)
        return True

    set_frame_buffer_pixel_confirmation = staticmethod(set_frame_buffer_pixel_confirmation)

