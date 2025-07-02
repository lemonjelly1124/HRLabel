from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QImage,QPixmap,QFont,QColor
from PySide6.QtWidgets import QApplication,QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QSpacerItem,QSizePolicy
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,TransparentToolButton,TransparentPushButton,MessageBox,InfoBar,InfoBarPosition,ListWidget,HeaderCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ColorPickerButton)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
class LabelCard(HeaderCardWidget):
    onLabelColorChanged = Signal(int,QColor)

    def __init__(self, parent=None):
        """ Initialize the LabelCard widget """
        super().__init__(parent)

        self.vLabelLayout = QVBoxLayout()
        self.addLabelBtn = ToolButton(FluentIcon.ADD)
        self.labelList= ListWidget()
        self.setFixedWidth(350)

        self.setTitle("标签列表")
        self.headerLayout.setContentsMargins(8, 8, 8, 0)
        self.viewLayout.setContentsMargins(0, 8, 4, 8)

        self.vLabelLayout.addWidget(self.addLabelBtn,0,Qt.AlignRight)
        self.vLabelLayout.addWidget(self.labelList)
        self.viewLayout.addLayout(self.vLabelLayout)

        self.datasetID = None  # 当前数据集ID

        self.__initConnect__()

    def setLabelList(self, datasetID: int):
        """ 设置标签列表 """
        self.datasetID = datasetID
        self.labelList.clear()
        dataset:Dataset = Dataset.get(Dataset.id == datasetID)
        project:Project=dataset.project

        labels:list[LabelData] = DO.query_label(project_id=project.id)
        for label in labels:
            self.addLabelItem(label.id, label.name, QColor(label.color))

    def addLabelItem(self,lblID:str,lblName:str,color: QColor):
        """ 添加一个新的LabelItem """
        listItem = QListWidgetItem(self.labelList)
        lblItem = LabelItem(lblID,lblName,color)
        listItem.setSizeHint(lblItem.sizeHint())
        lblItem.onColorChanged.connect(self.onLabelColorChanged)
        lblItem.onDeleteClicked.connect(self.onDeleteBtnClicked)

        self.labelList.addItem(listItem)
        self.labelList.setItemWidget(listItem, lblItem)

    def onAddBtnClicked(self):
        """ 点击添加按钮 """
        label=LabelData()
        label.name = "新标签"
        label.color = "#36e1ff"
        label.project = Dataset.get(Dataset.id == self.datasetID).project.id
        label=DO.insert_label(label)
        self.addLabelItem(label.id, label.name, QColor(label.color))

    def onDeleteBtnClicked(self, lblID: int):
        dlg= MessageBox("删除标签", "确定要删除该标签吗？\n", parent=QApplication.activeWindow())
        if dlg.exec() != MessageBox.Accepted:
            return
        DO.delete_label(id=lblID)
        for i in range(self.labelList.count()):
            item = self.labelList.item(i)
            if isinstance(self.labelList.itemWidget(item), LabelItem):
                lblItem:LabelItem = self.labelList.itemWidget(item)
                if lblItem.lblID == lblID:
                    self.labelList.takeItem(i)
                    break


        InfoBar.success("删除标签", "标签已成功删除", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=QApplication.activeWindow())


    def __initConnect__(self):
        """ Initialize connections """
        self.addLabelBtn.clicked.connect(self.onAddBtnClicked)
    
class LabelItem(QWidget):
    onNameChanged = Signal(int,str)
    onColorChanged = Signal(int,QColor)
    onDeleteClicked=Signal(int)

    """ Custom QListWidgetItem for labels """
    def __init__(self,lblID:int,lblName:str,color: QColor, parent=None):
        super().__init__(parent)
        self.setObjectName("LabelItem")
        self.lblID = lblID

        self.__initWidget__( lblName, color)
        self.__initConnect__()

    def __initWidget__(self,name:str,color: QColor):
        """ 初始化布局 """
        self.hLayout = QHBoxLayout(self)
        self.color=ColorPickerButton(color,"选择颜色",enableAlpha=True)
        self.lblName= BodyLabel(name)
        self.lineName = LineEdit(self)
        self.editBtn=TransparentToolButton(FluentIcon.EDIT)
        self.deleteBtn=TransparentToolButton(FluentIcon.DELETE)
        self.confirmBtn=TransparentToolButton(FluentIcon.ACCEPT_MEDIUM)
        self.cancelBtn=TransparentToolButton(FluentIcon.CANCEL_MEDIUM)

        self.color.setFixedSize(24, 24)

        self.hLayout.addWidget(self.color)
        self.hLayout.addWidget(self.lblName)
        self.hLayout.addWidget(self.lineName)
        self.hLayout.addWidget(self.editBtn)
        self.hLayout.addWidget(self.deleteBtn)
        self.hLayout.addWidget(self.confirmBtn)
        self.hLayout.addWidget(self.cancelBtn)

        self.hLayout.setContentsMargins(0,4,2,4)
        self.setEditState(False)
    
    def setEditState(self, state: bool):
        """ 设置编辑状态 """
        self.lineName.setVisible(state)
        self.confirmBtn.setVisible(state)
        self.cancelBtn.setVisible(state)
        self.lblName.setVisible(not state)
        self.editBtn.setVisible(not state)
        self.deleteBtn.setVisible(not state)

    def onEditBtnClicked(self):
        """ 点击编辑按钮 """
        self.setEditState(True)
        self.lineName.setText(self.lblName.text())
    def onConfirmBtnClicked(self):
        """ 点击确认按钮 """
        self.setEditState(False)
        self.lblName.setText(self.lineName.text())
        # self.onNameChanged.emit(self.lblID,self.lblName.text())
        DO.update_label(self.lblID, name=self.lblName.text())
    def onCancelBtnClicked(self):
        """ 点击取消按钮 """
        self.setEditState(False)
    def onColorChangedSlot(self, color: QColor):
        """ 颜色改变信号处理 """
        self.onColorChanged.emit(self.lblID, color)
        DO.update_label(self.lblID, color=color.name())

    def onDeleteBtnClicked(self):
        """ 点击删除按钮 """
        self.onDeleteClicked.emit(self.lblID)
    def __initConnect__(self):
        """ Initialize connections """
        self.editBtn.clicked.connect(self.onEditBtnClicked)
        self.confirmBtn.clicked.connect(self.onConfirmBtnClicked)
        self.cancelBtn.clicked.connect(self.onCancelBtnClicked)
        self.color.colorChanged.connect(self.onColorChangedSlot)
        self.deleteBtn.clicked.connect(self.onDeleteBtnClicked)