# Source Generated with Decompyle++
# File: changelog_dialog.pyc (Python 3.10)

import os
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget, QSizePolicy
from PySide6.QtGui import QIcon
from PySide6.QtCore import Qt
from flashing_tool.util import resolve_path
CHANGELOG_FILE = resolve_path('resources/CHANGELOG.txt')

class ChangelogDialog(QDialog):
    
    def __init__(self = None, title = None, text = None):
        super().__init__()
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(':/images/images/icon.ico'))
        self.setModal(True)
        self.setFixedSize(600, 400)
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        if text is None:
            changelog_text = QLabel(self.load_changelog_text())
        else:
            changelog_text = QLabel(text)
        changelog_text.setTextFormat(Qt.MarkdownText)
        changelog_text.setWordWrap(True)
        scroll_layout.addWidget(changelog_text, Qt.AlignTop, **('alignment',))
        scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        self.accept_button = QPushButton('OK')
        self.accept_button.clicked.connect(self.accept)
        self.accept_button.setStyleSheet('\n            QPushButton {\n                border: 2px solid #666;  /* outline color */\n                border-radius: 4px;\n                background-color: transparent;\n                padding: 6px 12px;\n            }\n            QPushButton:hover {\n                border-color: #0078d7;  /* light hover background */\n            }\n        ')
        layout.addWidget(self.accept_button)
        self.setLayout(layout)

    
    def load_changelog_text(self):
        '''Load the changelog text from a file.'''
        pass
        # TODO: Implementation needed
        raise NotImplementedError("Method not implemented")
    def accept(self = None):
        '''Handle closing the changelog dialog.'''
        super().accept()

    __classcell__ = None

