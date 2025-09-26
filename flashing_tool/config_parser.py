Warning: block stack is not empty!
Warning: Stack history is not empty!
Warning: block stack is not empty!
# Source Generated with Decompyle++
# File: config_parser.pyc (Python 3.10)

import os
import configparser
from flashing_tool.constants import APP_DATA_DIR
from flashing_tool.gui.consent_dialog import ConsentDialog
CONFIG_FILE_NAME = 'config.ini'

class ConfigParser:
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(APP_DATA_DIR, CONFIG_FILE_NAME)
        
        try:
            os.makedirs(APP_DATA_DIR)
        finally:
            pass
        self.config.read(self.config_path, 'utf-8', **('encoding',))
        return None


    
    def load(self):
        return {
            'fpga_fw_file_path': self.get('fpga_fw_file_path'),
            'mcu_fw_file_path': self.get('mcu_fw_file_path'),
            'cart_fw_file_path': self.get('cart_fw_file_path') }

    
    def get(self, option):
        
        try:
            value = self.config.get('DEFAULT', option)
        finally:
            return value
            value = ''
            return value


    
    def set(self, option, value):
        self.config.set('DEFAULT', option, value)
        self.config.write(open(self.config_path, 'w', 'utf-8', **('encoding',)))

    
    def get_eula_consent_key(self):
        return f'''eula_consented_{ConsentDialog.get_eula_sha()}'''


