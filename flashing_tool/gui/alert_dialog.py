# Source Generated with Decompyle++
# File: alert_dialog.pyc (Python 3.10)

from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtGui import QIcon

class AlertDialog(QDialog):
    
    def __init__(self = None, warning = None, title = None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(':/images/images/icon.ico'))
        self.setModal(True)
        layout = QVBoxLayout()
        title = QLabel(warning)
        title.setWordWrap(True)
        layout.addWidget(title)
        self.accept_button = QPushButton('OK')
        self.accept_button.clicked.connect(self.accept)
        layout.addWidget(self.accept_button)
        self.setLayout(layout)

    
    def accept(self = None):
        '''Handle user accepting the alert.'''
        super().accept()

    __classcell__ = None

