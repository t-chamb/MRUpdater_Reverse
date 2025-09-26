# Source Generated with Decompyle++
# File: system_check_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class Ui_SystemCheckScreen(object):
    
    def setupUi(self, SystemCheckScreen):
        if not SystemCheckScreen.objectName():
            SystemCheckScreen.setObjectName('SystemCheckScreen')
        SystemCheckScreen.resize(625, 432)
        self.bg = QLabel(SystemCheckScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/check_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gears = QLabel(SystemCheckScreen)
        self.gears.setObjectName('gears')
        self.gears.setGeometry(QRect(0, 0, 625, 432))
        self.gears.setPixmap(QPixmap(':/images/images/check_gear1.png'))
        self.gears.setScaledContents(True)
        self.gears.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_2_5 = QLabel(SystemCheckScreen)
        self.text_2_5.setObjectName('text_2_5')
        self.text_2_5.setGeometry(QRect(180, 150, 409, 19))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_2_5.sizePolicy().hasHeightForWidth())
        self.text_2_5.setSizePolicy(sizePolicy)
        self.text_2_5.setStyleSheet('color: rgb(153,153,153)')
        self.text_2_5.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(SystemCheckScreen)
        QMetaObject.connectSlotsByName(SystemCheckScreen)

    
    def retranslateUi(self, SystemCheckScreen):
        SystemCheckScreen.setWindowTitle(QCoreApplication.translate('SystemCheckScreen', 'Form', None))
        self.bg.setText('')
        self.gears.setText('')
        self.text_2_5.setText(QCoreApplication.translate('SystemCheckScreen', 'CHECKING FIRMWARE...', None))
        self.text_2_5.setProperty('fontname', QCoreApplication.translate('SystemCheckScreen', 'finger-five', None))


