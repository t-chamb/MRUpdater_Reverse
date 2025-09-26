# Source Generated with Decompyle++
# File: cc_connect_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

class Ui_CCConnectScreen(object):
    
    def setupUi(self, CCConnectScreen):
        if not CCConnectScreen.objectName():
            CCConnectScreen.setObjectName('CCConnectScreen')
        CCConnectScreen.resize(625, 432)
        self.bg = QLabel(CCConnectScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/connect_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayoutWidget_11 = QWidget(CCConnectScreen)
        self.horizontalLayoutWidget_11.setObjectName('horizontalLayoutWidget_11')
        self.horizontalLayoutWidget_11.setGeometry(QRect(180, 150, 411, 21))
        self.connect_label_3 = QHBoxLayout(self.horizontalLayoutWidget_11)
        self.connect_label_3.setObjectName('connect_label_3')
        self.connect_label_3.setContentsMargins(0, 0, 0, 0)
        self.text_2_7 = QLabel(self.horizontalLayoutWidget_11)
        self.text_2_7.setObjectName('text_2_7')
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_2_7.sizePolicy().hasHeightForWidth())
        self.text_2_7.setSizePolicy(sizePolicy)
        self.text_2_7.setStyleSheet('color: rgb(153,153,153)')
        self.text_2_7.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connect_label_3.addWidget(self.text_2_7)
        self.connect_arrows_2 = QLabel(CCConnectScreen)
        self.connect_arrows_2.setObjectName('connect_arrows_2')
        self.connect_arrows_2.setGeometry(QRect(0, 0, 625, 432))
        self.connect_arrows_2.setScaledContents(True)
        self.connect_arrows_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayoutWidget_12 = QWidget(CCConnectScreen)
        self.horizontalLayoutWidget_12.setObjectName('horizontalLayoutWidget_12')
        self.horizontalLayoutWidget_12.setGeometry(QRect(180, 310, 411, 21))
        self.connect_label_4 = QHBoxLayout(self.horizontalLayoutWidget_12)
        self.connect_label_4.setObjectName('connect_label_4')
        self.connect_label_4.setContentsMargins(0, 0, 0, 0)
        self.text_2_8 = QLabel(self.horizontalLayoutWidget_12)
        self.text_2_8.setObjectName('text_2_8')
        sizePolicy.setHeightForWidth(self.text_2_8.sizePolicy().hasHeightForWidth())
        self.text_2_8.setSizePolicy(sizePolicy)
        self.text_2_8.setStyleSheet('color: rgb(153,153,153)')
        self.text_2_8.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.connect_label_4.addWidget(self.text_2_8)
        self.retranslateUi(CCConnectScreen)
        QMetaObject.connectSlotsByName(CCConnectScreen)

    
    def retranslateUi(self, CCConnectScreen):
        CCConnectScreen.setWindowTitle(QCoreApplication.translate('CCConnectScreen', 'Form', None))
        self.bg.setText('')
        self.text_2_7.setText(QCoreApplication.translate('CCConnectScreen', 'PLEASE SWITCH ON YOUR CHROMATIC', None))
        self.text_2_7.setProperty('fontname', QCoreApplication.translate('CCConnectScreen', 'finger-five', None))
        self.connect_arrows_2.setText('')
        self.text_2_8.setText(QCoreApplication.translate('CCConnectScreen', 'AND CONNECT IT VIA USB', None))
        self.text_2_8.setProperty('fontname', QCoreApplication.translate('CCConnectScreen', 'finger-five', None))


