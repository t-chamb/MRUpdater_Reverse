# Source Generated with Decompyle++
# File: cc_uptodate_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QCursor, QIcon, QPixmap
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy

class Ui_CCUpToDateScreen(object):
    
    def setupUi(self, CCUpToDateScreen):
        if not CCUpToDateScreen.objectName():
            CCUpToDateScreen.setObjectName('CCUpToDateScreen')
        CCUpToDateScreen.resize(625, 432)
        self.cartridge_label1 = QLabel(CCUpToDateScreen)
        self.cartridge_label1.setObjectName('cartridge_label1')
        self.cartridge_label1.setGeometry(QRect(255, 197, 92, 80))
        self.cartridge_label1.setScaledContents(True)
        self.bg = QLabel(CCUpToDateScreen)
        self.bg.setObjectName('bg')
        self.bg.setEnabled(True)
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/screen_cc_update.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cc_cart1 = QLabel(CCUpToDateScreen)
        self.cc_cart1.setObjectName('cc_cart1')
        self.cc_cart1.setEnabled(True)
        self.cc_cart1.setGeometry(QRect(240, 160, 122, 137))
        self.cc_cart1.setPixmap(QPixmap(':/images/images/cartridge.png'))
        self.cc_cart1.setScaledContents(True)
        self.cc_cart1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_1_16 = QLabel(CCUpToDateScreen)
        self.text_1_16.setObjectName('text_1_16')
        self.text_1_16.setGeometry(QRect(360, 175, 221, 28))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_1_16.sizePolicy().hasHeightForWidth())
        self.text_1_16.setSizePolicy(sizePolicy)
        self.text_1_16.setStyleSheet('color: rgb(50,255,0);')
        self.text_1_16.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_1_18 = QLabel(CCUpToDateScreen)
        self.text_1_18.setObjectName('text_1_18')
        self.text_1_18.setGeometry(QRect(360, 200, 221, 28))
        sizePolicy.setHeightForWidth(self.text_1_18.sizePolicy().hasHeightForWidth())
        self.text_1_18.setSizePolicy(sizePolicy)
        self.text_1_18.setStyleSheet('color: rgb(50,255,0);')
        self.text_1_18.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cc_ok_uptodate_btn = QPushButton(CCUpToDateScreen)
        self.cc_ok_uptodate_btn.setObjectName('cc_ok_uptodate_btn')
        self.cc_ok_uptodate_btn.setGeometry(QRect(415, 250, 112, 33))
        self.cc_ok_uptodate_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.cc_ok_uptodate_btn.setStyleSheet('')
        icon = QIcon()
        icon.addFile(':/images/images/ok_btn.png', QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.cc_ok_uptodate_btn.setIcon(icon)
        self.cc_ok_uptodate_btn.setIconSize(QSize(182, 50))
        self.retranslateUi(CCUpToDateScreen)
        QMetaObject.connectSlotsByName(CCUpToDateScreen)

    
    def retranslateUi(self, CCUpToDateScreen):
        CCUpToDateScreen.setWindowTitle(QCoreApplication.translate('CCUpToDateScreen', 'Form', None))
        self.cartridge_label1.setText('')
        self.bg.setText('')
        self.cc_cart1.setText('')
        self.text_1_16.setText(QCoreApplication.translate('CCUpToDateScreen', 'Your game is', None))
        self.text_1_16.setProperty('fontname', QCoreApplication.translate('CCUpToDateScreen', 'hachipochi', None))
        self.text_1_16.setProperty('textalign', QCoreApplication.translate('CCUpToDateScreen', 'center', None))
        self.text_1_18.setText(QCoreApplication.translate('CCUpToDateScreen', 'up to date!', None))
        self.text_1_18.setProperty('fontname', QCoreApplication.translate('CCUpToDateScreen', 'hachipochi', None))
        self.text_1_18.setProperty('textalign', QCoreApplication.translate('CCUpToDateScreen', 'center', None))
        self.cc_ok_uptodate_btn.setText('')


