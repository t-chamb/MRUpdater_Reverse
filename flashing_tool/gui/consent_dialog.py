# Source Generated with Decompyle++
# File: consent_dialog.pyc (Python 3.10)

import hashlib
import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QMessageBox, QWidget
from PySide6.QtGui import QIcon
from flashing_tool.util import resolve_path
AGREEMENT_FILE = resolve_path('resources/EULA.txt')

class ConsentDialog(QDialog):
    
    def __init__(self = None):
        super().__init__()
        self.setWindowTitle('End User License Agreement')
        self.setWindowIcon(QIcon(':/images/images/icon.ico'))
        self.setModal(True)
        layout = QVBoxLayout()
        title = QLabel('Please read and accept the following agreement to use this application. It may have changed since your last agreement.')
        title.setWordWrap(True)
        layout.addWidget(title)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        agreement_text = QLabel(self.load_agreement_text())
        agreement_text.setWordWrap(True)
        scroll_layout.addWidget(agreement_text)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        footer = QLabel('If this is your first time running the application, a third-party driver may be installed.')
        footer.setWordWrap(True)
        layout.addWidget(footer)
        self.accept_button = QPushButton('Accept')
        self.decline_button = QPushButton('Decline')
        self.accept_button.clicked.connect(self.accept)
        self.decline_button.clicked.connect(self.decline)
        layout.addWidget(self.accept_button)
        layout.addWidget(self.decline_button)
        self.setLayout(layout)

    
    def load_agreement_text(self):
        '''Load the agreement text from a file.'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def decline(self):
        '''Handle user declining the agreement.'''
        QMessageBox.warning(self, 'Declined', 'You must accept the agreement to use the application.')
        self.reject()

    
    def accept(self = None):
        '''Handle user accepting the agreement.'''
        super().accept()

    
    def get_eula_sha():
        sha256 = hashlib.sha256()
        with None(None, None, None):
            f = open(AGREEMENT_FILE, 'rb')
            for chunk in None((lambda : f.read(4096)), b''):
                sha256.update(chunk)
        # Incomplete decompilation - manual review needed
        pass
    get_eula_sha = staticmethod(get_eula_sha)
    __classcell__ = None

