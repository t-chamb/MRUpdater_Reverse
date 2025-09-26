# Source Generated with Decompyle++
# File: cc_loading_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

class Ui_CCLoadingScreen(object):
    
    def setupUi(self, CCLoadingScreen):
        if not CCLoadingScreen.objectName():
            CCLoadingScreen.setObjectName('CCLoadingScreen')
        CCLoadingScreen.resize(625, 432)
        self.bg = QLabel(CCLoadingScreen)
        self.bg.setObjectName('bg')
        self.bg.setGeometry(QRect(0, 0, 625, 432))
        self.bg.setPixmap(QPixmap(':/images/images/check_screen.png'))
        self.bg.setScaledContents(True)
        self.bg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_cc_loading = QLabel(CCLoadingScreen)
        self.text_cc_loading.setObjectName('text_cc_loading')
        self.text_cc_loading.setGeometry(QRect(180, 138, 411, 20))
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text_cc_loading.sizePolicy().hasHeightForWidth())
        self.text_cc_loading.setSizePolicy(sizePolicy)
        self.text_cc_loading.setStyleSheet('color: rgb(153,153,153)')
        self.text_cc_loading.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.retranslateUi(CCLoadingScreen)
        QMetaObject.connectSlotsByName(CCLoadingScreen)

    
    def retranslateUi(self, CCLoadingScreen):
        CCLoadingScreen.setWindowTitle(QCoreApplication.translate('CCLoadingScreen', 'Form', None))
        self.bg.setText('')
        self.text_cc_loading.setText(QCoreApplication.translate('CCLoadingScreen', 'CHECKING CHROMATIC...', None))
        self.text_cc_loading.setProperty('fontname', QCoreApplication.translate('CCLoadingScreen', 'finger-five', None))


