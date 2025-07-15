from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QFileDialog
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,HeaderCardWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,
                            ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox,PillPushButton,SwitchButton)
from Database.DataOperate import DataOperate as DO
from Database.BaseModel import *
from qfluentwidgets import FluentIcon as FIF

class ParameterCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("参数设置")
        self.headerLayout.setContentsMargins(12,0,6,0)
        self.viewLayout.setContentsMargins(6,6,6,6)
        self.headerView.setFixedHeight(28)

        self.identifyModelPath=''
        self.locatModelPath=''


        self.__initWidget__()
        self.__initConnect__()

        self.stopBtn.setEnabled(False)
        self.locatBtn.hide()
        self.locatLbl.hide()


    def __initWidget__(self):
        """初始化界面"""
        self.vLayout=QVBoxLayout()
        self.startBtn=PrimaryPushButton(FIF.ROBOT,"加载模型")
        self.stopBtn=PushButton(FIF.STOP_WATCH,"关闭模型")
        self.hBtnLayout=QHBoxLayout()
        self.hBtnLayout.addWidget(self.startBtn)
        self.hBtnLayout.addWidget(self.stopBtn)
        self.vLayout.addLayout(self.hBtnLayout)

        self.gLayout=QGridLayout()
        self.identifyBtn=PushButton(FIF.EDIT,"选择模型一")
        self.identifyLbl=BodyLabel("未选择模型")
        self.enableLocatBtn=SwitchButton()
        self.locatBtn=PushButton(FIF.EDIT,"选择模型二")
        self.locatLbl=BodyLabel("未选择模型")

        self.enableLocatBtn.setOnText("启用")
        self.enableLocatBtn.setOffText("关闭")

        self.gLayout.addWidget(self.identifyBtn,0,0)
        self.gLayout.addWidget(self.identifyLbl,0,1)
        self.gLayout.addWidget(BodyLabel("模型二"),1,0)
        self.gLayout.addWidget(self.enableLocatBtn,1,1)
        self.gLayout.addWidget(self.locatBtn,2,0)
        self.gLayout.addWidget(self.locatLbl,2,1)


        self.gLayout.setAlignment(Qt.AlignTop|Qt.AlignLeft)
        self.gLayout.setSpacing(7)

        self.hBtnLayout.setAlignment(Qt.AlignLeft)

        self.vLayout.setAlignment(Qt.AlignTop)
        self.vLayout.addSpacing(10)
        self.vLayout.addLayout(self.gLayout)

        self.viewLayout.addLayout(self.vLayout)
        """"""
    
    def __initConnect__(self):
        """初始化信号连接"""
        self.identifyBtn.clicked.connect(self.onIdentifyBtnClicked)
        self.locatBtn.clicked.connect(self.onLocatBtnClicked)
        self.enableLocatBtn.checkedChanged.connect(self.onEnableLocatBtnChanged)
    
    
    def onIdentifyBtnClicked(self):
        """选择识别模型按钮点击事件"""
        self.identifyModelPath=QFileDialog.getOpenFileName(self,"选择识别模型",".","模型文件(*.pt)")[0]
        if self.identifyModelPath:
            self.identifyLbl.setText(self.identifyModelPath.split("/")[-1])


    def onLocatBtnClicked(self):
        """选择定位模型按钮点击事件"""
        self.locatModelPath=QFileDialog.getOpenFileName(self,"选择定位模型",".","模型文件(*.pt)")[0]
        if self.locatModelPath:
            self.locatLbl.setText(self.locatModelPath.split("/")[-1])

    def onEnableLocatBtnChanged(self,checked:bool):
        """定位模型开关按钮状态改变事件"""
        self.locatBtn.setVisible(checked)
        self.locatLbl.setVisible(checked)