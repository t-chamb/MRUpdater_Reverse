# Source Generated with Decompyle++
# File: system_error_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton

class Ui_SystemErrorScreen(object):
    
    def setupUi(self, SystemErrorScreen):
        if not SystemErrorScreen.objectName():
            SystemErrorScreen.setObjectName('SystemErrorScreen')
        SystemErrorScreen.resize(625, 432)
        self.text_3_3 = QLabel(SystemErrorScreen)
        self.text_3_3.setObjectName('text_3_3')
        self.text_3_3.setGeometry(QRect(180, 220, 411, 22))
        self.text_3_3.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_3.setOpenExternalLinks(True)
        self.retry_btn = QPushButton(SystemErrorScreen)
        self.retry_btn.setObjectName('retry_btn')
        self.retry_btn.setGeometry(QRect(325, 290, 112, 33))
        self.retry_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.retry_btn.setStyleSheet('')
        icon = QIcon()
        icon.addFile(':/images/images/retry_btn.png', QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.retry_btn.setIcon(icon)
        self.retry_btn.setIconSize(QSize(182, 50))
        self.bg = QLabel(SystemErrorScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_error.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_1 = QLabel(SystemErrorScreen)
        self.text_3_1.setObjectName('text_3_1')
        self.text_3_1.setGeometry(QRect(180, 145, 411, 25))
        self.text_3_1.setStyleSheet('color: rgb(255, 0, 0);')
        self.text_3_1.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_1.setOpenExternalLinks(True)
        self.text_contact_us = QLabel(SystemErrorScreen)
        self.text_contact_us.setObjectName('text_contact_us')
        self.text_contact_us.setGeometry(QRect(180, 245, 411, 22))
        self.text_contact_us.setTextFormat(Qt.TextFormat.RichText)
        self.text_contact_us.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_contact_us.setOpenExternalLinks(True)
        self.text_3_2 = QLabel(SystemErrorScreen)
        self.text_3_2.setObjectName('text_3_2')
        self.text_3_2.setGeometry(QRect(180, 195, 411, 22))
        self.text_3_2.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_2.setOpenExternalLinks(True)
        self.bg.raise_()
        self.text_3_3.raise_()
        self.retry_btn.raise_()
        self.text_3_1.raise_()
        self.text_contact_us.raise_()
        self.text_3_2.raise_()
        self.retranslateUi(SystemErrorScreen)
        QMetaObject.connectSlotsByName(SystemErrorScreen)

    
    def retranslateUi(self, SystemErrorScreen):
        SystemErrorScreen.setWindowTitle(QCoreApplication.translate('SystemErrorScreen', 'Form', None))
        self.text_3_3.setText(QCoreApplication.translate('SystemErrorScreen', 'AND TRY AGAIN. IF THE ISSUE PERSISTS,', None))
        self.text_3_3.setProperty('fontname', QCoreApplication.translate('SystemErrorScreen', 'finger-five', None))
        self.retry_btn.setText('')
        self.bg.setText('')
        self.text_3_1.setText(QCoreApplication.translate('SystemErrorScreen', 'THE UPDATE WAS NOT SUCCESSFUL', None))
        self.text_3_1.setProperty('fontname', QCoreApplication.translate('SystemErrorScreen', 'finger-five', None))
        self.text_contact_us.setText(QCoreApplication.translate('SystemErrorScreen', '<html><head/><body><p>PLEASE CONTACT US <a href="https://modretro.com/pages/contact"><span style=" text-decoration: underline; color:#12f412;">HERE</span></a>.</p></body></html>', None))
        self.text_contact_us.setProperty('fontname', QCoreApplication.translate('SystemErrorScreen', 'finger-five', None))
        self.text_3_2.setText(QCoreApplication.translate('SystemErrorScreen', 'PLEASE CHECK YOUR USB CONNECTION', None))
        self.text_3_2.setProperty('fontname', QCoreApplication.translate('SystemErrorScreen', 'finger-five', None))


