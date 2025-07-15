from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from PySide6.QtGui import QFont
from PySide6.QtCore import Qt
from qfluentwidgets import (MessageDialog,MessageBoxBase,LineEdit,BodyLabel,setFont,InfoBar,InfoBarPosition,ComboBox,SpinBox,CheckBox)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from GlobalData import gData


class TrainModelDialog(MessageBoxBase):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.titleLbl=BodyLabel('训练模型',self)
        setFont(self.titleLbl,24,QFont.Weight.DemiBold)
        self.yesButton.setText("开始训练")
        self.cancelButton.setText("取消")

        self.gLayout=QGridLayout()
        self.gLayout.setContentsMargins(0,0,0,0)
        self.viewLayout.addWidget(self.titleLbl)
        self.viewLayout.addLayout(self.gLayout)

        self.cmbModel=ComboBox()
        self.cmbModel.addItems(["物体识别","语义分割"])

        self.spnEpochs=SpinBox(self)
        self.spnBatchSize=SpinBox(self)
        self.spnWorkers=SpinBox(self)

        self.cmbModel.setCurrentIndex(0)

        self.spnEpochs.setRange(1,1000)
        self.spnBatchSize.setRange(1,128)
        self.spnWorkers.setRange(1,8)

        self.spnEpochs.setValue(gData.watcherConfig['epochs'])
        self.spnBatchSize.setValue(gData.watcherConfig['batch_size'])
        self.spnWorkers.setValue(gData.watcherConfig['workers'])

        self.chkSplit=CheckBox()

        self.gLayout.addWidget(BodyLabel('模型',self),0,0)
        self.gLayout.addWidget(self.cmbModel,0,1)
        self.gLayout.addWidget(BodyLabel('轮数',self),2,0)
        self.gLayout.addWidget(self.spnEpochs,2,1)
        self.gLayout.addWidget(BodyLabel('批次大小',self),3,0)
        self.gLayout.addWidget(self.spnBatchSize,3,1)
        self.gLayout.addWidget(BodyLabel('线程数',self),4,0)
        self.gLayout.addWidget(self.spnWorkers,4,1)
        self.gLayout.addWidget(BodyLabel('拆分图片',self),5,0)
        self.gLayout.addWidget(self.chkSplit,5,1)
