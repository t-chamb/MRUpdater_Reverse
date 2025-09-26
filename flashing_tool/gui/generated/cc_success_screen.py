# Source Generated with Decompyle++
# File: cc_success_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton

class Ui_CCSuccessScreen(object):
    
    def setupUi(self, CCSuccessScreen):
        if not CCSuccessScreen.objectName():
            CCSuccessScreen.setObjectName('CCSuccessScreen')
        CCSuccessScreen.resize(625, 432)
        self.text_3_11 = QLabel(CCSuccessScreen)
        self.text_3_11.setObjectName('text_3_11')
        self.text_3_11.setGeometry(QRect(180, 140, 411, 28))
        self.text_3_11.setStyleSheet('color: rgb(50,255,0);')
        self.text_3_11.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_11.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_11.setOpenExternalLinks(True)
        self.ok_icon = QLabel(CCSuccessScreen)
        self.ok_icon.setObjectName('ok_icon')
        self.ok_icon.setGeometry(QRect(360, 218, 62, 52))
        self.ok_icon.setTextFormat(Qt.TextFormat.PlainText)
        self.ok_icon.setPixmap(QPixmap(':/images/images/ok_icon.png'))
        self.ok_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.ok_icon.setOpenExternalLinks(True)
        self.cc_ok_done_btn = QPushButton(CCSuccessScreen)
        self.cc_ok_done_btn.setObjectName('cc_ok_done_btn')
        self.cc_ok_done_btn.setGeometry(QRect(330, 300, 112, 33))
        self.cc_ok_done_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cc_ok_done_btn.setStyleSheet('')
        icon = QIcon()
        icon.addFile(':/images/images/ok_btn.png', QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cc_ok_done_btn.setIcon(icon)
        self.cc_ok_done_btn.setIconSize(QSize(182, 50))
        self.text_3_13 = QLabel(CCSuccessScreen)
        self.text_3_13.setObjectName('text_3_13')
        self.text_3_13.setGeometry(QRect(180, 165, 411, 28))
        self.text_3_13.setStyleSheet('color: rgb(50,255,0);')
        self.text_3_13.setTextFormat(Qt.TextFormat.PlainText)
        self.text_3_13.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_3_13.setOpenExternalLinks(True)
        self.bg = QLabel(CCSuccessScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_cc_success.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg.raise_()
        self.text_3_11.raise_()
        self.ok_icon.raise_()
        self.cc_ok_done_btn.raise_()
        self.text_3_13.raise_()
        self.retranslateUi(CCSuccessScreen)
        QMetaObject.connectSlotsByName(CCSuccessScreen)

    
    def retranslateUi(self, CCSuccessScreen):
        CCSuccessScreen.setWindowTitle(QCoreApplication.translate('CCSuccessScreen', 'Form', None))
        self.text_3_11.setText(QCoreApplication.translate('CCSuccessScreen', 'The game was', None))
        self.text_3_11.setProperty('fontname', QCoreApplication.translate('CCSuccessScreen', 'hachipochi', None))
        self.ok_icon.setText('')
        self.ok_icon.setProperty('fontname', QCoreApplication.translate('CCSuccessScreen', 'finger-five', None))
        self.cc_ok_done_btn.setText('')
        self.text_3_13.setText(QCoreApplication.translate('CCSuccessScreen', 'successfully updated!', None))
        self.text_3_13.setProperty('fontname', QCoreApplication.translate('CCSuccessScreen', 'hachipochi', None))
        self.bg.setText('')


