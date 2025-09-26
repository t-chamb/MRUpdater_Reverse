# Source Generated with Decompyle++
# File: common.pyc (Python 3.10)

from __future__ import annotations
import struct
from dataclasses import dataclass, field
from enum import IntEnum

class CmdId(IntEnum):
    Loopback = 1
    ReadCartByte = 2
    WriteCartByte = 3
    WriteCartFlashByte = 4
    DetectCart = 5
    SetFrameBufferPixel = 6
    SetPSRAMAddress = 16
    WritePSRAMData = 17
    ReadPSRAMData = 18
    StartAudioPlayback = 19
    StopAudioPlayback = 20


class ReplyLen(IntEnum):
    Loopback = 3
    ReadCartByte = 3
    WriteCartByte = 3
    WriteCartFlashByte = 3
    DetectCart = 3
    SetFrameBufferPixel = 0
    SetPSRAMAddress = 3
    WritePSRAMData = 3
    ReadPSRAMData = 3
    StartAudioPlayback = 3
    StopAudioPlayback = 3


class ReplyPayloadLen(IntEnum):
    Loopback = 3
    ReadCartByte = 3
    WriteCartByte = 3
    WriteCartFlashByte = 3
    DetectCart = 3
    SetFrameBufferPixel = 0
    SetPSRAMAddress = 3
    WritePSRAMData = 3
    ReadPSRAMData = 3
    StartAudioPlayback = 3
    StopAudioPlayback = 3

SCREEN_PIXEL_WIDTH = 160
SCREEN_PIXEL_HEIGHT = 144
SCREEN_DRAW_TIMEOUT_S = 0.2
LimitedInteger = dataclass(<NODE:12>)
UnsignedByte = dataclass(<NODE:12>)
UnsignedHalfWord = dataclass(<NODE:12>)
VariableBitWidth = dataclass(<NODE:12>)
CartBusAddr = dataclass(<NODE:12>)
FrameBufferAddr = dataclass(<NODE:12>)

class PixelRGB888:
    '''
    A class which represents RGB888 pixel image data.
    Color is RGB888 (8-bits each channel). Converting to PixelRGB555 is done by shifting each channel by 3 bits.
    '''
    
    def __init__(self = None, value = None):
        self.idx2name = [
            'red',
            'green',
            'blue']
        for ch_value, name in zip(value, self.idx2name):
            if not isinstance(ch_value, int):
                raise TypeError(f'''Color channel {name} is not an integer''')
            if not ch_value <= ch_value or ch_value <= 255:
                pass
            else:
                0
            raise ValueError(f'''Color channel {name} must be between 0-255''')
        self.red = value[0]
        self.green = value[1]
        self.blue = value[2]


PixelRGB555 = dataclass(<NODE:12>)
PSRAMAddr = dataclass(<NODE:12>)
PSRAMData = dataclass(<NODE:12>)
AudioSampleCount = dataclass(<NODE:12>)

class CartFlashChip(IntEnum):
    '''An enum of existing cartridge flash chips.'''
    Microchip_SST39VF1681 = 1
    Infineon_S29JL032J70 = 2
    ISSI_IS29GL032 = 3
    Microchip_SST39VF1682 = 4

CartFlashInfo = dataclass(<NODE:12>)

class ChromaticBitmap:
    '''A class describing a 160x144 bitmap to be drawn to the Chromatic screen'''
    
    def __init__(self = None, bitmap = None):
        if len(bitmap) != SCREEN_PIXEL_HEIGHT:
            raise ValueError(f'''Bitmap height must be {SCREEN_PIXEL_HEIGHT}, got {len(bitmap)}''')
        for row in bitmap:
            if len(row) != SCREEN_PIXEL_WIDTH:
                raise ValueError(f'''Bitmap width must be {SCREEN_PIXEL_WIDTH}, got {len(row)}''')
        self.bitmap = bitmap

    
    def from_solid_color(cls = None, color = None):
        '''Generates a bitmap filled with the color specified'''
        bitmap = []
        for _ in range(SCREEN_PIXEL_HEIGHT):
            row = []
            for _ in range(SCREEN_PIXEL_WIDTH):
                row.append(color)
            bitmap.append(row)
        return cls(bitmap)

    from_solid_color = None(from_solid_color)
    
    def from_bmp(cls = None, bmp_path = None):
        '''Generates a bitmap from a 24-bit bmp file'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    from_bmp = None(from_bmp)
    
    def get_pixel(self = None, x = None, y = None):
        '''Return the pixel at coordinates (x, y)'''
        if not x <= x or x < SCREEN_PIXEL_WIDTH:
            pass
        else:
            0
        raise IndexError(f'''X coordinate out of range: {x}''')
        if not y <= y or y < SCREEN_PIXEL_HEIGHT:
            pass
        else:
            0
        raise IndexError(f'''Y coordinate out of range: {y}''')
        return self.bitmap[y][x]


