import sys
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage,QPixmap

from qfluentwidgets import (NavigationItemPosition, MessageBox, setTheme, Theme, MSFluentWindow,
                            NavigationAvatarWidget, qrouter, SubtitleLabel, setFont,FluentIcon,NavigationBarPushButton,MessageDialog)
from DataWidget.DataInterface import DataInterface
from LabelWidget.LabelInterface import LabelInterface
from CheckWidget.CheckInterface import CheckInterface
from GlobalData import gData
from datetime import datetime,date
from PySide6.QtCore import QTimer
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
        self.setWindowTitle("英锐捷-AI标注训练软件")

        self.dataInterface.projectCard.onLabelDatasetBtnClicked.connect(self.onLabelDatasetBtnClicked)

        self.resize(1600, 1000)

        screen = self.screen().geometry()
        size = self.geometry()
        self.move(
            screen.center().x() - size.width() // 2,
            screen.center().y() - size.height() // 2
        )
        self.__initConnect__() 

        self.isExpired = False
        QTimer.singleShot(0, self.validityDateCheck)

    
    def validityDateCheck(self):
        """校验软件使用日期是否过期"""
        currentDate = date.today()
        validDate = date(2026,4,1)
        if currentDate > validDate:
            self.isExpired = True
            # dlg=MessageBox("软件到期","软件使用日期已过期，无法继续使用",self.window())
            # dlg.exec()
            # self.close()

    def __initConnect__(self):
        """初始化连接"""
        if not gData.isDebug:
            pass

    def onLabelDatasetBtnClicked(self, dataset: int):
        self.stackedWidget.setCurrentIndex(1)
        self.labelInterface.setDataset(dataset)

    def closeEvent(self, event):
        """重写关闭事件"""
        print("关闭窗口")
        # if self.checkInterface.client:
        #     self.checkInterface.client.stop()
        if self.isExpired:
            super().closeEvent(event)
            return
        
        dlg=MessageBox("退出程序","确认是否关闭软件",self.window())
        dlg.yesButton.setText("退出")
        dlg.cancelButton.setText("取消")
        if dlg.exec() == MessageBox.Accepted:
            if self.checkInterface.executor:
                self.checkInterface.executor.stop()
            if self.dataInterface.watcher is not None:
                self.dataInterface.watcher.stop()
            super().closeEvent(event)
        else:
            event.ignore()


