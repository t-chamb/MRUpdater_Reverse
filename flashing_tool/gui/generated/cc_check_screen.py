# Source Generated with Decompyle++
# File: cc_check_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class Ui_CCCheckScreen(object):
    
    def setupUi(self, CCCheckScreen):
        if not CCCheckScreen.objectName():
            CCCheckScreen.setObjectName('CCCheckScreen')
        CCCheckScreen.resize(625, 432)
        self.text_2_16 = QLabel(CCCheckScreen)
        self.text_2_16.setObjectName('text_2_16')
        self.text_2_16.setGeometry(QRect(180, 320, 409, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_2_16.sizePolicy().hasHeightForWidth())
        self.text_2_16.setSizePolicy(sizePolicy)
        self.text_2_16.setStyleSheet('color: rgb(255, 0, 0);')
        self.text_2_16.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg = QLabel(CCCheckScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/check_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_checking = QLabel(CCCheckScreen)
        self.text_cc_checking.setObjectName('text_cc_checking')
        self.text_cc_checking.setGeometry(QRect(180, 138, 409, 20))
        sizePolicy.setHeightForWidth(self.text_cc_checking.sizePolicy().hasHeightForWidth())
        self.text_cc_checking.setSizePolicy(sizePolicy)
        self.text_cc_checking.setStyleSheet('color: rgb(153,153,153)')
        self.text_cc_checking.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(CCCheckScreen)
        QMetaObject.connectSlotsByName(CCCheckScreen)

    
    def retranslateUi(self, CCCheckScreen):
        CCCheckScreen.setWindowTitle(QCoreApplication.translate('CCCheckScreen', 'Form', None))
        self.text_2_16.setText(QCoreApplication.translate('CCCheckScreen', 'DO NOT REMOVE THE CARTRIDGE!', None))
        self.text_2_16.setProperty('fontname', QCoreApplication.translate('CCCheckScreen', 'finger-five', None))
        self.bg.setText('')
        self.text_cc_checking.setText(QCoreApplication.translate('CCCheckScreen', 'CHECKING YOUR GAME...', None))
        self.text_cc_checking.setProperty('fontname', QCoreApplication.translate('CCCheckScreen', 'finger-five', None))


