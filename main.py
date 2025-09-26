Warning: Stack history is not empty!
Warning: block stack is not empty!
WARNING: Circular reference detected
# Source Generated with Decompyle++
# File: main.pyc (Python 3.10)

import logging
import math
import sys
import time
from pathlib import Path
from typing import Any
from PySide6.QtCore import Qt, QEvent, QObject, QUrl
from PySide6.QtGui import QIcon, QMovie, QPixmap, QFontDatabase, QFontMetrics, QDesktopServices, QShortcut, QKeySequence, QTransform
from PySide6.QtWidgets import QApplication, QMainWindow, QMessageBox, QLabel, QDialog, QWidget, QInputDialog
from cartclinic.gui import CartClinic
from config import __version__, __version_sha__
from flashing_tool.chromatic import Chromatic, ChromaticError
from flashing_tool.chromatic_subprocess import ProcessManifest, WaitForTime, DownloadFirmware, DetectVersionSubprocess, reset_fpga
from flashing_tool.config_parser import ConfigParser
from flashing_tool.constants import APP_NAME, CHROMATIC_MANUAL_LINK, MRUpdaterFeature
from flashing_tool.gui import ChangelogDialog, ConsentDialog, ErrorDialog
from flashing_tool.gui.generated import Ui_SystemTab, Ui_CartClinicTab, Ui_AboutScreen, Ui_SystemConnectScreen, Ui_SystemCheckScreen, Ui_SystemErrorScreen, Ui_SystemInternetScreen, Ui_SystemUpdateScreen, Ui_SystemUpdatingScreen, Ui_SystemUpToDateScreen, Ui_SystemSuccessScreen
from flashing_tool.initializer import configure_usb_backend, configure_logging, check_os_permissions, ApplicationStartupError, GowinDriverIsMissingError, install_gowin_driver, PrivilegeEscalationError
from flashing_tool.ui_flasher_form import Ui_FlasherForm
from flashing_tool.ui_util import UITab
from flashing_tool.util import ChromaticFirmwarePackage, MRUpdaterManifestData, S3FirmwareInfo, is_env_dev, get_openfpga_loader_bin_path
from flashing_tool.features import FeatureManager
from libpyretro.feature_api import FeatureAPIClient
flashing_tool_logger = logging.getLogger('mrupdater')
if is_env_dev():
    FEATURE_API_URL = 'https://8xlzcdo2o6.execute-api.us-east-1.amazonaws.com'
else:
    FEATURE_API_URL = 'https://7hcmw5socl.execute-api.us-east-1.amazonaws.com'
feature_manager = FeatureManager(FeatureAPIClient(FEATURE_API_URL))

try:
    from flashing_tool.plugins.base import PluginManager
    plugins = PluginManager(feature_manager)
finally:
    pass
from flashing_tool import EmptyObject
plugins = EmptyObject()

class GUI(QMainWindow):
    _activation_code_shortcut: QShortcut = 13
    
    def __init__(self = None):
        super(GUI, self).__init__()
        self._form = None
        self.dragging = False
        self._chromatic = None
        self._flashing_start_time = None
        self._timer_keepalive = None
        self._progress_modifier = (1, 0)
        self._pause_success = False
        self._state_enabled = False
        self._selected_fw_index = 0
        self._firmware_options = []
        self._latest_fw_version = None
        self._download_failure = False
        self._detect_failure = False
        self._flash_failure = False
        self._cart_clinic_available = False
        self._current_tab = None
        self._manifest_thread = None
        self._downloader_thread = None
        self._detect_thread = None
        self._chromatic = Chromatic(get_openfpga_loader_bin_path(), self.update_progress_bar, self.on_chromatic_state_transition, **('openfpga_loader_bin', 'progress_callback', 'on_state_transition_callback'))
        self.load_gui()
        self.start_downloads()

    
    def selected_firmware(self = None):
        '''Returns the currently selected firmware package.'''
        if not self._firmware_options:
            return None
        :
            if not self._firmware_options:
                return None
            
            return self._firmware_options[self._selected_fw_index]
            return None
        return self._firmware_options[self._selected_fw_index]

    selected_firmware = None(selected_firmware)
    
    def preview_firmware_accessible(self = None):
        return feature_manager.is_feature_enabled(MRUpdaterFeature.PREVIEW_FIRMWARE)

    preview_firmware_accessible = None(preview_firmware_accessible)
    
    def rollback_firmware_accessible(self = None):
        return feature_manager.is_feature_enabled(MRUpdaterFeature.ROLLBACK_FIRMWARE)

    rollback_firmware_accessible = None(rollback_firmware_accessible)
    
    def fw_selection_enabled(self = None):
        if not not plugins.is_plugin_enabled_for_user('manufacturing-tab') and self.preview_firmware_accessible:
            pass
        return self.rollback_firmware_accessible

    fw_selection_enabled = None(fw_selection_enabled)
    
    def load_gui(self):
        self._form = Ui_FlasherForm()
        self._form.setupUi(self)
        self._top_level_widget = self._form.tab_system.parent()
        self._cart_clinic = CartClinic(self, self._chromatic, self._form, feature_manager, app_config)
        self.setWindowIcon(QIcon(':/images/images/icon.ico'))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.load_screens()
        self.show()
        self.load_fonts()
        self.init_event_listeners()
        self.load_icons()
        title = f'''{APP_NAME} - {__version_sha__}'''
        self.setWindowTitle(title)
        self._about_tab.text_title.setText(title)
        self._about_tab.text_uptodate.setText('')

    
    def retry_download(self):
        self._download_failure = False
        self.start_downloads()
        self.update_screens()

    
    def retry_flash(self):
        self._flash_failure = False
        self._chromatic.disconnect()
        self.update_screens()

    
    def load_screen(self, screen_class, parent_widget):
        screen_instance = screen_class()
        screen_instance.setupUi(parent_widget)
        return screen_instance

    
    def load_screens(self):
        self._system_tab = self.load_screen(Ui_SystemTab, self._form.tab_system)
        self._cc_tab = self.load_screen(Ui_CartClinicTab, self._form.tab_cartclinic)
        self._about_tab = self.load_screen(Ui_AboutScreen, self._form.tab_about)
        self._system_connect_screen = self.load_screen(Ui_SystemConnectScreen, self._system_tab.screen_connect)
        self._system_check_screen = self.load_screen(Ui_SystemCheckScreen, self._system_tab.screen_check)
        self._system_error_screen = self.load_screen(Ui_SystemErrorScreen, self._system_tab.screen_error)
        self._system_internet_screen = self.load_screen(Ui_SystemInternetScreen, self._system_tab.screen_internet)
        self._system_update_screen = self.load_screen(Ui_SystemUpdateScreen, self._system_tab.screen_update)
        self._system_updating_screen = self.load_screen(Ui_SystemUpdatingScreen, self._system_tab.screen_updating)
        self._system_uptodate_screen = self.load_screen(Ui_SystemUpToDateScreen, self._system_tab.screen_uptodate)
        self._system_success_screen = self.load_screen(Ui_SystemSuccessScreen, self._system_tab.screen_success)
        self._cart_clinic.load_screens()
        self._form.splash.show()
        hide_elements = (lambda .0: [ screen for screen in .0 if screen.objectName().startswith('screen_') ])(self._top_level_widget.findChildren(QWidget))
        hide_elements += [
            self._form.close_btn,
            self._form.chromatic_manual_link,
            self._form.dragger,
            self._form.tab_system,
            self._form.tab_about,
            self._form.tab_cartclinic,
            self._form.tab_manufacturing,
            self._form.btn_tab_manufacturing,
            self._system_tab.current_fw]
        for el in hide_elements:
            el.hide()
        bottom_elements = (lambda .0: [ el for el in .0 if el.objectName() == 'bg' ])(self._top_level_widget.findChildren(QWidget))
        for el in bottom_elements:
            el.lower()
        top_elements = [
            self._form.close_btn,
            self._form.dragger,
            self._system_update_screen.update_btn,
            self._form.chromatic_manual_link,
            self._form.btn_tab_system,
            self._form.btn_tab_cartclinic,
            self._form.btn_tab_about,
            self._form.btn_tab_manufacturing]
        for el in top_elements:
            el.raise_()
        self.waiter = WaitForTime(2.5, **('timeout',))
        self.waiter.finished.connect(self.end_splash)
        self.waiter.start()

    
    def load_tab(self = None, tab = None):
        tabs = {
            UITab.MANUFACTURING: self._form.tab_manufacturing,
            UITab.ABOUT: self._form.tab_about,
            UITab.CART_CLINIC: self._form.tab_cartclinic,
            UITab.SYSTEM: self._form.tab_system }
        if tab not in tabs:
            return None
        chromatic_manual_link = None._form.chromatic_manual_link
        chromatic_manual_link.hide() if tab == UITab.MANUFACTURING else chromatic_manual_link.show()
        if self._chromatic.current_state.id in self._chromatic.cart_clinic_active_states:
            return self.show_error_message('Please finish your Cart Clinic update first!', 'Warning')
        if not None == UITab.CART_CLINIC and self._cart_clinic_available:
            message = "Cart Clinic isn't ready! Please confirm your Chromatic is detected and fully updated."
            if self._chromatic.current_state.id in self._chromatic.disconnected_states:
                message = 'Chromatic not detected! Please plug in your Chromatic and try again.'
            if self._chromatic.current_state.id in self._chromatic.unready_states:
                message = 'Chromatic not ready! Please wait for firmware version to be detected.'
            if self._chromatic.current_state.id in self._chromatic.firmware_update_states:
                message = 'Chromatic update is in progress! Please follow the prompts on the System Update tab.'
            if self._chromatic.current_state.id in self._chromatic.success_states:
                message = 'Chromatic needs a reset! Please follow the prompts on the System Update tab.'
            return self.show_error_message(message, 'Warning')
        if None.is_plugin_enabled_for_user('manufacturing-tab'):
            if tab == UITab.CART_CLINIC:
                return self.show_error_message('Cart Clinic is disabled. Please use the manufacturing tab.')
            if None == UITab.MANUFACTURING:
                self._form.btn_tab_manufacturing.hide()
            else:
                self._form.btn_tab_manufacturing.show()
        for tab_key in tabs:
            tabs[tab_key].hide()
        tabs[tab].show()
        self._current_tab = tab

    
    def end_splash(self):
        if self._state_enabled:
            return None
        None.display_tabs(self)
        self._activation_code_shortcut = QShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_I), self)
        self._activation_code_shortcut.activated.connect(self.show_activation_code_dialog)
        self._activation_code_shortcut.setAutoRepeat(False)
        self._state_enabled = True
        self._form.splash.hide()
        self.init_hidden_elements()
        self.load_tab(UITab.SYSTEM)
        self.update_screens()

    
    def load_icons(self):
        flip_icons = (lambda .0: [ icon for icon in .0 if icon.property('icon-flip-h') is True ])(self._top_level_widget.findChildren(QWidget))
        for flip_icon in flip_icons:
            icon = flip_icon.icon() if hasattr(flip_icon, 'icon') else None
            if isinstance(icon, QIcon):
                size = icon.actualSize(flip_icon.size())
                pixmap = icon.pixmap(size)
                flipped = pixmap.transformed(QTransform().scale(-1, 1))
                flip_icon.setIcon(QIcon(flipped))
        gifs = [
            (self._system_check_screen.gears, 'check_gears.gif'),
            (self._cc_tab.cc_gears, 'cc_gears.gif'),
            (self._system_connect_screen.connect_arrows, 'arrows.gif'),
            (self._system_updating_screen.static_face, 'static_face.gif'),
            (self._cart_clinic._updating_screen.cc_static_face, 'static_face.gif')]
        for label, filename in gifs:
            movie = QMovie(f''':/images/images/{filename}''')
            label.setMovie(movie)
            movie.start()

    
    def load_fonts(self):
        QFontDatabase.addApplicationFont(':/fonts/fonts/Finger Five.ttf')
        QFontDatabase.addApplicationFont(':/fonts/fonts/Hachipochi EightAl Regular.ttf')
        text_labels = (lambda .0: [ lbl for lbl in .0 if lbl.objectName().startswith('text_') ])(self._top_level_widget.findChildren(QLabel))
        text_labels += [
            self._system_tab.current_fw,
            self._form.chromatic_manual_link]
        for label in text_labels:
            set_dynamic_font_size(label)
        transparent_labels = (lambda .0: [ label for label in .0 if label.objectName().startswith('text_trans_') ])(self._top_level_widget.findChildren(QLabel))
        for label in transparent_labels:
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    
    def init_event_listeners(self):
        self._form.dragger.installEventFilter(self)
        self._about_tab.text_changelog_app.installEventFilter(self)
        self._form.close_btn.clicked.connect(self.close)
        self._system_update_screen.update_btn.clicked.connect(self.both_submit)
        self._system_uptodate_screen.update_anyway_btn.clicked.connect(self.both_submit)
        self._system_internet_screen.retry_btn.clicked.connect(self.retry_download)
        self._system_error_screen.retry_btn.clicked.connect(self.retry_flash)
        self._form.chromatic_manual_link.clicked.connect(self.open_manual)
        self._system_tab.fw_changelog_btn.clicked.connect(self.open_fw_changelog)
        None((lambda : self.cycle_selected_firmware(-1)))
        None((lambda : self.cycle_selected_firmware(1)))
        None((lambda x = None: self.load_tab(UITab.SYSTEM)))
        None((lambda x = None: self.load_tab(UITab.CART_CLINIC)))
        None((lambda x = None: self.load_tab(UITab.ABOUT)))
        None((lambda x = None: self.load_tab(UITab.MANUFACTURING)))

    
    def init_hidden_elements(self):
        '''Toggle on/off miscellaneous elements on app init after splash screen.'''
        self._form.close_btn.show()
        self._form.chromatic_manual_link.show()
        self._form.dragger.show()

    
    def start_downloads(self = None):
        if plugins.is_plugin_enabled_for_user('manufacturing-tab'):
            return None
        self._manifest_thread = None(self.preview_firmware_accessible, self.rollback_firmware_accessible)
        self._manifest_thread.error_signal.connect(self.download_fw_error)
        self._manifest_thread.finished.connect(self.process_manifest_callback)
        self._manifest_thread.start()

    
    def download_firmware(self = None, chromatic_fw_options = None, cartclinic_fw_info = None, chromatic_fw_changelog_uri = ('chromatic_fw_options', list[S3FirmwareInfo], 'cartclinic_fw_info', S3FirmwareInfo, 'chromatic_fw_changelog_uri', str, 'return', None)):
        self._downloader_thread = DownloadFirmware(chromatic_fw_options, cartclinic_fw_info, chromatic_fw_changelog_uri)
        self._downloader_thread.error_signal.connect(self.download_fw_error)
        self._downloader_thread.firmware_changelog_signal.connect(self.download_fw_changelog_callback)
        self._downloader_thread.chromatic_fw_signal.connect(self.download_fw_callback)
        self._downloader_thread.cartclinic_fw_signal.connect(self._cart_clinic.download_cc_fw_callback)
        self._downloader_thread.start()

    
    def detect_firmware(self = None):
        if self._detect_thread is not None:
            return None
        if not None._chromatic.mcu_port:
            time.sleep(3)
        self._detect_thread = DetectVersionSubprocess(self._chromatic, **('chromatic',))
        self._detect_thread.finished.connect(self.detect_firmware_callback)
        self._detect_thread.start()

    
    def reset_flash(self = None):
        self._progress_modifier = (1, 0)
        self._flashing_start_time = time.monotonic()
        self.update_progress_bar(0)

    
    def closeEvent(self = None, event = None):
        '''This method defines what the app does when it closes expectedly. This includes exits through
        the keyboard (alt+F4), as well as the custom close button.
        '''
        plugins.on_quit_main_application()
        if not self._chromatic.current_state.id in self._chromatiWarning: Stack history is not empty!
Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
c.firmware_update_states and self.show_prompt('Warning', 'If you quit now, your Chromatic might stop working.\nAre you sure you want to exit?'):
            event.ignore()
            return None
        if not None._chromatic.current_state.id in self._chromatic.cart_clinic_updating_states and self.show_prompt('Warning', 'If you quit now, your cartridge might stop working.\nAre you sure you want to exit?'):
            event.ignore()
            return None
        if None._cart_clinic:
            self._cart_clinic.cleanup_cart_clinic(True, **('is_shutting_down',))
            if self._cart_clinic._cc_check_thread and self._cart_clinic._cc_check_thread._cc_timer_thread and self._cart_clinic._cc_check_thread._cc_timer_thread.isRunning():
                self._cart_clinic._cc_check_thread._cc_timer_thread.wait()
        event.accept()

    
    def quit_app(self):
        app.quit()

    
    def eventFilter(self = None, source = None, event = None):
        
        try:
            if source == self._form.dragger:
                if event.type() == QEvent.MouseButtonPress:
                    self.dragging = True
                    self.drag_position = event.globalPosition().toPoint() - self.window().pos()
                    self._form.dragger.setCursor(Qt.ClosedHandCursor)
                return True
            if None.type() == QEvent.MouseMove and self.dragging:
                self.move(event.globalPosition().toPoint() - self.drag_position)
        finally:
            return True
            if event.type() == QEvent.MouseButtonRelease:
                self.dragging = False
                self._form.dragger.setCursor(Qt.OpenHandCursor)
            return True
            if source == self._about_tab.text_changelog_app and event.type() == QEvent.MouseButtonPress:
                show_changelog_dialog()
            return True
            if event.type() == QEvent.MouseButtonPress:
                print(source)
            return super(GUI, self).eventFilter(source, event)
            e = None
            
            try:
                logger.error(f'''Error in eventFilter: {e}''')
            finally:
                e = None
                del e
                return False
                e = None
                del e



    
    def both_submit(self = None):
        self.reset_flash()
        if self._chromatic.current_state.id in self._chromatic.cart_clinic_updating_states:
            return self.show_error_message('Please finish Cart Clinic update first')
        selected_fw = None.selected_firmware
        if not selected_fw and selected_fw.fpga_fw_path or selected_fw.mcu_fw_path:
            logger.error(f'''Firmware paths missing for selected firmware: {selected_fw.version}''')
            return self.show_error_message('Something went wrong. Please restart the application.')
        if not None._selected_fw_index != 0 and self.show_prompt('Firmware Selection', f'''Selected firmware: {selected_fw.label}: {selected_fw.version}\nYou have selected a firmware version that is not the latest. Are you sure?'''):
            return None
        logger.info(f'''Flashing firmware version: {selected_fw.version}''')
        self._chromatic.flash_both_start(selected_fw.mcu_fw_path, selected_fw.fpga_fw_path)
        :
            self.reset_flash()
            if self._chromatic.current_state.id in self._chromatic.cart_clinic_updating_states:
                return self.show_error_message('Please finish Cart Clinic update first')
            selected_fw = None.selected_firmware
            if not selected_fw and selected_fw.fpga_fw_path or selected_fw.mcu_fw_path:
                logger.error(f'''Firmware paths missing for selected firmware: {selected_fw.version}''')
                return self.show_error_message('Something went wrong. Please restart the application.')
            if not None._selected_fw_index != 0 and self.show_prompt('Firmware Selection', f'''Selected firmware: {selected_fw.label}: {selected_fw.version}\nYou have selected a firmware version that is not the latest. Are you sure?'''):
         WARNING: Circular reference detected
       return None
            logger.info(f'''Flashing firmware version: {selected_fw.version}''')
            self._chromatic.flash_both_start(selected_fw.mcu_fw_path, selected_fw.fpga_fw_path)
            
            return None
            self.show_error_message('FPGA detection failed. Please reset and try again.')
            return None
            e = None
        return None
        self.show_error_message('FPGA detection failed. Please reset and try again.')
        return None
        e = None

    
    def on_chromatic_state_transition(self = None, event = None, state = None):
        '''Callback function to perform UI updates when the Chromatic
        has a state transition
        '''
        self.update_screens()
        if state.id in self._chromatic.ready_states:
            self._system_tab.current_fw.setText(f'''<html><head/><body><p>DEVICE IS RUNNING FIRMWARE: <span style=\'color:#ffffff;\'>{self._chromatic.fw_version}</span></p></body></html>''')
            if self._chromatic.fw_version is None:
                self.update_screens()
        if state.id == self._chromatic.detecting_firmware.id:
            self._chromatic.set_fw_version(None)
            self.detect_firmware()
        if state.id in self._chromatic.error_states:
            self._flash_failure = True
            self.update_screens()
            return None

    
    def download_fw_error(self, error):
        self._download_failure = True
        logger.error(f'''Firmware download failed: {error}''')
        self.update_screens()

    
    def download_fw_changelog_callback(self = None, changelog = None):
        self._fw_changelog = changelog
        self.update_screens()

    
    def download_fw_callback(self = None, fw_packages = None):
        self.process_firmware_files(fw_packages)
        self.update_screens()

    
    def process_manifest_callback(self = None, manifest_data = None):
        self.get_app_version_callback(manifest_data.version)
        self._cart_clinic.set_mrpatcher_endpoint(manifest_data.mrpatcher_endpoint)
        self.download_firmware(manifest_data.chromatic_fw_options, manifest_data.cartclinic_fw_info, manifest_data.chromatic_fw_changelog_uri)

    
    def get_app_version_callback(self, version):
        if f'''v{__version__}''' == version:
            self._about_tab.text_uptodate.setText(f'''{APP_NAME} is up to date!''')
            self._about_tab.text_uptodate.setStyleSheet('color: white;')
            return None
        if None == '':
            return None
        None._about_tab.text_uptodate.setText(f'''{APP_NAME} has an update available!''')
        self._about_tab.text_uptodate.setStyleSheet('color: orange;')
        self.end_splash()
        self.load_tab(UITab.ABOUT)
        self.show_error_message(f'''A new version of {APP_NAME} is available! Please see the About tab for a download link.''', 'Update Available', **('title',))

    
    def process_firmware_files(self = None, fw_packages = None):
        self._firmware_options = []
        for fw_package in fw_packages:
            if '' in (fw_package.zip_path, fw_package.fpga_fw_path, fw_package.mcu_fw_path, fw_package.temp_dir_path):
                self._download_failure = True
                logger.error('Firmware download failed')
                return None
            if not None.zip_path.endswith('.zip'):
                fw_package.zip_path = f'''{fw_package.zip_path}.zip'''
            fw_ver = Path(fw_package.zip_path).stem
            logger.info(f'''Firmware download successful: {fw_ver}''')
            fw_package.version = fw_ver
            self._firmware_options.append(fw_package)
        if len(self._firmware_options) == 0:
            self._download_failure = True
            logger.error('No firmware packages found')
            return None
        self._selected_fw_index = None
        latest_fw_package = self._firmware_options[self._selected_fw_index]
        self._tmp_dir_holder = latest_fw_package.temp_dir_path
        self._latest_fw_version = latest_fw_package.version

    
    def detect_firmware_callback(selfError decompyling /tmp/MRUpdater.exe_extracted/main.pyc: std::bad_cast
, v):
        logger.info(f'''Firmware detected: {v}''')
        self._detect_thread = None
        self._detect_failure = False
        if v == '':
            v = '--'
            self._detect_failure = True
        self._chromatic.set_fw_version(v)

    
    def open_manual(self):
        QDesktopServices.openUrl(QUrl(CHROMATIC_MANUAL_LINK))

    
    def open_fw_changelog(self):
        if self._fw_changelog or 'versions' not in self._fw_changelog:
            return self.show_error_message('Changelog could not be loaded. Please try re-launching MRUpdater.')
        changelog_text = None
        versions = sorted(self._fw_changelog['versions'], True, **('reverse',))
        for version in versions:
            changelog_text += f'''## v{version}\n'''
            changelog_text += self._fw_changelog['versions'][version]['changes']
            changelog_text += '\n\n'
        changelog_dialog = ChangelogDialog('Chromatic Firmware Changelog', str(changelog_text), **('title', 'text'))
        changelog_dialog.exec()

    
    def cycle_selected_firmware(self = None, increment = None):
        '''Cycle through the available firmware versions.'''
        if len(self._firmware_options) == 0:
            return None
        if None.fw_selection_enabled:
            self._selected_fw_index += increment
            if self._selected_fw_index < 0:
                self._selected_fw_index = len(self._firmware_options) - 1
            elif self._selected_fw_index >= len(self._firmware_options):
                self._selected_fw_index = 0
        self.set_selected_fw_text()

    
    def set_selected_fw_text(self = None):
        selected_fw = self.selected_firmware
        if not selected_fw:
            return None
        None._system_tab.text_selected_version.setText(f'''{selected_fw.label.upper()}: {selected_fw.version}''')

    
    def update_screens(self):
        if not self._state_enabled:
            return None
        hide_elements = (lambda 