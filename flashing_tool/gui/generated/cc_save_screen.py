# Source Generated with Decompyle++
# File: cc_save_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class Ui_CCSaveScreen(object):
    
    def setupUi(self, CCSaveScreen):
        if not CCSaveScreen.objectName():
            CCSaveScreen.setObjectName('CCSaveScreen')
        CCSaveScreen.resize(625, 432)
        self.text_2_20 = QLabel(CCSaveScreen)
        self.text_2_20.setObjectName('text_2_20')
        self.text_2_20.setGeometry(QRect(180, 320, 409, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_2_20.sizePolicy().hasHeightForWidth())
        self.text_2_20.setSizePolicy(sizePolicy)
        self.text_2_20.setStyleSheet('color: rgb(255, 0, 0);')
        self.text_2_20.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bg = QLabel(CCSaveScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/check_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_save_label = QLabel(CCSaveScreen)
        self.text_cc_save_label.setObjectName('text_cc_save_label')
        self.text_cc_save_label.setGeometry(QRect(180, 138, 409, 20))
        sizePolicy.setHeightForWidth(self.text_cc_save_label.sizePolicy().hasHeightForWidth())
        self.text_cc_save_label.setSizePolicy(sizePolicy)
        self.text_cc_save_label.setStyleSheet('color: rgb(153,153,153)')
        self.text_cc_save_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(CCSaveScreen)
        QMetaObject.connectSlotsByName(CCSaveScreen)

    
    def retranslateUi(self, CCSaveScreen):
        CCSaveScreen.setWindowTitle(QCoreApplication.translate('CCSaveScreen', 'Form', None))
        self.text_2_20.setText(QCoreApplication.translate('CCSaveScreen', 'DO NOT REMOVE THE CARTRIDGE!', None))
        self.text_2_20.setProperty('fontname', QCoreApplication.translate('CCSaveScreen', 'finger-five', None))
        self.bg.setText('')
        self.text_cc_save_label.setText(QCoreApplication.translate('CCSaveScreen', 'CHECKING YOUR GAME...', None))
        self.text_cc_save_label.setProperty('fontname', QCoreApplication.translate('CCSaveScreen', 'finger-five', None))


