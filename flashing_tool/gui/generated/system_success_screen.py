# Source Generated with Decompyle++
# File: system_success_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import QLabel

class Ui_SystemSuccessScreen(object):
    
    def setupUi(self, SystemSuccessScreen):
        if not SystemSuccessScreen.objectName():
            SystemSuccessScreen.setObjectName('SystemSuccessScreen')
        SystemSuccessScreen.resize(625, 432)
        self.text_3_5 = QLabel(SystemSuccessScreen)
        self.text_3_5.setObjectName('text_3_5')
        self.text_3_5.setGeometry(QRect(180, 195, 411, 22))
        self.text_3_5.setStyleSheet('color:rgb(153,153,153);')
        self.text_3_5.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_5.setOpenExternalLinks(True)
        self.text_3_4 = QLabel(SystemSuccessScreen)
        self.text_3_4.setObjectName('text_3_4')
        self.text_3_4.setGeometry(QRect(180, 145, 411, 31))
        font = QFont()
        font.setPointSize(16)
        self.text_3_4.setFont(font)
        self.text_3_4.setStyleSheet('color: rgb(50, 255, 0);')
        self.text_3_4.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_4.setOpenExternalLinks(True)
        self.text_3_7 = QLabel(SystemSuccessScreen)
        self.text_3_7.setObjectName('text_3_7')
        self.text_3_7.setGeometry(QRect(180, 245, 411, 22))
        self.text_3_7.setStyleSheet('color:rgb(153,153,153);')
        self.text_3_7.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_7.setOpenExternalLinks(True)
        self.text_3_9 = QLabel(SystemSuccessScreen)
        self.text_3_9.setObjectName('text_3_9')
        self.text_3_9.setGeometry(QRect(180, 300, 411, 22))
        self.text_3_9.setStyleSheet('color: rgb(50, 255, 0);')
        self.text_3_9.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_9.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_9.setOpenExternalLinks(True)
        self.text_3_6 = QLabel(SystemSuccessScreen)
        self.text_3_6.setObjectName('text_3_6')
        self.text_3_6.setGeometry(QRect(180, 220, 411, 22))
        self.text_3_6.setStyleSheet('color:rgb(153,153,153);')
        self.text_3_6.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_6.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_6.setOpenExternalLinks(True)
        self.bg = QLabel(SystemSuccessScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_update.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(SystemSuccessScreen)
        QMetaObject.connectSlotsByName(SystemSuccessScreen)

    
    def retranslateUi(self, SystemSuccessScreen):
        SystemSuccessScreen.setWindowTitle(QCoreApplication.translate('SystemSuccessScreen', 'Form', None))
        self.text_3_5.setText(QCoreApplication.translate('SystemSuccessScreen', 'DISCONNECT THE USB CABLE FROM', None))
        self.text_3_5.setProperty('fontname', QCoreApplication.translate('SystemSuccessScreen', 'finger-five', None))
        self.text_3_4.setText(QCoreApplication.translate('SystemSuccessScreen', 'One last thing...', None))
        self.text_3_4.setProperty('fontname', QCoreApplication.translate('SystemSuccessScreen', 'hachipochi', None))
        self.text_3_7.setText(QCoreApplication.translate('SystemSuccessScreen', 'WAIT A FEW SECONDS...', None))
        self.text_3_7.setProperty('fontname', QCoreApplication.translate('SystemSuccessScreen', 'finger-five', None))
        self.text_3_9.setText(QCoreApplication.translate('SystemSuccessScreen', 'AFTERWARDS, GAME ON!', None))
        self.text_3_9.setProperty('fontname', QCoreApplication.translate('SystemSuccessScreen', 'finger-five', None))
        self.text_3_6.setText(QCoreApplication.translate('SystemSuccessScreen', 'YOUR CHROMATIC, POP OUT THE BATTERIES,', None))
        self.text_3_6.setProperty('fontname', QCoreApplication.translate('SystemSuccessScreen', 'finger-five', None))
        self.bg.setText('')


