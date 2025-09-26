# Source Generated with Decompyle++
# File: cc_error_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton

class Ui_CCErrorScreen(object):
    
    def setupUi(self, CCErrorScreen):
        if not CCErrorScreen.objectName():
            CCErrorScreen.setObjectName('CCErrorScreen')
        CCErrorScreen.resize(625, 432)
        self.cc_retry_btn = QPushButton(CCErrorScreen)
        self.cc_retry_btn.setObjectName('cc_retry_btn')
        self.cc_retry_btn.setGeometry(QRect(330, 245, 112, 33))
        self.cc_retry_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cc_retry_btn.setStyleSheet('')
        icon = QIcon()
        icon.addFile(':/images/images/retry_btn.png', QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cc_retry_btn.setIcon(icon)
        self.cc_retry_btn.setIconSize(QSize(182, 50))
        self.bg = QLabel(CCErrorScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_error.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_error_2 = QLabel(CCErrorScreen)
        self.text_cc_error_2.setObjectName('text_cc_error_2')
        self.text_cc_error_2.setGeometry(QRect(180, 220, 411, 19))
        self.text_cc_error_2.setStyleSheet('color: rgb(153,153,153)')
        self.text_cc_error_2.setTextFormat(Qt.TextFormat.PlainText)
        self.text_cc_error_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_error_2.setOpenExternalLinks(True)
        self.text_cc_error = QLabel(CCErrorScreen)
        self.text_cc_error.setObjectName('text_cc_error')
        self.text_cc_error.setGeometry(QRect(180, 200, 411, 19))
        self.text_cc_error.setStyleSheet('color: rgb(153,153,153)')
        self.text_cc_error.setTextFormat(Qt.TextFormat.PlainText)
        self.text_cc_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_error.setOpenExternalLinks(True)
        self.text_3_8 = QLabel(CCErrorScreen)
        self.text_3_8.setObjectName('text_3_8')
        self.text_3_8.setGeometry(QRect(180, 165, 411, 31))
        self.text_3_8.setStyleSheet('color: rgb(255, 0, 0);')
        self.text_3_8.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_8.setOpenExternalLinks(True)
        self.bg.raise_()
        self.cc_retry_btn.raise_()
        self.text_cc_error_2.raise_()
        self.text_cc_error.raise_()
        self.text_3_8.raise_()
        self.retranslateUi(CCErrorScreen)
        QMetaObject.connectSlotsByName(CCErrorScreen)

    
    def retranslateUi(self, CCErrorScreen):
        CCErrorScreen.setWindowTitle(QCoreApplication.translate('CCErrorScreen', 'Form', None))
        self.cc_retry_btn.setText('')
        self.bg.setText('')
        self.text_cc_error_2.setText('')
        self.text_cc_error_2.setProperty('fontname', QCoreApplication.translate('CCErrorScreen', 'finger-five', None))
        self.text_cc_error.setText(QCoreApplication.translate('CCErrorScreen', 'SOMETHING WENT WRONG', None))
        self.text_cc_error.setProperty('fontname', QCoreApplication.translate('CCErrorScreen', 'finger-five', None))
        self.text_3_8.setText(QCoreApplication.translate('CCErrorScreen', 'Oops!', None))
        self.text_3_8.setProperty('fontname', QCoreApplication.translate('CCErrorScreen', 'hachipochi', None))


