# Source Generated with Decompyle++
# File: error_dialog.pyc (Python 3.10)

import sys
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon

class ErrorDialog(QDialog):
    
    def __init__(self = None, title = None, message = None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(':/images/images/icon.ico'))
        self.setModal(True)
        self.setFixedSize(450, 250)
        layout = QVBoxLayout()
        title = QLabel(message)
        title.setWordWrap(True)
        layout.addWidget(title)
        self.accept_button = QPushButton('OK')
        self.accept_button.clicked.connect(self.accept)
        layout.addWidget(self.accept_button)
        self.setLayout(layout)

    
    def accept(self = None):
        '''Handle user accepting. Attempt to move the app to Applications and relaunch'''
        super().accept()
        sys.exit()

    __classcell__ = None

