# Source Generated with Decompyle++
# File: gui.pyc (Python 3.10)

import base64
import logging
import os
from pathlib import Path
import serial
import random
import time
from cartclinic.consts import LOADING_TEXT_DEFAULT, LOADING_TEXT_SNIPPETS, CartClinicFeature, CartClinicConfigItem, CartClinicSaveOperation
from flashing_tool.chromatic import Chromatic
from flashing_tool.config_parser import ConfigParser
from flashing_tool.features.manager import IFeatureManager
from flashing_tool.gui.changelog_dialog import ChangelogDialog
from flashing_tool.gui.generated import Ui_CartClinicTab, Ui_CCStartScreen, Ui_CCCheckScreen, Ui_CCConnectScreen, Ui_CCErrorScreen, Ui_CCLoadingScreen, Ui_CCSaveScreen, Ui_CCSuccessScreen, Ui_CCUpdateScreen, Ui_CCUpdatingScreen, Ui_CCUpToDateScreen
from flashing_tool.ui_flasher_form import Ui_FlasherForm
from libpyretro.cartclinic.comms import Session, Transport, Transporter, TransportKind
from libpyretro.cartclinic.protocol.common import CmdId
from cartclinic.animation import AnimateChromaticSubprocess
from cartclinic.cc_subprocess import FRAM_SIZE, CartClinicBackupSaveSubprocess, CartClinicCheckSubprocess, CartClinicDetectFRAMSubprocess, CartClinicEraseSaveSubprocess, CartClinicGetGameSettingsSubprocess, CartClinicUpdateSubprocess, CartClinicHomebrewSubprocess, CartClinicWriteSaveSubprocess, DetectCartridgeSubprocess, DetectChromaticSubprocess
from cartclinic.mrpatcher import MRPatcherGameInfo, MRPatcherResponse
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QFileDialog
from statemachine import State
from flashing_tool.util import CartClinicFirmwarePackage, resolve_path
logger = logging.getLogger('mrupdater')

class CartClinic:
    
    def __init__(self, main_gui, chromatic = None, form = None, feature_manager = None, app_config = ('chromatic', Chromatic, 'form', Ui_FlasherForm, 'feature_manager', IFeatureManager, 'app_config', ConfigParser)):
        self._main_gui = main_gui
        self._chromatic = chromatic
        self._form = form
        self._feature_manager = feature_manager
        self._app_config = app_config
        self._cc_mrpatcher_response = None
        self._cc_current_cart_data = None
        self._cc_session = None
        self._cart_clinic_fw_path = None
        self._cc_check_progress = 0
        self._cc_save_op = CartClinicSaveOperation.BACKUP
        self._cc_check_thread = None
        self._cc_animation_thread = None
        self._cc_detection_thread = None
        self._cc_chromatic_thread = None
        self._cc_update_thread = None
        self._cc_save_op_thread = None
        self._cc_save_detect_thread = None

    
    def load_screens(self):
        self._cc_tab = self._main_gui._cc_tab
        self._start_screen = self._main_gui.load_screen(Ui_CCStartScreen, self._cc_tab.screen_cc_start)
        self._connect_screen = self._main_gui.load_screen(Ui_CCConnectScreen, self._cc_tab.screen_cc_connect)
        self._check_screen = self._main_gui.load_screen(Ui_CCCheckScreen, self._cc_tab.screen_cc_check)
        self._error_screen = self._main_gui.load_screen(Ui_CCErrorScreen, self._cc_tab.screen_cc_error)
        self._loading_screen = self._main_gui.load_screen(Ui_CCLoadingScreen, self._cc_tab.screen_cc_loading)
        self._save_screen = self._main_gui.load_screen(Ui_CCSaveScreen, self._cc_tab.screen_cc_save)
        self._success_screen = self._main_gui.load_screen(Ui_CCSuccessScreen, self._cc_tab.screen_cc_success)
        self._update_screen = self._main_gui.load_screen(Ui_CCUpdateScreen, self._cc_tab.screen_cc_update)
        self._updating_screen = self._main_gui.load_screen(Ui_CCUpdatingScreen, self._cc_tab.screen_cc_updating)
        self._uptodate_screen = self._main_gui.load_screen(Ui_CCUpToDateScreen, self._cc_tab.screen_cc_uptodate)
        self.init_buttons()

    
    def init_buttons(self):
        self._start_screen.cc_btn_check.clicked.connect(self.cart_clinic_check)
        self._start_screen.cc_homebrew_btn.clicked.connect(self.cart_clinic_homebrew)
        self._update_screen.cc_update_btn.clicked.connect(self.cart_clinic_update)
        self._error_screen.cc_retry_btn.clicked.connect(self.retry_cart_clinic)
        self._update_screen.cc_cancel_btn.clicked.connect(self.cancel_cart_clinic)
        self._update_screen.cc_changelog_btn.clicked.connect(self.show_changelog_dialog)
        self._success_screen.cc_ok_done_btn.clicked.connect(self.disconnect_cart_clinic)
        self._uptodate_screen.cc_ok_uptodate_btn.clicked.connect(self.disconnect_cart_clinic)
        None((lambda _ = None: self.setup_save_operation(CartClinicSaveOperation.BACKUP)))
        None((lambda _ = None: self.setup_save_operation(CartClinicSaveOperation.RESTORE)))
        None((lambda _ = None: self.setup_save_operation(CartClinicSaveOperation.ERASE)))

    
    def set_mrpatcher_endpoint(self = None, endpoint = None):
        self._mrpatcher_endpoint = endpoint

    
    def developer_mode(self = None):
        return self._feature_manager.is_feature_enabled(CartClinicFeature.DEVELOPER_MODE)

    developer_mode = None(developer_mode)
    
    def _previous_homebrew_dir(self = None):
        prev_dir = self._app_config.get(CartClinicConfigItem.PREVIOUS_HOMEBREW_DIR)
        if not prev_dir:
            return Path.home()
        return None(prev_dir)

    _previous_homebrew_dir = None(_previous_homebrew_dir)
    
    def _previous_homebrew_dir(self = None, prev_dir = None):
        self._app_config.set(CartClinicConfigItem.PREVIOUS_HOMEBREW_DIR, str(prev_dir))

    _previous_homebrew_dir = None(_previous_homebrew_dir)
    
    def _previous_save_dir(self = None):
        prev_dir = self._app_config.get(CartClinicConfigItem.PREVIOUS_SAVE_DIR)
        if not prev_dir:
            return Path.home()
        return None(prev_dir)

    _previous_save_dir = None(_previous_save_dir)
    
    def _previous_save_dir(self = None, prev_dir = None):
        self._app_config.set(CartClinicConfigItem.PREVIOUS_SAVE_DIR, str(prev_dir))

    _previous_save_dir = None(_previous_save_dir)
    
    def download_cc_fw_callback(self = None, fw_package = None):
        logger.info(f'''Cart Clinic firmware download successful: {fw_package.fpga_fw_path}''')
        self._cc_tmp_dir_holder = fw_package.temp_dir_path
        self._cart_clinic_fw_path = fw_package.fpga_fw_path
        self._main_gui.update_screens()

    
    def retry_cart_clinic(self):
        '''In a failure state, retry moves back to the checking state'''
        self._chromatic.cart_clinic_retry()

    
    def disconnect_cart_clinic(self):
        '''When the workflow reaches an end state, disconnect Chromatic
        to start over.
        '''
        self._chromatic.disconnect()

    
    def cancel_cart_clinic(self):
        '''When the user presses the cancel button, perform cleanup and
        then disconnect to reset the workflow.
        '''
        logger.info('Update cancelled')
        self.cleanup_cart_clinic()
        self.disconnect_cart_clinic()

    
    def cart_clinic_check(self):
        '''This gets called when the user presses the Cart Clinic
        check button and kicks off the first part of the workflow.
        '''
        if not self._mrpatcher_endpoint or self._cart_clinic_fw_path:
            logger.warning('Cart Clinic not yet set up')
            return None
        if not None._main_gui.show_prompt('Warning', 'This action will turn off your game. Make sure you saved your progress.\nDo you wish to proceed?'):
            return None
        None.info('Starting cart clinic...')
        self.reset_cart_clinic()
        self._chromatic.cart_clinic_check_game()
        self._cc_check_thread = CartClinicCheckSubprocess(self._chromatic, self._cart_clinic_fw_path, self._mrpatcher_endpoint, **('chromatic', 'cart_clinic_fw_path', 'mrpatcher_endpoint'))
        self._cc_check_thread.error.connect(self.cart_clinic_error)
        self._cc_check_thread.finished.connect(self.cart_clinic_check_callback)
        self._cc_check_thread.text_timer_signal.connect(self.update_checking_game_text)
        self._cc_check_thread.progress.connect(self.cart_clinic_check_progress_callback)
        self._cc_check_thread.setup_complete_signal.connect(self.cart_clinic_setup_complete_callback)
        self._cc_check_thread.current_cart_data.connect(self.set_current_cart_data)
        self._cc_check_thread.start()

    
    def _create_session(self = None):
        serial_handle = serial.Serial(self._chromatic.mcu_port, 115200, 0.001, **('port', 'baudrate', 'timeout'))
        self._cc_session = Session(Transporter(Transport(TransportKind.Serial, serial_handle)))
        self._cc_session.tporter.add_listener([
            CmdId.SetFrameBufferPixel])
        return self._cc_session

    
    def cart_clinic_setup_complete_callback(self, _):
        '''After flashing SRAM, open the serial handle, load the animation,
        and start reading from the cartridge.
        '''
        logger.info('Cart Clinic firmware loaded')
        session = self._create_session()
        self._cc_animation_thread = AnimateChromaticSubprocess(session, **('chromatic_session',))
        self._cc_animation_thread.start()
        self._cc_animation_thread.run_once()
        self._cc_detection_thread = DetectCartridgeSubprocess(session, **('chromatic_session',))
        self._cc_detection_thread.start()
        self._cc_chromatic_thread = DetectChromaticSubprocess(session, **('chromatic_session',))
        self._cc_chromatic_thread.error.connect(self.chromatic_connection_lost)
        self._cc_chromatic_thread.start()
        self._cc_check_thread.start_check_cartridge(session, self._cc_animation_thread, self._cc_detection_thread)

    
    def cart_clinic_homebrew(self):
        if not self.developer_mode:
            return None
        (rom_path, _) = None.getOpenFileName(self._main_gui, 'Select a Homebrew ROM', str(self._previous_homebrew_dir), 'Game Boy Files (*.gb *.gbc *.bin)')
        if not rom_path:
            return None
        self._previous_homebrew_dir = None(rom_path).parent
        self.reset_cart_clinic()
        self._chromatic.cart_clinic_check_game()
        logger.info(f'''Writing homebrew ROM {rom_path!r}''')
        self._cc_homebrew_thread = CartClinicHomebrewSubprocess(self._chromatic, self._cart_clinic_fw_path, rom_path, **('chromatic', 'cart_clinic_fw_path', 'homebrew_game_path'))
        self._cc_homebrew_thread.error.connect(self.cart_clinic_error)
        self._cc_homebrew_thread.finished.connect(self.cart_clinic_homebrew_finished_callback)
        self._cc_homebrew_thread.text_timer_signal.connect(self.update_checking_game_text)
        self._cc_homebrew_thread.progress.connect(self.cart_clinic_check_progress_callback)
        self._cc_homebrew_thread.setup_complete_signal.connect(self.cart_clinic_homebrew_setup_complete_callback)
        self._cc_homebrew_thread.start()

    
    def cart_clinic_homebrew_setup_complete_callback(self, _):
        '''After flashing SRAM, open the serial handle, load the animation,
        and start writing the homebrew rom
        '''
        logger.info('Cart Clinic firmware loaded, writing homebrew ROM')
        session = self._create_session()
        self._cc_animation_thread = AnimateChromaticSubprocess(session, **('chromatic_session',))
        self._cc_animation_thread.start()
        self._cc_animation_thread.run_once()
        self._cc_detection_thread = DetectCartridgeSubprocess(session, **('chromatic_session',))
        self._cc_detection_thread.start()
        self._cc_chromatic_thread = DetectChromaticSubprocess(session, **('chromatic_session',))
        self._cc_chromatic_thread.error.connect(self.chromatic_connection_lost)
        self._cc_chromatic_thread.start()
        self._cc_homebrew_thread.start_write_homebrew(session, self._cc_animation_thread, self._cc_detection_thread)

    
    def cart_clinic_homebrew_finished_callback(self = None, success = None):
        logger.info('Finished writing homebrew ROM')
        self.cleanup_cart_clinic()
        if success:
            self._chromatic.cart_clinic_game_uptodate()
            return None
        None._chromatic.cart_clinic_fail()

    
    def show_save_warning_prompt(self = None):
        return self._main_gui.show_prompt('Warning', self._cc_save_op.value.warning_message)

    
    def show_save_success_message(self):
        self._main_gui.show_message_box('Success', self._cc_save_op.value.success_message)

    
    def setup_save_operation(self = None, operation = None):
        '''Start a save operation by detecting FRAM on the cartridge'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def setup_save_operation_callback(self):
        session = self._create_session()
        if not self._cc_save_detect_thread.check_mr_cart_inserted(session):
            return None
        None((lambda fram_detected = None: self.cart_clinic_fram_detect_callback(session, fram_detected)))
        self._cc_save_detect_thread.detect_fram(session)

    
    def cart_clinic_fram_detect_callback(self = None, session = None, fram_detected = None):
        '''
        If FRAM is detected, continue with the save operation as usual
        If not detected, we need to identify the game and get its save settings
        from MRPatcher.
        '''
        logger.info(f'''FRAM detected: {fram_detected}''')
        if fram_detected:
            self._cc_save_game_info = None
            return self.continue_save_operation(session, fram_detected)
        self._cc_save_id_thread = None(self._chromatic, session, self._mrpatcher_endpoint, **('chromatic', 'chromatic_session', 'endpoint'))
        None((lambda game_info = None: self.cart_clinic_get_game_settings_finished_callback(session, game_info)))
        self._cc_save_id_thread.error.connect(self.cart_clinic_error)
        self._cc_save_id_thread.start()

    
    def cart_clinic_get_game_settings_finished_callback(self = None, session = None, game_info = None):
        logger.info('Finished getting game settings')
        logger.info(game_info)
        self._cc_save_game_info = game_info
        self.continue_save_operation(session, False)

    
    def continue_save_operation(self = None, session = None, fram_detected = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def save_backup(self = None, session = None, fram_detected = None):
        logger.info(f'''Backing up save to file {self._cc_save_path}''')
        self._cc_save_op_thread = CartClinicBackupSaveSubprocess(self._chromatic, session, self._cc_save_path, fram_detected, self._cc_save_game_info, **('chromatic', 'chromatic_session', 'save_path', 'fram_detected', 'game_info'))
        self._cc_save_op_thread.error.connect(self.cart_clinic_error)
        self._cc_save_op_thread.finished.connect(self.cart_clinic_save_operation_finished_callback)
        self._cc_save_op_thread.start()

    
    def save_restore(self = None, session = None, fram_detected = None):
        self._cc_save_op_thread = CartClinicWriteSaveSubprocess(self._chromatic, session, self._cc_save_path, fram_detected, self._cc_save_game_info, **('chromatic', 'chromatic_session', 'save_path', 'fram_detected', 'game_info'))
        self._cc_save_op_thread.error.connect(self.cart_clinic_error)
        self._cc_save_op_thread.finished.connect(self.cart_clinic_save_operation_finished_callback)
        self._cc_save_op_thread.start()

    
    def save_erase(self = None, session = None, fram_detected = None):
        self._cc_save_op_thread = CartClinicEraseSaveSubprocess(self._chromatic, session, fram_detected, self._cc_save_game_info, **('chromatic', 'chromatic_session', 'fram_detected', 'game_info'))
        self._cc_save_op_thread.error.connect(self.cart_clinic_error)
        self._cc_save_op_thread.finished.connect(self.cart_clinic_save_operation_finished_callback)
        self._cc_save_op_thread.start()

    
    def cart_clinic_save_operation_finished_callback(self, _):
        logger.info('Finished save operation')
        self.cleanup_cart_clinic()
        self._chromatic.cart_clinic_finish_save()
        self.show_save_success_message()

    
    def set_current_cart_data(self = None, cart_data = None):
        self._cc_current_cart_data = cart_data

    
    def chromatic_connection_lost(self = None, exception = None):
        if self._chromatic.current_state.id not in self._chromatic.cart_clinic_updating_states:
            return None
        None.error(exception)
        self.cart_clinic_error('LOST CONNECTION TO CHROMATIC')

    
    def cart_clinic_error(self = None, error = None):
        '''This method should run if any error happens during the Cart Clinic
        workflow. All paths lead either here or cart_clinic_update_callback
        or Chromatic.cart_clinic_uptodate.
        '''
        logger.error(error)
        self._chromatic.cart_clinic_fail()
        self.cleanup_cart_clinic()
        error_lines = error.split('\n')
        primary_error_msg = error_lines[0]
        secondary_error_msg = ''
        if len(error_lines) > 1:
            secondary_error_msg = error_lines[1]
        self.set_cc_error_text(primary_error_msg, secondary_error_msg)

    
    def cart_clinic_check_callback(self = None, mrpatcher_response = None):
        logger.info('Cart Clinic check complete!')
        self._cc_mrpatcher_response = mrpatcher_response
        response_info = f'''Response:\nGame: {mrpatcher_response.game_title}\n'''
        response_info += f'''Needs Update: {mrpatcher_response.needs_update}\n'''
        response_info += f'''Save Compatible: {mrpatcher_response.save_compatible}\n'''
        response_info += f'''Uploaded Version: {mrpatcher_response.uploaded_version}\n'''
        response_info += f'''Latest Version: {mrpatcher_response.latest_version}\n'''
        if mrpatcher_response.error:
            response_info += f'''User Error: {mrpatcher_response.user_error}\n'''
            response_info += f'''Error: {mrpatcher_response.error}\n'''
        logger.info(response_info)
        if not mrpatcher_response.user_error or mrpatcher_response.game_title:
            self.cart_clinic_error('THE GAME WAS NOT RECOGNIZED')
            return None
        if None.error:
            self.cart_clinic_error(f'''SERVER ERROR ({mrpatcher_response.error_code})\nPLEASE TRY AGAIN LATER''')
            return None
        if not None.needs_update:
            self._chromatic.cart_clinic_game_uptodate()
            self.cleanup_cart_clinic()
            return None
        if None.save_compatible:
            self._update_screen.text_cc_save_warning.setVisible(False)
            self._update_screen.text_cc_save_warning2.setVisible(False)
        self._chromatic.cart_clinic_game_needs_update()

    
    def show_changelog_dialog(self = None):
        '''Show the changes between the current and latest versions of the game.'''
        if not self._cc_mrpatcher_response or self._cc_mrpatcher_response.patch:
            logger.warning('Missing MRPatcher response')
            return None
        changelog_text = None
        if not self._cc_mrpatcher_response.uploaded_version:
            changelog_text += "We couldn't determine your current version. We recommend updating anyway.\n\n"
        elif self._cc_mrpatcher_response.uploaded_version == self._cc_mrpatcher_response.latest_version:
            changelog_text += 'You have the latest version but may have corrupt data. We recommend updating anyway.\n\n'
        else:
            changelog_text += f'''# Updating from v{self._cc_mrpatcher_response.uploaded_version} to v{self._cc_mrpatcher_response.latest_version}\n\n\n'''
            changelog_text += self._cc_mrpatcher_response.changes
        changelog_dialog = ChangelogDialog(f'''Changelog for {self._cc_mrpatcher_response.game_title.upper()}''', changelog_text, **('title', 'text'))
        changelog_dialog.exec()

    
    def cart_clinic_update(self):
        '''This gets called after MRPatcher responds and has given us an IPS'''
        if not self._cc_mrpatcher_response or self._cc_mrpatcher_response.patch:
            logger.warning('Missing MRPatcher response')
            return None
        if not None._cc_current_cart_data:
            logger.warning('Missing old cartridge data')
            return None
        if not None._cc_mrpatcher_response.save_compatible and self._main_gui.show_prompt('Warning', 'Updating this game cartridge will invalidate your saved data.\nDo you wish to proceed with the update?'):
            return None
        save_settings = None._cc_mrpatcher_response.save_settings
        if save_settings:
            save_settings.save_compatible = self._cc_mrpatcher_response.save_compatible
        logger.info('Starting cart clinic update...')
        self._chromatic.cart_clinic_update()
        self._cc_update_thread = CartClinicUpdateSubprocess(self._chromatic, self._cc_session, self._cc_mrpatcher_response.patch, self._cc_current_cart_data, self._cc_mrpatcher_response.save_settings, self._cc_animation_thread, self._cc_detection_thread, **('chromatic', 'chromatic_session', 'ips_base64', 'cart_game_data', 'game_save_settings', 'animation_thread', 'detection_thread'))
        self._cc_update_thread.error.connect(self.cart_clinic_error)
        self._cc_update_thread.finished.connect(self.cart_clinic_update_callback)
        self._cc_update_thread.progress.connect(self.cart_clinic_progress_callback)
        self._cc_update_thread.start()

    
    def cart_clinic_update_callback(self = None, result = None):
        self.cleanup_cart_clinic()
        if result:
            self._chromatic.cart_clinic_complete()
            return None
        None._chromatic.cart_clinic_fail()

    
    def cart_clinic_check_progress_callback(self = None, progress = None):
        self._cc_check_progress = progress
        self.update_checking_game_text(None, False, **('increment',))

    
    def update_checking_game_text(self, _, increment = (True,)):
        '''Update the progress text and append progress percentage'''
        if self._cc_check_progress >= 95:
            text = 'WRAPPING UP...'
        elif self._loading_text_index < len(self._loading_text_snippets):
            text = self._loading_text_snippets[self._loading_text_index]
        text = f'''{text} ({self._cc_check_progress}%)'''
        self._check_screen.text_cc_checking.setText(text)

    
    def cart_clinic_progress_callback(self = None, progress = None):
        self._main_gui.draw_progress_bar(progress, self._updating_screen, 'cc_progress_')

    
    def reset_cart_clinic(self = None):
        self.set_cc_error_text('Something went wrong')
        self._cc_check_progress = 0
        self._loading_text_index = 0
        self._check_screen.text_cc_checking.setText(LOADING_TEXT_DEFAULT)
        self._loading_text_snippets = random.sample(LOADING_TEXT_SNIPPETS, len(LOADING_TEXT_SNIPPETS), **('k',))
        self.set_current_cart_data(None)
        self._cc_mrpatcher_response = None
        self.cart_clinic_progress_callback(0)
        self._update_screen.text_cc_save_warning.setVisible(True)
        self._update_screen.text_cc_save_warning2.setVisible(True)

    
    def cleanup_cart_clinic(self = None, is_shutting_down = None):
        if self._cc_session:
            logger.info('Cleaning up...')
            if self._cc_animation_thread:
                self._cc_animation_thread.stop()
                self._cc_animation_thread.wait()
            if self._cc_detection_thread:
                self._cc_detection_thread.stop()
                self._cc_detection_thread.wait()
            if self._cc_chromatic_thread:
                self._cc_chromatic_thread.stop()
                self._cc_chromatic_thread.wait()
            if self._cc_check_thread and self._cc_check_thread.isRunning():
                self._cc_check_thread.wait()
            if self._cc_update_thread and self._cc_update_thread.isRunning():
                self._cc_update_thread.wait()
            if self._cc_save_detect_thread and self._cc_save_detect_thread.isRunning():
                self._cc_save_detect_thread.wait()
            if self._cc_save_op_thread and self._cc_save_op_thread.isRunning():
                self._cc_save_op_thread.wait()
            self._cc_session.tporter.remove_listener([
                CmdId.SetFrameBufferPixel])
            self._cc_session.tporter.stop()
            self._cc_session = None
            self._main_gui.reset_fpga()
            if is_shutting_down:
                time.sleep(0.5)
                return None
            return None

    
    def set_cc_error_text(self = None, error_msg = None, secondary_error_msg = None):
        self._error_screen.text_cc_error.setText(error_msg)
        self._error_screen.text_cc_error_2.setText(secondary_error_msg)

    
    def display_cart_label(self = None, label_base64 = None):
        '''Display the given base64 image on the cartridge label
        on the cart clinic tab.'''
        image_data = base64.b64decode(label_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(image_data))
        self._uptodate_screen.cartridge_label1.setPixmap(pixmap)
        self._uptodate_screen.cartridge_label1.raise_()
        self._update_screen.cartridge_label2.setPixmap(pixmap)
        self._update_screen.cartridge_label2.raise_()

    
    def display_homebrew_cart_label(self = None):
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def update_screens(self = None, main_tab_ready = None, chromatic_state = None):
        '''Return the screens and extra elements to be displayed given the current state'''
        show_screens = []
        show_extras = []
        if not main_tab_ready:
            if chromatic_state.id == self._chromatic.not_connected.id:
                show_screens.append(self._cc_tab.screen_cc_connect)
                return (show_screens, show_extras)
            None.append(self._cc_tab.screen_cc_loading)
            show_extras = [
                self._cc_tab.cc_gears]
            self._loading_screen.text_cc_loading.setText('CHECKING CHROMATIC...')
            return (show_screens, show_extras)
        if not None._cart_clinic_fw_path or self._mrpatcher_endpoint:
            show_extras = [
                self._cc_tab.cc_gears]
            show_screens.append(self._cc_tab.screen_cc_loading)
            self._loading_screen.text_cc_loading.setText('ESTABLISHING CONNECTION...')
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_checking.id:
            show_extras = [
                self._cc_tab.cc_gears]
            show_screens.append(self._cc_tab.screen_cc_check)
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_processing_save.id:
            show_extras = [
                self._cc_tab.cc_gears]
            self._save_screen.text_cc_save_label.setText(self._cc_save_op.value.status_message)
            show_screens.append(self._cc_tab.screen_cc_save)
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_error.id:
            show_screens.append(self._cc_tab.screen_cc_error)
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_needs_update.id:
            show_screens.append(self._cc_tab.screen_cc_update)
            if self._cc_mrpatcher_response.thumbnail:
                self.display_cart_label(self._cc_mrpatcher_response.thumbnail)
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_uptodate.id:
            show_screens.append(self._cc_tab.screen_cc_uptodate)
            if self._cc_mrpatcher_response and self._cc_mrpatcher_response.thumbnail:
                self.display_cart_label(self._cc_mrpatcher_response.thumbnail)
                return (show_screens, show_extras)
            None.display_homebrew_cart_label()
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_updating.id:
            show_screens.append(self._cc_tab.screen_cc_updating)
            return (show_screens, show_extras)
        if None.id == self._chromatic.cart_clinic_success.id:
            show_screens.append(self._cc_tab.screen_cc_success)
            return (show_screens, show_extras)
        None.append(self._cc_tab.screen_cc_start)
        if self.developer_mode:
            show_extras.append(self._start_screen.cc_homebrew)
        return (show_screens, show_extras)


