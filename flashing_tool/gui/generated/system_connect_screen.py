# Source Generated with Decompyle++
# File: system_connect_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class Ui_SystemConnectScreen(object):
    
    def setupUi(self, SystemConnectScreen):
        if not SystemConnectScreen.objectName():
            SystemConnectScreen.setObjectName('SystemConnectScreen')
        SystemConnectScreen.resize(625, 432)
        self.text_2_4 = QLabel(SystemConnectScreen)
        self.text_2_4.setObjectName('text_2_4')
        self.text_2_4.setGeometry(QRect(180, 150, 409, 19))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_2_4.sizePolicy().hasHeightForWidth())
        self.text_2_4.setSizePolicy(sizePolicy)
        self.text_2_4.setStyleSheet('color: rgb(153,153,153)')
        self.text_2_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_2_6 = QLabel(SystemConnectScreen)
        self.text_2_6.setObjectName('text_2_6')
        self.text_2_6.setGeometry(QRect(180, 310, 409, 19))
        sizePolicy.setHeightForWidth(self.text_2_6.sizePolicy().hasHeightForWidth())
        self.text_2_6.setSizePolicy(sizePolicy)
        self.text_2_6.setStyleSheet('color: rgb(153,153,153)')
        self.text_2_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connect_arrows = QLabel(SystemConnectScreen)
        self.connect_arrows.setObjectName('connect_arrows')
        self.connect_arrows.setGeometry(QRect(0, 0, 625, 432))
        self.connect_arrows.setScaledContents(True)
        self.connect_arrows.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg = QLabel(SystemConnectScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/connect_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(SystemConnectScreen)
        QMetaObject.connectSlotsByName(SystemConnectScreen)

    
    def retranslateUi(self, SystemConnectScreen):
        SystemConnectScreen.setWindowTitle(QCoreApplication.translate('SystemConnectScreen', 'Form', None))
        self.text_2_4.setText(QCoreApplication.translate('SystemConnectScreen', 'PLEASE SWITCH ON YOUR CHROMATIC', None))
        self.text_2_4.setProperty('fontname', QCoreApplication.translate('SystemConnectScreen', 'finger-five', None))
        self.text_2_6.setText(QCoreApplication.translate('SystemConnectScreen', 'AND CONNECT IT VIA USB', None))
        self.text_2_6.setProperty('fontname', QCoreApplication.translate('SystemConnectScreen', 'finger-five', None))
        self.connect_arrows.setText('')
        self.bg.setText('')


