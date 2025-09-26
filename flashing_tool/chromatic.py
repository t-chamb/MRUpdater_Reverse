# Source Generated with Decompyle++
# File: chromatic.pyc (Python 3.10)

import itertools
import logging
import os.path as os
import threading
import time
from typing import Callable, List
import statemachine
import usb.core as usb
from esptool.loader import ESPLoader, DEFAULT_CONNECT_ATTEMPTS
from statemachine import StateMachine, State
from flashing_tool.chromatic_subprocess import FlashFPGASubprocess, FlashMCUSubprocess, is_fpga_detected
from flashing_tool.esp_util import esp_connect_loop, get_mcu_port, find_usb_device
from flashing_tool.logging import IntervalSamplingFilter
from flashing_tool.util import is_env_manufacturing
flashing_tool_logger = logging.getLogger('mrupdater')

class ChromaticError(Exception):
    pass


class Chromatic(StateMachine):
    GOWIN_DEVICE_IDS = '0x33aa:0120'
    MODRETRO_DEVICE_IDS = '0x374e:0101'
    MCU_BAUD_RATE = 115200
    MCU_CHIP_TYPE = 'esp32'
    FPGA_FLASH_TIMEOUT = 600
    not_connected = State('Not Connected', True, **('initial',))
    detecting_firmware = State('Detecting Firmware')
    ready_to_flash = State('Ready To Flash')
    flashing = State('Flashing')
    flashing_error = State('Flashing Error')
    update_successful = State('Update Successful')
    cart_clinic_checking = State('Cart Clinic Checking')
    cart_clinic_processing_save = State('Cart Clinic Processing Save')
    cart_clinic_needs_update = State('Cart Clinic Needs Update')
    cart_clinic_uptodate = State('Cart Clinic Up To Date')
    cart_clinic_updating = State('Cart Clinic Updating')
    cart_clinic_success = State('Cart Clinic Success')
    cart_clinic_error = State('Cart Clinic Error')
    start_detection = not_connected.to(detecting_firmware)
    ready = detecting_firmware.to(ready_to_flash)
    start_flashing = ready_to_flash.to(flashing)
    complete_flashing = flashing.to(update_successful)
    fail_flashing = flashing.to(flashing_error)
    cart_clinic_check_game = ready_to_flash.to(cart_clinic_checking)
    cart_clinic_process_save = ready_to_flash.to(cart_clinic_processing_save)
    cart_clinic_game_needs_update = cart_clinic_checking.to(cart_clinic_needs_update)
    cart_clinic_game_uptodate = cart_clinic_checking.to(cart_clinic_uptodate)
    cart_clinic_update = cart_clinic_needs_update.to(cart_clinic_updating)
    cart_clinic_complete = cart_clinic_updating.to(cart_clinic_success)
    cart_clinic_finish_save = cart_clinic_processing_save.to(ready_to_flash)
    cart_clinic_fail = cart_clinic_updating.to(cart_clinic_error) | cart_clinic_checking.to(cart_clinic_error) | cart_clinic_processing_save.to(cart_clinic_error)
    cart_clinic_retry = cart_clinic_error.to(ready_to_flash)
    disconnect = detecting_firmware.to(not_connected) | ready_to_flash.to(not_connected) | flashing.to(not_connected) | flashing_error.to(not_connected) | update_successful.to(not_connected) | cart_clinic_checking.to(not_connected) | cart_clinic_needs_update.to(not_connected) | cart_clinic_uptodate.to(not_connected) | cart_clinic_error.to(not_connected) | cart_clinic_success.to(not_connected)
    
    def on_enter_detecting_firmware(self):
        self._set_hardware_attributes()
        if not self._polling_thread.is_alive():
            self._start_device_auto_detection()
            return None

    
    def on_enter_ready_to_flash(self):
        self._set_hardware_attributes()
        if not self._polling_thread.is_alive():
            self._start_device_auto_detection()
            return None

    
    def on_enter_flashing(self):
        self._stop_device_auto_detection()
        self._esp = None

    
    def on_enter_not_connected(self):
        self._init_hardware_attributes()
        self._start_device_auto_detection()
        self._esp = None

    
    def on_enter_update_successful(self):
        self._start_device_auto_detection()
        self._esp = None

    
    def on_enter_cart_clinic_checking(self):
        self._stop_device_auto_detection()
        self._esp = None

    
    def on_enter_cart_clinic_processing_save(self):
        self._stop_device_auto_detection()
        self._esp = None

    
    def after_transition(self, event, state):
        flashing_tool_logger.info("Received event '%s' to transition to the '%s' state", event, state)
        if self._on_state_transition_callback:
            self._on_state_transition_callback(event, state)
            return None

    
    def __init__(self = None, openfpga_loader_bin = None, progress_callback = None, on_state_transition_callback = None):
        if not os.path.isfile(openfpga_loader_bin):
            raise ChromaticError(f'''Invalid path to openFGPALoader executable: {openfpga_loader_bin}''')
        self._openfpga_loader_bin = openfpga_loader_bin
        self._progress_callback = progress_callback
        self._esp = None
        self._previous_status = None
        self._should_update_hardware_attrs = True
        self._flashing_lock = threading.RLock()
        self._flash_result = 0
        self._detect_thread = None
        self.fw_version = None
        self.logging_signal = IntervalSamplingFilter('fpga', 3, **('name', 'interval'))
        self._hardware_attributes = {
            'fpga': ('product', 'manufacturer'),
            'esp': ('chip_description', 'chip_features', 'crystal_freq') }
        self._init_hardware_attributes()
        self._auto_detect_keepalive = None
        self._on_state_transition_callback = on_state_transition_callback
        self._start_device_auto_detection()
        super(Chromatic, self).__init__()

    
    def get_esp(self = None, force_connect = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def fpga(self = None):
        (vendor_id, product_id) = map((lambda x: int(x, 16)), self.GOWIN_DEVICE_IDS.split(':'))
        return find_usb_device(vendor_id, product_id, **('vendor_id', 'product_id'))

    fpga = None(fpga)
    
    def mcu_port(self = None):
        '''Returns the name of the port for accessing the ModRetro MCU

        On new hardware, this property is only accessible after the
        FPGA has been flashed and the bridge comes up.
        '''
        (vendor_id, product_id) = map((lambda x: int(x, 16)), self.MODRETRO_DEVICE_IDS.split(':'))
        port = get_mcu_port(vendor_id, product_id, **('vendor_id', 'product_id'))
        return port

    mcu_port = None(mcu_port)
    
    def fpga_cable_name(self = None):
        '''Return the name of the cable for accessing the FPGA

        If the Chromatic loses connectivity, this property will
        return an empty string
        '''
        name = self.fpga_product
        if name and self.fpga is not None:
            name = self.fpga.product
        if name is not None:
            name = name.lower()
        return name

    fpga_cable_name = None(fpga_cable_name)
    
    def openfgpa_loader_bin(self):
        return self._openfpga_loader_bin

    openfgpa_loader_bin = property(openfgpa_loader_bin)
    
    def connected_states(self = None):
        return [
            self.ready_to_flash.id,
            self.detecting_firmware.id]

    connected_states = None(connected_states)
    
    def firmware_update_states(self = None):
        return [
            self.flashing.id]

    firmware_update_states = None(firmware_update_states)
    
    def unready_states(self = None):
        return [
            self.not_connected.id,
            self.detecting_firmware.id]

    unready_states = None(unready_states)
    
    def ready_states(self = None):
        return [
            self.ready_to_flash.id]

    ready_states = None(ready_states)
    
    def disconnected_states(self = None):
        return [
            self.not_connected.id]

    disconnected_states = None(disconnected_states)
    
    def error_states(self = None):
        return [
            self.flashing_error.id]

    error_states = None(error_states)
    
    def success_states(self = None):
        return [
            self.update_successful.id]

    success_states = None(success_states)
    
    def completion_events(self = None):
        return [
            self.complete_flashing.name]

    completion_events = None(completion_events)
    
    def cart_clinic_active_states(self = None):
        return [
            self.cart_clinic_checking.id,
            self.cart_clinic_processing_save.id,
            self.cart_clinic_needs_update.id,
            self.cart_clinic_updating.id,
            self.cart_clinic_uptodate.id,
            self.cart_clinic_error.id,
            self.cart_clinic_success.id]

    cart_clinic_active_states = None(cart_clinic_active_states)
    
    def cart_clinic_updating_states(self = None):
        return [
            self.cart_clinic_checking.id,
            self.cart_clinic_processing_save.id,
            self.cart_clinic_updating.id]

    cart_clinic_updating_states = None(cart_clinic_updating_states)
    
    def failure_events(self = None):
        return [
            self.fail_flashing.name]

    failure_events = None(failure_events)
    
    def set_fw_version(self, version):
        self.fw_version = version

    
    def flash_both_start(self = None, mcu_filepath = None, fpga_filepath = None):
        self.start_flashing()
        self._stop_device_auto_detection()
        if not is_fpga_detected(self):
            raise ChromaticError('The Chromatic cannot be flashed. Reconnect the device and try again')
        fpga_cable_name = self.fpga_cable_name
        # Assignment completed
    def flash_both_p1_callback(self, rc, mcu_filepath):
        self._flash_result = rc
        if rc != 0:
            self.fail_flashing()
            return None
        None.flash_both_p2(mcu_filepath)

    
    def flash_both_p2(self = None, filepath = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def flash_both_p2_callback(self, rc):
        self._flash_result = rc
        if rc != 0:
            self.fail_flashing()
            return None
        None.complete_flashing()

    
    def update_status(self):
        current_thread = threading.current_thread()
        polling_thread_name = self._polling_thread.name if self._polling_thread else None
        if current_thread.name != polling_thread_name:
            self._flashing_lock.acquire()
        # Property or method access
    def _init_hardware_attributes(self = None, component = None):
        all_attrs = []
        # Assignment completed
    def _set_hardware_attributes(self = None):
        self._set_fpga_attributes()

    
    def _set_fpga_attributes(self):
        flashing_tool_logger.info(f'''{self.logging_signal} Searching for USB device with vid/pid: {self.GOWIN_DEVICE_IDS}''')
        fpga = self.fpga
        if fpga is None:
            return None
        for attr in self._hardware_attributes['fpga']:
            value = getattr(fpga, attr)
            setattr(self, f'''fpga_{attr}''', value)
        :
            flashing_tool_logger.info(f'''{self.logging_signal} Searching for USB device with vid/pid: {self.GOWIN_DEVICE_IDS}''')
            fpga = self.fpga
            if fpga is None:
                return None
            for attr in self._hardware_attributes['fpga']:
                value = getattr(fpga, attr)
                setattr(self, f'''fpga_{attr}''', value)
            
            return None
        return None
        # Return statement completed
    def _perform_device_poll(self = None):
        timeout = 1
        # Assignment completed
    def _stop_device_auto_detection(self):
        if self._on_state_transition_callback is not None:
            self._auto_detect_keepalive.set()
            return None

    
    def _start_device_auto_detection(self = None):
        if self._auto_detect_keepalive is None:
            self._auto_detect_keepalive = threading.Event()
        elif self._auto_detect_keepalive.is_set():
            self._auto_detect_keepalive.clear()
        self._polling_thread = threading.Thread('auto_detect_daemon', self._perform_device_poll, True, **('name', 'target', 'daemon'))
        flashing_tool_logger.info('Checking for connected device')
        self._polling_thread.start()

    
    def dispose(self = None):
        self.disconnect()

    __classcell__ = None

