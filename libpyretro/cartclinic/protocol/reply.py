# Source Generated with Decompyle++
# File: reply.pyc (Python 3.10)

import typing
from common import CmdId
from proto import FPGAReply

class ReplyLoopback(FPGAReply):
    '''
    A reply to a CmdLoopback message.
    FPGA responds back with the original bytes sent from the Host computer.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'
        self.expected_id = CmdId.Loopback

    
    def decode(self = None, data = None):
        (cmd_id, b0, b1, b2) = super().decode(data)
        return dict(cmd_id, bytes([
            b0,
            b1,
            b2]), **('cmd_id', 'payload'))

    __classcell__ = None


class ReplyReadCartByte(FPGAReply):
    '''
    The FPGA response of a byte read from the cartridge bus.
    '''
    
    def __init__(self = None):
        self.fmt = '<BHB'
        self.expected_id = CmdId.ReadCartByte

    
    def decode(self = None, data = None):
        (cmd_id, addr, data) = super().decode(data)
        return dict(cmd_id, addr, data, **('cmd_id', 'addr', 'data'))

    __classcell__ = None


class ReplyWriteCartByte(FPGAReply):
    '''
    The FPGA response of a byte written to the cartridge bus.
    '''
    
    def __init__(self = None):
        self.fmt = '<BHB'
        self.expected_id = CmdId.WriteCartByte

    
    def decode(self = None, data = None):
        (cmd_id, addr, data) = super().decode(data)
        return dict(cmd_id, addr, data, **('cmd_id', 'addr', 'data'))

    __classcell__ = None


class ReplyWriteCartFlashByte(FPGAReply):
    '''
    The FPGA response of a byte written to cartrige flash.
    '''
    
    def __init__(self = None):
        self.fmt = '<BHB'
        self.expected_id = CmdId.WriteCartFlashByte

    
    def decode(self = None, data = None):
        (cmd_id, addr, data) = super().decode(data)
        return dict(cmd_id, addr, data, **('cmd_id', 'addr', 'data'))

    __classcell__ = None


class ReplyDetectCart(FPGAReply):
    '''
    The FPGA response of detect cartridge status command.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'
        self.expected_id = CmdId.DetectCart

    
    def decode(self = None, data = None):
        (cmd_id, status, _, _) = super().decode(data)
        flag_inserted = status & 1 == 1
        flag_removed = status & 2 == 2
        return dict(cmd_id, flag_inserted, flag_removed, **('cmd_id', 'inserted', 'removed'))

    __classcell__ = None


class ReplySetFrameBufferPixel(FPGAReply):
    '''
    The FPGA response of setting a pixel within the frame bufffer.
    '''
    
    def __init__(self = None):
        self.fmt = '<B'
        self.expected_id = CmdId.SetFrameBufferPixel

    
    def decode(self = None, data = None):
        cmd_id = super().decode(data)
        return dict(cmd_id, **('cmd_id',))

    __classcell__ = None


class ReplySetPSRAMAddress(FPGAReply):
    '''
    The FPGA response of setting the PSRAM address.
    '''
    
    def __init__(self = None):
        self.fmt = '<BBBB'
        self.expected_id = CmdId.SetPSRAMAddress

    
    def decode(self = None, data = None):
        (cmd_id, a0, a1, a2) = super().decode(data)
        addr = a2 << 16 | a1 << 8 | a0
        return dict(cmd_id, addr, **('cmd_id', 'addr'))

    __classcell__ = None


class ReplyWritePSRAMData(FPGAReply):
    '''
    The FPGA response to writing data to PSRAM.
    '''
    
    def __init__(self = None):
        self.fmt = '<BH'
        self.expected_id = CmdId.WritePSRAMData

    
    def decode(self = None, data = None):
        (cmd_id, data) = super().decode(data)
        return dict(cmd_id, data, **('cmd_id', 'data'))

    __classcell__ = None


class ReplyReadPSRAMData(FPGAReply):
    
    def __init__(self = None):
        self.fmt = '<BH'
        self.expected_id = CmdId.ReadPSRAMData

    
    def decode(self = None, data = None):
        (cmd_id, data) = super().decode(data)
        return dict(cmd_id, data, **('cmd_id', 'data'))

    __classcell__ = None


class ReplyStartAudioPlayback(FPGAReply):
    
    def __init__(self = None):
        self.fmt = '<BBBB'
        self.expected_id = CmdId.StartAudioPlayback

    
    def decode(self = None, data = None):
        (cmd_id, sc0, sc1, sc2) = super().decode(data)
        count = sc2 << 16 | sc1 << 8 | sc0
        return dict(cmd_id, count, **('cmd_id', 'sample_count'))

    __classcell__ = None


class ReplyStopAudioPlayback(FPGAReply):
    
    def __init__(self = None):
        self.fmt = '<BBBB'
        self.expected_id = CmdId.StopAudioPlayback

    
    def decode(self = None, data = None):
        (cmd_id, _, _, _) = super().decode(data)
        return dict(cmd_id, **('cmd_id',))

    __classcell__ = None

