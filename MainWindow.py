import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPixmap

from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont,FluentIcon,NavigationBarPushButton)
from DataWidget.DataInterface import DataInterface
from LabelWidget.LabelInterface import LabelInterface
from CheckWidget.CheckInterface import CheckInterface
from GlobalData import gData

class AoiWindow(MSFluentWindow):
    """ Main window """
    def __init__(self,Role:int = 0):
        super().__init__()
        setTheme(Theme.DARK)
        self.setWindowIcon(QPixmap('hr.svg'))

        self.dataInterface = DataInterface()
        self.labelInterface = LabelInterface()
        self.checkInterface = CheckInterface()
        self.addSubInterface(self.dataInterface,FluentIcon.APPLICATION, "数据管理", None,NavigationItemPosition.TOP,False)
        self.addSubInterface(self.labelInterface,FluentIcon.EDIT, "标注管理", None,NavigationItemPosition.TOP,False)
        self.checkBtn=self.addSubInterface(self.checkInterface,FluentIcon.CHECKBOX, "校验模型", None,NavigationItemPosition.TOP,False)
        self.setWindowTitle("AOI标注工具")

        self.dataInterface.projectCard.onLabelDatasetBtnClicked.connect(self.onLabelDatasetBtnClicked)

        self.resize(1600, 1000)

        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            screen.center().x() - size.width() // 2,
            screen.center().y() - size.height() // 2
        )
        self.__initConnect__() 

    def __initConnect__(self):
        """初始化连接"""
        if not gData.isDebug:
            self.checkBtn.clicked.connect(self.onCheckBtnClicked)


    def onLabelDatasetBtnClicked(self, dataset: int):
        self.stackedWidget.setCurrentIndex(1)
        self.labelInterface.setDataset(dataset)

    def onCheckBtnClicked(self):
        """校验按钮点击事件"""
        self.checkInterface.measureWidget.setMeasureData()

    def closeEvent(self, event):
        """重写关闭事件"""
        print("关闭窗口")
        # if self.checkInterface.client:
        #     self.checkInterface.client.stop()
        if self.checkInterface.executor:
            self.checkInterface.executor.stop()

        super().closeEvent(event)

