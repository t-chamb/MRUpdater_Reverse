# Source Generated with Decompyle++
# File: about_screen.pyc (Python 3.10)

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, Qt
from PySide6.QtGui import QCursor, QPixmap
from PySide6.QtWidgets import QLabel, QWidget

class Ui_AboutScreen(object):
    
    def setupUi(self, AboutScreen):
        if not AboutScreen.objectName():
            AboutScreen.setObjectName('AboutScreen')
        AboutScreen.resize(625, 432)
        self.text_container = QWidget(AboutScreen)
        self.text_container.setObjectName('text_container')
        self.text_container.setGeometry(QRect(190, 120, 391, 241))
        self.text_title = QLabel(self.text_container)
        self.text_title.setObjectName('text_title')
        self.text_title.setGeometry(QRect(10, 10, 381, 21))
        self.text_manual = QLabel(self.text_container)
        self.text_manual.setObjectName('text_manual')
        self.text_manual.setGeometry(QRect(10, 160, 381, 21))
        self.text_manual.setTextFormat(Qt.TextFormat.RichText)
        self.text_manual.setOpenExternalLinks(True)
        self.text_download = QLabel(self.text_container)
        self.text_download.setObjectName('text_download')
        self.text_download.setGeometry(QRect(10, 70, 381, 21))
        self.text_download.setTextFormat(Qt.TextFormat.RichText)
        self.text_download.setOpenExternalLinks(True)
        self.text_changelog = QLabel(self.text_container)
        self.text_changelog.setObjectName('text_changelog')
        self.text_changelog.setGeometry(QRect(10, 130, 381, 21))
        self.text_changelog.setTextFormat(Qt.TextFormat.RichText)
        self.text_changelog.setOpenExternalLinks(True)
        self.text_uptodate = QLabel(self.text_container)
        self.text_uptodate.setObjectName('text_uptodate')
        self.text_uptodate.setGeometry(QRect(10, 40, 381, 21))
        self.text_uptodate.setTextFormat(Qt.TextFormat.PlainText)
        self.text_uptodate.setOpenExternalLinks(False)
        self.text_changelog_app = QLabel(self.text_container)
        self.text_changelog_app.setObjectName('text_changelog_app')
        self.text_changelog_app.setGeometry(QRect(10, 100, 381, 21))
        self.text_changelog_app.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.text_changelog_app.setTextFormat(Qt.TextFormat.RichText)
        self.text_changelog_app.setOpenExternalLinks(True)
        self.text_manual.raise_()
        self.text_download.raise_()
        self.text_changelog.raise_()
        self.text_uptodate.raise_()
        self.text_changelog_app.raise_()
        self.text_title.raise_()
        self.static_img_tab3 = QLabel(AboutScreen)
        self.static_img_tab3.setObjectName('static_img_tab3')
        self.static_img_tab3.setGeometry(QRect(0, 0, 625, 432))
        self.static_img_tab3.setPixmap(QPixmap(':/images/images/static_tab3.png'))
        self.static_img_tab3.raise_()
        self.text_container.raise_()
        self.retranslateUi(AboutScreen)
        QMetaObject.connectSlotsByName(AboutScreen)

    
    def retranslateUi(self, AboutScreen):
        AboutScreen.setWindowTitle(QCoreApplication.translate('AboutScreen', 'Form', None))
        self.text_title.setText(QCoreApplication.translate('AboutScreen', 'MRUpdater', None))
        self.text_title.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.text_manual.setText(QCoreApplication.translate('AboutScreen', '<html><head/><body><p><a href="https://modretro.com/pages/chromatic-manual"><span style=" text-decoration: underline; color:#12f412;">Chromatic Manual</span></a><span style=" color:#89bf48;"/></p></body></html>', None))
        self.text_manual.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.text_download.setText(QCoreApplication.translate('AboutScreen', '<html><head/><body><p><a href="https://modretro.com/pages/downloads/#mrupdater"><span style=" text-decoration: underline; color:#12f412;">Download latest MRUpdater</span></a><span style=" color:#89bf48;"/></p></body></html>', None))
        self.text_download.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.text_changelog.setText(QCoreApplication.translate('AboutScreen', '<html><head/><body><p><span style=" color:#ffffff;">Firmware Changelogs: </span><a href="https://github.com/ModRetro/chromatic_fpga/blob/main/CHANGELOG.md"><span style=" text-decoration: underline; color:#12f412;">FPGA</span></a><span style=" color:#ffffff;">, </span><a href="https://github.com/ModRetro/chromatic_mcu/blob/main/CHANGELOG.md"><span style=" text-decoration: underline; color:#12f412;">MCU</span></a></p></body></html>', None))
        self.text_changelog.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.text_uptodate.setText(QCoreApplication.translate('AboutScreen', 'MRUpdater is up to date!', None))
        self.text_uptodate.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.text_changelog_app.setText(QCoreApplication.translate('AboutScreen', '<html><head/><body><p><span style=" text-decoration: underline; color:#12f412;">MRUpdater Changelog</span></p></body></html>', None))
        self.text_changelog_app.setProperty('fontname', QCoreApplication.translate('AboutScreen', 'hachipochi', None))
        self.static_img_tab3.setText('')


