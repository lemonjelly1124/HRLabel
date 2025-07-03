
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from qfluentwidgets import (MessageDialog,MessageBoxBase,LineEdit,BodyLabel,setFont,InfoBar,InfoBarPosition)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
class ProjectDialog(MessageBoxBase):
    def __init__(self, parent=None):
        """ Initialize the ProjectDialog widget """
        super().__init__(parent)
        self.setWindowTitle("新建项目")
        self.isEdit=False

        self.yesButton.setText("创建")
        self.cancelButton.setText("取消")
        self.lblTitle = BodyLabel("新建项目")
        setFont(self.lblTitle, 20, QFont.Bold)

        self.hLayout1= QHBoxLayout()
        self.hLayout2= QHBoxLayout()
        self.lineName= LineEdit()
        self.lineDesc= LineEdit()
        self.lineName.setFixedWidth(220)
        self.lineName.setPlaceholderText("请输入项目名称")
        self.lineDesc.setPlaceholderText("请输入项目描述")

        self.hLayout1.addWidget(BodyLabel("项目名称:"))
        self.hLayout1.addWidget(self.lineName)
        self.hLayout2.addWidget(BodyLabel("项目描述:"))
        self.hLayout2.addWidget(self.lineDesc)
        self.hLayout1.setContentsMargins(0, 0, 0, 0)
        self.hLayout2.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addWidget(self.lblTitle,0,Qt.AlignLeft)
        self.viewLayout.addLayout(self.hLayout1)
        self.viewLayout.addLayout(self.hLayout2)
        self.yesButton.clicked.disconnect()
        self.yesButton.clicked.connect(self.onYesBtnClicked)
    def onYesBtnClicked(self):
        name= self.lineName.text()
        if name is not None:
            if self.isEdit==False and DO.isExistProject(name):
                InfoBar.error( "添加项目失败","项目名称已存在",Qt.Horizontal, isClosable=True, duration=3000,position=InfoBarPosition.TOP,parent=self.parent())
            else:
                self.accept()
        else:
            InfoBar.warning("添加项目失败", "项目名称不能为空", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self.parent())
    
    def setTitle(self, title: str):
        self.lblTitle.setText(title)
    def setValue(self, name: str, desc: str):
        self.isEdit = True
        self.lineName.setText(name)
        self.lineDesc.setText(desc)


        

