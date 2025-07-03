from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from qfluentwidgets import (MessageDialog,MessageBoxBase,LineEdit,BodyLabel,setFont,InfoBar,InfoBarPosition)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO

class DatasetDialog(MessageBoxBase):
    def __init__(self, parent=None):
        """ Initialize the ProjectDialog widget """
        super().__init__(parent)
        self.setWindowTitle("新建数据集")

        self.gLayout = QGridLayout()
        self.gLayout.setContentsMargins(0, 0, 0, 0)

        self.yesButton.setText("创建")
        self.cancelButton.setText("取消")

        self.lblTitle = BodyLabel("新建数据集")
        setFont(self.lblTitle, 20, QFont.Bold)
        self.lineName = LineEdit()
        self.lineDesc = LineEdit()
        self.lineVersion=LineEdit()
        self.lineName.setFixedWidth(220)
        self.lineName.setPlaceholderText("请输入数据集名称")
        self.lineDesc.setPlaceholderText("请输入数据集描述")
        self.lineVersion.setPlaceholderText("请输入数据集版本")

        self.gLayout.addWidget(BodyLabel("名称"), 0, 0)
        self.gLayout.addWidget(self.lineName, 0, 1)
        self.gLayout.addWidget(BodyLabel("描述"), 1, 0)
        self.gLayout.addWidget(self.lineDesc, 1, 1)
        self.gLayout.addWidget(BodyLabel("版本"), 2, 0)
        self.gLayout.addWidget(self.lineVersion, 2, 1)

        self.viewLayout.addWidget(self.lblTitle, 0, Qt.AlignLeft)
        self.viewLayout.addLayout(self.gLayout)

    
