# Source Generated with Decompyle++
# File: cmd.pyc (Python 3.10)

import struct
from common import AudioSampleCount, CartBusAddr, CmdId, FrameBufferAddr, PixelRGB555, PSRAMAddr, PSRAMData, UnsignedByte
from proto import FPGACmd, InvalidCmdLengthException

class CmdLoopback(FPGACmd):
    '''
    A command used to verify the connection to a Chromatic FPGA.
    FPGA will respond back with the original bytes sent from the Host computer.
    '''
    CMD_LEN = 3
    
    def __init__(self = None, payload = None):
        '''
        payload ([bytes;3]): Dummy bytes used to confirm loopback validity.
        '''
        if payload is None:
            raise ValueError
        if type(payload) is not bytes:
            raise TypeError
        if len(payload) is not self.CMD_LEN:
            raise InvalidCmdLengthException(self.CMD_LEN, len(payload))
        self.fmt = '<BBBB'
        self.payload = payload

    
    def encode(self = None):
        if self.payload is None:
            raise ValueError(f'''Command {self.__class__.__name__} has no payload''')
        return struct.pack(self.fmt, CmdId.Loopback, self.payload[0], self.payload[1], self.payload[2])

    
    def __setattr__(self = None, name = None, value = None):
        if name == 'CMD_LEN':
            raise AttributeError('Cannot modify CMD_LEN')
        super().__setattr__(name, value)

    __classcell__ = None


class CmdReadCartByte(FPGACmd):
    '''
    The FPGA will read from an address on the cartridge bus.
    Can be used for reading cartridge data in case of dump or verify.
    '''
    
    def __init__(self = None, addr = None):
        '''
        addr (uint16): The cartridge bus address to read from.
        '''
        self.fmt = '<BHB'
        self.cart_addr = CartBusAddr(addr)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.ReadCartByte, self.cart_addr.value, 0)



class CmdWriteCartByte(FPGACmd):
    '''
    The FPGA will write a byte to the specified address on the cartridge bus.
    Useful to communicate with memory controller (MBC) to change memory banks.
    '''
    
    def __init__(self = None, addr = None, data = None):
        '''
        addr (uint16): The cartridge bus address to read from.
        data (uint8): The data to write to the cartridge bus.
        '''
        self.fmt = '<BHB'
        self.cart_addr = CartBusAddr(addr)
        self.data = UnsignedByte(data)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.WriteCartByte, self.cart_addr.value, self.data.value)



class CmdWriteCartFlashByte(FPGACmd):
    '''
    FPGA will write data byte to address on cartridge flash bus, then starts reading the same address up to 2^16 times.

    This is the standard procedure to write a byte to the flash and check if the write has finished.
    The flash chip hardware returns an incorrect read value until the internal write is complete.
    '''
    
    def __init__(self = None, addr = None, data = None):
        '''
        addr (uint16): The cartridge bus address to read from.
        data (uint8): The data to write to the cartridge bus.
        '''
        self.fmt = '<BHB'
        self.cart_addr = CartBusAddr(addr)
        self.data = UnsignedByte(data)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.WriteCartFlashByte, self.cart_addr.value, self.data.value)



class CmdDetectCart(FPGACmd):
    '''
    A command used to check if the cartridge is detected.
    This command can be used to detect that there is a cartridge available.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.DetectCart, 0, 0, 0)



class CmdSetFrameBufferPixel(FPGACmd):
    '''
    A command used to write pixels to the display.
    Useful to write bitmap images to the screen.
    '''
    
    def __init__(self, addr = None, r = None, g = None, b = ('addr', int, 'r', int, 'g', int, 'b', int)):
        '''
        addr (uint15):  The frame buffer address.
                        The address is 15 bits for 160x144 pixels.
                        The pixel position decoded as: (y * 160) + x.

        r (uint15): The 5-bit red channel.
        g (uint15): The 5-bit green channel.
        b (uint15): The 5-bit blue channel.
        '''
        self.fmt = '<BHH'
        self.fb_addr = FrameBufferAddr(addr)
        self.color = PixelRGB555((r, g, b))

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.SetFrameBufferPixel, self.fb_addr.value, self.color.value_as_uint15())



class CmdSetPSRAMAddress(FPGACmd):
    '''
    A command used to set up the PSRAM address for read and write operations.
    '''
    
    def __init__(self = None, addr = None):
        '''
        addr (uint24): The PSRAM address to set up.
        '''
        self.fmt = '<BI'
        self.psram_addr = PSRAMAddr(addr)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.SetPSRAMAddress, self.psram_addr.value)[0:-1]



class CmdWritePSRAMData(FPGACmd):
    '''
    A command used to write data to PSRAM set up by CmdSetPSRAMAddress.
    '''
    
    def __init__(self = None, data = None):
        '''
        data (uint16): The data value to write to PSRAM.
        '''
        self.fmt = '<BH'
        self.psram_data = PSRAMData(data)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.WritePSRAMData, self.psram_data.value)



class CmdReadPSRAMData(FPGACmd):
    '''
    A command used to read data from PSRAM set up by CmdSetPSRAMAddress.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.ReadPSRAMData, 0, 0, 0)



class CmdStartAudioPlayback(FPGACmd):
    '''
    A command used to start audio playback.
    The FPGA will start to play back 44.1Khz, 16 bit Stereo audio from PSRAM starting at address zero for the length set in this command.

    Length is in count of samples, so it will play back 4 bytes * length of bytes.
    Playback will loop back to address zero after the last sample has been played.
    '''
    
    def __init__(self = None, samples = None):
        self.fmt = '<BI'
        self.sample_count = AudioSampleCount(samples)

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.StartAudioPlayback, self.sample_count.value)[0:-1]



class CmdStopAudioPlayback(FPGACmd):
    '''
    A command used to stop any audio playback and give out zero amplitude to the speaker.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'

    
    def encode(self = None):
        return struct.pack(self.fmt, CmdId.StopAudioPlayback, 0, 0, 0)


