# Source Generated with Decompyle++
# File: system_internet_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton

class Ui_SystemInternetScreen(object):
    
    def setupUi(self, SystemInternetScreen):
        if not SystemInternetScreen.objectName():
            SystemInternetScreen.setObjectName('SystemInternetScreen')
        SystemInternetScreen.resize(625, 432)
        self.retry_btn = QPushButton(SystemInternetScreen)
        self.retry_btn.setObjectName('retry_btn')
        self.retry_btn.setGeometry(QRect(325, 310, 112, 33))
        self.retry_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.retry_btn.setStyleSheet('')
        icon = QIcon()
        icon.addFile(':/images/images/retry_btn.png', QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.retry_btn.setIcon(icon)
        self.retry_btn.setIconSize(QSize(182, 50))
        self.bg = QLabel(SystemInternetScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_internet.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(SystemInternetScreen)
        QMetaObject.connectSlotsByName(SystemInternetScreen)

    
    def retranslateUi(self, SystemInternetScreen):
        SystemInternetScreen.setWindowTitle(QCoreApplication.translate('SystemInternetScreen', 'Form', None))
        self.retry_btn.setText('')
        self.bg.setText('')


