import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPixmap

from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont,FluentIcon)
from DataWidget.DataInterface import DataInterface
from LabelWidget.LabelInterface import LabelInterface


class AoiWindow(MSFluentWindow):
    """ Main window """
    def __init__(self,Role:int = 0):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowIcon(QPixmap(os.path.join(os.path.dirname(__file__), 'hr.svg')))

        self.dataInterface = DataInterface()
        self.labelInterface = LabelInterface()
        self.addSubInterface(self.dataInterface,FluentIcon.APPLICATION, "数据管理", None,NavigationItemPosition.TOP,False)
        self.addSubInterface(self.labelInterface,FluentIcon.EDIT, "标注管理", None,NavigationItemPosition.TOP,False)
        self.setWindowTitle("AOI标注工具")

        self.dataInterface.projectCard.onLabelDatasetBtnClicked.connect(self.onLabelDatasetBtnClicked)

        self.resize(1600, 1000)

        # Center the window on the screen
        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            screen.center().x() - size.width() // 2,
            screen.center().y() - size.height() // 2
        )

    def onLabelDatasetBtnClicked(self, dataset: int):
        self.stackedWidget.setCurrentIndex(1)
        self.labelInterface.setDataset(dataset)
        

