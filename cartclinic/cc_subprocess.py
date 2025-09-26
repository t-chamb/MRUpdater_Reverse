# Source Generated with Decompyle++
# File: cc_subprocess.pyc (Python 3.10)

import logging
import tempfile
import time
import base64
import os
from libpyretro.cartclinic.comms import Session
from libpyretro.ips_util.patch import Patch
from libpyretro.cartclinic.comms.exceptions import WriteBlockDataError
from cartclinic.animation import AnimateChromaticSubprocess
from cartclinic.cartridge_read import read_cartridge_helper, read_single_flash_bank
from cartclinic.cartridge_write import write_cartridge_helper
from cartclinic.consts import LOADING_TEXT_INTERVAL_S
from PySide6.QtCore import Signal
from cartclinic.exceptions import CartridgeUnpluggedError, InvalidCartridgeError, CartridgeTooSmallError, SaveWriteFailureError
from cartclinic.mrpatcher import GameSaveSettings, MRPatcherGameInfo, MRPatcherResponse, MRPatcherAPI
from cartclinic.save_to_rom import map_game_title
from flashing_tool.chromatic import Chromatic
from flashing_tool.chromatic_subprocess import ChromaticSubprocess, FlashSRAMSubprocess, OpenFPGALoaderResult, PauseableSubprocess, ReadFileSubprocess, WaitForInterval
flashing_tool_logger = logging.getLogger('mrupdater')
PATCH_PROGRESS_OFFSET = 10
MRPATCHER_PROGRESS_OFFSET = 1
CART_CHECK_FREQUENCY = 1.5
FRAM_SIZE = 32768

class DetectCartridgeSubprocess(PauseableSubprocess):
    '''Detects whether a ModRetro cartridge is inserted. This should
    not be running asynchronously with any other cartridge operations.
    '''
    
    def __init__(self = None, chromatic_session = None, interval_s = None):
        super().__init__()
        self.chromatic_session = chromatic_session
        self.interval_s = interval_s
        self.last_checked = time.monotonic() - interval_s

    
    def is_stale(self):
        return time.monotonic() - self.last_checked > self.interval_s

    
    def run_once(self):
        if not self.is_stale():
            return None
        None(self.chromatic_session)
        self.last_checked = time.monotonic()

    __classcell__ = None


class DetectChromaticSubprocess(PauseableSubprocess):
    '''Checks the session exception queue for serial exceptions, which
    indicate that we lost connection to the Chromatic.
    '''
    error = Signal(Exception)
    
    def __init__(self = None, chromatic_session = None):
        super().__init__(True, **('autoplay',))
        self.chromatic_session = chromatic_session

    
    def run_once(self):
        exc = self.chromatic_session.get_transporter_exception_if_any()
        if exc is not None:
            self.error.emit(exc)
            return None

    __classcell__ = None


class CartClinicSubprocess(ChromaticSubprocess):
    '''This is a subprocess base class that implements the initial setup process
    of flashing the cart clinic firmware.
    '''
    setup_complete_signal = Signal(bool)
    text_timer_signal = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, cart_clinic_fw_path = None):
        super().__init__(chromatic)
        self.cart_clinic_fw_path = cart_clinic_fw_path
        self._sram_thread = None
        self._cc_timer_thread = None

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def setup(self):
        flashing_tool_logger.info('Flashing Cart Clinic firmware to SRAM...')
        self._sram_thread = FlashSRAMSubprocess(self.chromatic, self.cart_clinic_fw_path, **('chromatic', 'filepath'))
        self._sram_thread.finished.connect(self.setup_callback)
        self._sram_thread.start()

    
    def setup_callback(self = None, flash_result = None):
        if flash_result != OpenFPGALoaderResult.SUCCESS:
            self.error_callback('FAILED TO PUT CHROMATIC IN CART CLINIC MODE')
            return None
        None.setup_complete_signal.emit(True)

    
    def start_timer(self):
        self._cc_timer_thread = WaitForInterval(LOADING_TEXT_INTERVAL_S, **('interval',))
        self._cc_timer_thread.update_signal.connect(self.timer_callback)
        self._cc_timer_thread.start()

    
    def timer_callback(self, _):
        self.text_timer_signal.emit(True)

    
    def error_callback(self = None, error = None):
        self.cleanup()
        self.error.emit(error)

    
    def cleanup(self):
        if self._cc_timer_thread:
            self._cc_timer_thread.stop()
            return None

    
    def parse_progress(self = None, data = None):
        pass

    
    def finish(self = None, result = None):
        self.cleanup()
        super().finish(result)

    
    def check_mr_cart_inserted(self = None, session = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    __classcell__ = None


class CartClinicCheckSubprocess(CartClinicSubprocess):
    '''This is a wrapper subprocess to do the first half of the cart clinic
    workflow - setup, read cartridge, request patch. Each step has a callback
    which kicks off the next step.
    '''
    finished = Signal(MRPatcherResponse)
    current_cart_data = Signal(bytearray)
    
    def __init__(self = None, chromatic = None, cart_clinic_fw_path = None, mrpatcher_endpoint = None):
        super().__init__(chromatic, cart_clinic_fw_path)
        self.mrpatcher_endpoint = mrpatcher_endpoint
        self._cc_read_thread = None
        self._cc_request_thread = None

    
    def start_check_cartridge(self = None, session = None, animation_thread = None, detection_thread = ('session', Session, 'animation_thread', AnimateChromaticSubprocess, 'detection_thread', DetectCartridgeSubprocess)):
        self.chromatic_session = session
        self._cc_animation_thread = animation_thread
        self._cc_detection_thread = detection_thread
        self._cc_read_thread = ReadCartridgeSubprocess(self.chromatic, self.chromatic_session, self._cc_animation_thread, self._cc_detection_thread)
        self._cc_read_thread.finished.connect(self.read_cartridge_callback)
        self._cc_read_thread.progress.connect(self.progress_callback)
        self._cc_read_thread.error.connect(self.error_callback)
        self._cc_read_thread.start()

    
    def read_cartridge_callback(self = None, cart_bytes = None):
        if cart_bytes or len(cart_bytes) == 0:
            self.error_callback('COULD NOT READ CARTRIDGE DATA')
            return None
        None._cc_animation_thread.play()
        self._cc_detection_thread.play()
        self.current_cart_data.emit(cart_bytes)
        self.request_patch(cart_bytes)

    
    def request_patch(self = None, cart_bytes = None):
        self._cc_request_thread = RequestPatchSubprocess(self.chromatic, self.mrpatcher_endpoint, cart_bytes)
        self._cc_request_thread.finished.connect(self.request_patch_callback)
        self._cc_request_thread.error.connect(self.error_callback)
        self._cc_request_thread.start()

    
    def request_patch_callback(self = None, mrpatcher_response = None):
        self.cleanup()
        self.finish(mrpatcher_response)

    __classcell__ = None


class CartClinicUpdateSubprocess(ChromaticSubprocess):
    '''This is a wrapper subprocess to do the second half of the cart clinic
    workflow - patch game, write cartridge data, and cleanup.
    '''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, ips_base64 = None, cart_game_data = None, game_save_settings = None, animation_thread = None, detection_thread = None):
        super().__init__(chromatic)
        self.chromatic_session = chromatic_session
        self.ips_base64 = ips_base64
        self.cart_game_data = cart_game_data
        self.game_save_settings = game_save_settings
        self._cc_animation_thread = animation_thread
        self._cc_detection_thread = detection_thread

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def error_callback(self = None, error = None):
        self.error.emit(error)

    
    def patch_game(self):
        self._cc_patch_thread = ApplyPatchSubprocess(self.chromatic, self.cart_game_data, self.ips_base64, **('game_data', 'ips_base64'))
        self._cc_patch_thread.finished.connect(self.patch_game_callback)
        self._cc_patch_thread.error.connect(self.error_callback)
        self._cc_patch_thread.start()

    
    def patch_game_callback(self = None, game_data = None):
        self._cc_animation_thread.pause()
        self._cc_detection_thread.pause()
        time.sleep(0.5)
        self.progress_callback(PATCH_PROGRESS_OFFSET)
        self.write_cartridge(game_data)

    
    def write_cartridge(self = None, game_data = None):
        self._cc_write_thread = WriteCartridgeSubprocess(self.chromatic, self.chromatic_session, game_data, self.game_save_settings, self._cc_animation_thread, self._cc_detection_thread, **('chromatic_session', 'game_data', 'game_save_settings', 'animation_thread', 'detection_thread'))
        self._cc_write_thread.finished.connect(self.write_cartridge_callback)
        self._cc_write_thread.error.connect(self.error_callback)
        self._cc_write_thread.progress.connect(self.progress_callback)
        self._cc_write_thread.start()

    
    def write_cartridge_callback(self = None, result = None):
        time.sleep(0.5)
        self.finish(result)

    __classcell__ = None


class CartClinicHomebrewSubprocess(CartClinicSubprocess):
    '''This is a subprocess to perform the writing of user-provided homebrew games'''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, cart_clinic_fw_path = None, homebrew_game_path = None):
        super().__init__(chromatic, cart_clinic_fw_path)
        self._homebrew_game_path = homebrew_game_path
        self._read_file_thread = None

    
    def start_write_homebrew(self = None, chromatic_session = None, animation_thread = None, detection_thread = ('chromatic_session', Session, 'animation_thread', AnimateChromaticSubprocess, 'detection_thread', DetectCartridgeSubprocess)):
        self._cc_animation_thread = animation_thread
        self._cc_detection_thread = detection_thread
        self._read_file_thread = ReadFileSubprocess(self._homebrew_game_path)
        None((lambda data = None: self.read_file_callback(data, chromatic_session)))
        self._read_file_thread.error.connect(self.error_callback)
        self._read_file_thread.start()

    
    def read_file_callback(self = None, file_data = None, chromatic_session = None):
        game_data = bytearray(file_data)
        self._cc_animation_thread.pause()
        self._cc_detection_thread.pause()
        time.sleep(0.5)
        game_save_settings = GameSaveSettings()
        self._cc_write_thread = WriteCartridgeSubprocess(self.chromatic, chromatic_session, game_data, game_save_settings, self._cc_animation_thread, self._cc_detection_thread, **('chromatic_session', 'game_data', 'game_save_settings', 'animation_thread', 'detection_thread'))
        self._cc_write_thread.finished.connect(self.write_homebrew_callback)
        self._cc_write_thread.error.connect(self.error_callback)
        self._cc_write_thread.progress.connect(self.progress_callback)
        self._cc_write_thread.start()

    
    def write_homebrew_callback(self = None, result = None):
        time.sleep(0.5)
        self.finish(result)

    __classcell__ = None


class ReadCartridgeSubprocess(ChromaticSubprocess):
    '''Reads game data off the cartridge'''
    finished = Signal(bytearray)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, animation_thread = None, detection_thread = None):
        super().__init__(chromatic)
        self.chromatic_session = chromatic_session
        self.animation_thread = animation_thread
        self.detection_thread = detection_thread

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def parse_progress(self = None, data = None):
        pass

    
    def emit_progress(self = None, progress = None):
        offset_progress = ((100 - MRPATCHER_PROGRESS_OFFSET) / 100) * progress
        self.progress.emit(offset_progress)

    __classcell__ = None


class RequestPatchSubprocess(ChromaticSubprocess):
    '''Requests a patch from MRPatcher service'''
    finished = Signal(MRPatcherResponse)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, endpoint = None, game_bytes = None):
        super().__init__(chromatic)
        self.endpoint = endpoint
        self.game_bytes = game_bytes

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def parse_progress(self = None, data = None):
        pass

    __classcell__ = None


class ApplyPatchSubprocess(ChromaticSubprocess):
    '''Applies an IPS patch file to a game ROM'''
    finished = Signal(bytearray)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, game_data = None, ips_base64 = None):
        super().__init__(chromatic)
        self.game_data = game_data
        self.ips_base64 = ips_base64

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def parse_progress(self = None, data = None):
        pass

    __classcell__ = None


class WriteCartridgeSubprocess(ChromaticSubprocess):
    '''Writes game data to the cartridge'''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, game_data = None, game_save_settings = None, animation_thread = None, detection_thread = None):
        super().__init__(chromatic)
        self.chromatic_session = chromatic_session
        self.game_data = game_data
        self.game_save_settings = game_save_settings
        self.animation_thread = animation_thread
        self.detection_thread = detection_thread

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def emit_progress(self = None, progress = None):
        offset_progress = ((100 - PATCH_PROGRESS_OFFSET) / 100) * progress
        self.progress.emit(PATCH_PROGRESS_OFFSET + offset_progress)

    __classcell__ = None


class CartClinicDetectFRAMSubprocess(CartClinicSubprocess):
    '''Check if FRAM exists on the cartridge'''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, cart_clinic_fw_path = None):
        super().__init__(chromatic, cart_clinic_fw_path)

    
    def detect_fram(self = None, chromatic_session = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    __classcell__ = None


class CartClinicGetGameSettingsSubprocess(ChromaticSubprocess):
    '''Read the ID sector of the inserted cartridge and pass it to MRPatcher
    to retrieve game save settings.
    '''
    finished = Signal(MRPatcherGameInfo)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, endpoint = None):
        super().__init__(chromatic)
        self.chromatic_session = chromatic_session
        self.endpoint = endpoint

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    __classcell__ = None


class CartClinicBackupSaveSubprocess(ChromaticSubprocess):
    '''Backup the game save data in FRAM to a user-provided file path'''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, save_path = None, fram_detected = None, game_info = None):
        super().__init__(chromatic)
        self._chromatic_session = chromatic_session
        self._save_path = save_path
        self._fram_detected = fram_detected
        self._game_info = game_info

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def get_save_data(self = None):
        '''Retrieves the save data either from FRAM or flash based on the cart/game save settings.'''
        if self._fram_detected:
            return self._chromatic_session.read_fram()
        game_handler = None(self._chromatic_session, self._game_info)
        return game_handler.get_save()

    __classcell__ = None


class CartClinicWriteSaveSubprocess(ChromaticSubprocess):
    '''
    Write the game save data in FRAM, either from a user-provided .sav file,
    or set to 0xFF to erase the save.
    '''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, save_path = None, fram_detected = None, game_info = None):
        super().__init__(chromatic)
        self._chromatic_session = chromatic_session
        self._save_path = save_path
        self._fram_detected = fram_detected
        self._game_info = game_info

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def write_save_data(self = None, save_data = None):
        '''Writes the save data either to FRAM or flash based on the cart/game save settings.'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    __classcell__ = None


class CartClinicEraseSaveSubprocess(ChromaticSubprocess):
    '''
    Write the game save data in FRAM, either from a user-provided .sav file,
    or set to 0xFF to erase the save.
    '''
    finished = Signal(bool)
    error = Signal(str)
    
    def __init__(self = None, chromatic = None, chromatic_session = None, fram_detected = None, game_info = None):
        super().__init__(chromatic)
        self._chromatic_session = chromatic_session
        self._fram_detected = fram_detected
        self._game_info = game_info

    
    def run(self):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def erase_save_data(self = None):
        '''Writes the save data either to FRAM or flash based on the cart/game save settings.'''
        if self._fram_detected:
            save_data = bytearray(b'\xff' * FRAM_SIZE)
            return self._chromatic_session.write_fram(save_data)
        game_handler = None(self._chromatic_session, self._game_info)
        return game_handler.erase_save()

    __classcell__ = None


def request_game_info(service_endpoint = None, game_bytes = None):
    '''Requests game ID based on ROM'''
    mrpatcher = MRPatcherAPI(service_endpoint)
    mrpatcher_res = mrpatcher.get_game_id(game_bytes)
    return mrpatcher_res


def request_game_patch(service_endpoint = None, game_bytes = None):
    '''Requests a patch for the game at the given path'''
    mrpatcher = MRPatcherAPI(service_endpoint)
    mrpatcher_res = mrpatcher.request_patch(game_bytes)
    return mrpatcher_res


def apply_game_patch(game_data = None, ips_base64 = None):
    '''Applies an IPS file to the given game ROM.'''
    decoded_ips = base64.b64decode(ips_base64)
    with tempfile.NamedTemporaryFile(False, 'wb', '.ips', **('delete', 'mode', 'suffix')) as patch_file:
        patch_file.write(decoded_ips)
        patch_file.flush()
        patch_path = patch_file.name
        None(None, None, None)
        # Incomplete decompilation - manual review needed
        pass
def require_mr_cartridge_inserted(session = None):
    '''Raises an error if a MR cartridge is not detected.'''
    (cart_detected, _) = session.detect_mr_cart()
    if not cart_detected:
        raise InvalidCartridgeError()

