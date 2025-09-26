# Source Generated with Decompyle++
# File: exceptions.pyc (Python 3.10)


class InvalidCartridgeError(Exception):
    '''Exception raised when the cartridge is not recognized as one used by ModRetro.'''
    
    def __init__(self = None):
        self.message = 'MODRETRO CARTRIDGE NOT DETECTED\nPLEASE REINSERT THE CARTRIDGE'
        super().__init__(self.message)

    __classcell__ = None


class CartridgeUnpluggedError(Exception):
    '''Exception raised when the cartridge is unplugged during a check or update.'''
    
    def __init__(self = None):
        self.message = 'LOST CONNECTION TO THE CARTRIDGE\nPLEASE REINSERT THE CARTRIDGE'
        super().__init__(self.message)

    __classcell__ = None


class CartridgeWriteError(Exception):
    '''Exception raised when there is an error writing to the cartridge.'''
    pass


class CartridgeTooSmallError(Exception):
    '''Exception raised when the cartridge is too small for the provided ROM.'''
    
    def __init__(self = None, game_banks = None, cart_banks = None):
        self.message = 'CARTRIDGE TOO SMALL FOR GAME ROM'
        self.game_banks = game_banks
        self.cart_banks = cart_banks
        super().__init__(self.message)

    __classcell__ = None


class SaveWriteFailureError(Exception):
    '''Exception raised when there is a failure writing save data to the cartridge.'''
    pass

