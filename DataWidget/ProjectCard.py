from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from typing import List

from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QSpacerItem,QSizePolicy
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,MessageBox,ImageLabel,BodyLabel,TableWidget,setFont,
                            ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,ProgressRing)
from Database.DataOperate import DataOperate as DO
from .ProjectDialog import ProjectDialog
from .DatasetDialog import DatasetDialog

from Database.BaseModel import *
from PySide6.QtWidgets import QFileDialog
from GlobalData import gData
class ProjectCard(SimpleCardWidget):
    """ Project Card Widget """
    onProjectEdited = Signal(int, str)
    onProjectDeleted = Signal(int)
    onLabelDatasetBtnClicked = Signal(int)


    def __init__(self,parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectCard")

        self.projectID = None  # Project ID
        self.__initWidget__()
        self.__initConnect__()

    def __initWidget__(self):
        self.vRightLayout = QVBoxLayout(self)
        self.topCard= SimpleCardWidget()
        self.hCardLayout = QHBoxLayout(self.topCard)
        self.vCardLayout = QVBoxLayout()
        self.hRingLayout=QHBoxLayout()
        self.iconLbl = ImageLabel("hr.svg")
        self.hTitleLayout = QHBoxLayout()
        self.titleLbl = BodyLabel("项目")
        self.editBtn = ToolButton(FluentIcon.EDIT)
        self.deleteBtn= ToolButton(FluentIcon.DELETE)
        self.descLbl = BodyLabel("项目描述")
        self.hBtnLayout = QHBoxLayout()
        self.addDataset=PushButton(FluentIcon.ADD,"添加数据集")
        self.exportBtn=PushButton(FluentIcon.IMAGE_EXPORT,"导出数据集")
        self.trainBtn=PrimaryPushButton(FluentIcon.UPDATE,"开始训练")
        self.stopBtn=PushButton("停止训练")
        self.dataTable = TableWidget()

        self.trainProgress=ProgressRing()
        self.trainProgress.setValue(0)
        self.trainProgress.setTextVisible(True)
        self.trainProgress.setStrokeWidth(10)

        self.saveBtn=PrimaryPushButton("保存模型")
        self.saveBtn.setFixedWidth(80)

        setFont(self.titleLbl, 25, QFont.Bold)
        self.iconLbl.setFixedSize(90, 90)
        self.topCard.setFixedHeight(150)
        self.hBtnLayout.setAlignment(Qt.AlignRight)

        self.dataTable.setColumnCount(7)
        headers = ["ID", "数据集","版本", "描述", "创建时间","标注进度","操作"]
        self.dataTable.setHorizontalHeaderLabels(headers)
        self.dataTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.dataTable.verticalHeader().setVisible(False)

        self.hTitleLayout.addWidget(self.titleLbl)
        self.hTitleLayout.addWidget(self.editBtn)
        self.hTitleLayout.addWidget(self.deleteBtn)
        self.hTitleLayout.setAlignment(Qt.AlignLeft)

        self.vCardLayout.addLayout(self.hTitleLayout)
        self.vCardLayout.addWidget(self.descLbl)

        self.hRingLayout.addWidget(self.trainProgress)
        self.hRingLayout.addWidget(self.saveBtn)
        self.hRingLayout.setContentsMargins(0,0,0,0)

        self.hCardLayout.addWidget(self.iconLbl)
        self.hCardLayout.addLayout(self.vCardLayout)
        self.hCardLayout.addSpacerItem(QSpacerItem(20,20,QSizePolicy.Expanding))
        self.hCardLayout.addLayout(self.hRingLayout)

        self.hBtnLayout.addWidget(self.addDataset)
        self.hBtnLayout.addWidget(self.exportBtn)
        self.hBtnLayout.addWidget(self.trainBtn)
        self.hBtnLayout.addWidget(self.stopBtn)
        
        self.vRightLayout.addWidget(self.topCard)
        self.vRightLayout.addLayout(self.hBtnLayout)
        self.vRightLayout.addWidget(self.dataTable)
        self.vRightLayout.setAlignment(Qt.AlignTop)
    def __initConnect__(self):
        """ Initialize the connections """
        self.editBtn.clicked.connect(self.onEditProjectBtnClicked)
        self.addDataset.clicked.connect(self.onAddDatasetBtnClicked)
        self.deleteBtn.clicked.connect(self.onDeleteProjectBtnClicked)

    
    def onDeleteProjectBtnClicked(self):
        dlg= MessageBox("删除项目","是否确认删除该项目?\n",self.window())
        if dlg.exec() != MessageBox.Accepted:
            return
        affected_rows=DO.delete_project(id=self.projectID)
        DO.delete_label(project_id=self.projectID)
        datasets=DO.query_dataset(project_id=self.projectID)
        for dataset in datasets:
            DO.delete_dataset(id=dataset.id)
            DO.delete_image(dataset_id=dataset.id)

        self.onProjectDeleted.emit(self.projectID)


    def onEditProjectBtnClicked(self):
        """点击编辑按钮"""
        dialog= ProjectDialog(self.window())
        dialog.setTitle("编辑项目")
        dialog.setValue(self.titleLbl.text(), self.descLbl.text())
        if dialog.exec():
            project= Project()
            project.name= dialog.lineName.text()
            project.description= dialog.lineDesc.text()

            affected_rows =DO.update_project(project_id=int(self.projectID),name=project.name, description=project.description)
            if affected_rows >0:
                InfoBar.success( "修改项目信息", "修改项目信息成功",orient=Qt.Horizontal, isClosable=True, duration=3000,position=InfoBarPosition.TOP,parent=self)
                self.titleLbl.setText(project.name)
                self.descLbl.setText(project.description)
                self.onProjectEdited.emit(self.projectID, project.name)
            else:
                InfoBar.warning("修改项目信息", "修改项目信息异常", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
    
    def onAddDatasetBtnClicked(self):
        """点击添加数据集按钮"""
        dialog = DatasetDialog(self.window())
        if dialog.exec():
            dataset=Dataset()
            dataset.name = dialog.lineName.text()
            dataset.description = dialog.lineDesc.text()
            dataset.version = dialog.lineVersion.text()
            dataset.project = self.projectID
            datasetRes:Dataset = DO.insert_dataset(dataset)

            if( datasetRes.id is not None):
                InfoBar.success("添加数据集", "添加数据集成功", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
                dataObj={
                    "id": datasetRes.id,
                    "name": datasetRes.name,
                    "version": datasetRes.version,
                    "description": datasetRes.description,
                    "date": datasetRes.created_at.strftime("%Y-%m-%d")
                }
                self.addDataItem(dataObj)
            else:
                InfoBar.error("添加数据集", "添加数据集失败", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
    
    def onDeleteDatasetBtnClicked(self, dataId: int):
        datasetNmae= ""
        datasetVersion= ""
        for i in range(self.dataTable.rowCount()):
                item = self.dataTable.item(i, 0)
                if item and int(item.text()) == dataId:
                    datasetNmae = self.dataTable.item(i, 1).text()
                    datasetVersion = self.dataTable.item(i, 2).text()
                    break

        dlg= MessageBox("删除数据集","是否确认删除该数据集?\n\n数据集名称:"+datasetNmae+"数据集版本:"+datasetVersion+"\n\n同时将删除数据集的标注数据且不可恢复",parent=self)
        if dlg.exec() != MessageBox.Accepted:
            return
        """点击删除数据集按钮"""
        imageRows=DO.delete_image(dataset_id=dataId)

        affected_rows=DO.delete_dataset(id=dataId)
        if affected_rows ==1:
            InfoBar.success("删除数据集", "删除数据集成功", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            for i in range(self.dataTable.rowCount()):
                item = self.dataTable.item(i, 0)
                if item and int(item.text()) == dataId:
                    self.dataTable.removeRow(i)
        else:
            InfoBar.error("删除数据集", "删除数据集失败", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
    
    def onImportImageBtnClicked(self, dataId: int):
        """点击导入图片按钮"""
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if fileDialog.exec():
            InfoBar.info("导入图片", "正在导入图片，请稍等...", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            selectedFiles = fileDialog.selectedFiles()
            if selectedFiles:
                if len(selectedFiles) > 300:
                    selectedFiles = selectedFiles[:300]
                    InfoBar.warning("导入图片", "已限制导入图片数量为300张", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
                for filePath in selectedFiles:
                    qimage=QImage(filePath)
                    image=ImageData()
                    image.path = filePath
                    image.dataset = dataId
                    image.sizeW=qimage.width()
                    image.sizeH=qimage.height()
                    DO.insert_image(image)

                InfoBar.success("导入图片", f"成功导入 {len(selectedFiles)} 张图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
                self.setDatasetProgress(dataId)  # 更新数据集的标注进度
            else:
                InfoBar.warning("导入图片", "未选择任何图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
    
    
        
    def addDataItem(self, dataObj: dict):
        """ Add a data item to the data table """
        dataRow = self.dataTable.rowCount()
        self.dataTable.insertRow(dataRow)

        dataName = dataObj.get("name", "Unnamed")
        dataId = dataObj.get("id", "0")
        dataVersion = dataObj.get("version", "1.0")
        dataDesc = dataObj.get("description", "")
        dataDate = dataObj.get("date", "2023-01-01")
        itemID= QTableWidgetItem(str(dataId))
        itemName= QTableWidgetItem(dataName)
        itemVersion= QTableWidgetItem(dataVersion)
        itemDesc= QTableWidgetItem(dataDesc)
        itemDate= QTableWidgetItem(dataDate)

        itemName.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        itemID.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        itemDesc.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        itemDate.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        itemVersion.setTextAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        itemID.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)  # 设置为可勾选
        itemID.setCheckState(Qt.Unchecked)  # 初始状态为未勾选
        itemName.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        itemDesc.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        itemDate.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        itemVersion.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)

        self.dataTable.setItem(dataRow, 0, itemID)
        self.dataTable.setItem(dataRow, 1, itemName)
        self.dataTable.setItem(dataRow, 2, itemVersion)
        self.dataTable.setItem(dataRow, 3, itemDesc)
        self.dataTable.setItem(dataRow, 4, itemDate)

        progressWdg=ProgressWidget()
        self.dataTable.setCellWidget(dataRow, 5, progressWdg)

        btnWidget= QWidget()
        importBtn= HyperlinkButton()
        delBtn=HyperlinkButton()
        labelBtn=HyperlinkButton()
        hBtnLayout = QHBoxLayout(btnWidget)
        importBtn.setText("导入")
        delBtn.setText("删除")
        labelBtn.setText("标注")

        delBtn.clicked.connect(lambda: self.onDeleteDatasetBtnClicked(dataId))
        labelBtn.clicked.connect(lambda: self.onLabelDatasetBtnClicked.emit(dataId))
        importBtn.clicked.connect(lambda: self.onImportImageBtnClicked(dataId))

        hBtnLayout.addWidget(importBtn)
        hBtnLayout.addWidget(labelBtn)
        hBtnLayout.addWidget(delBtn)

        hBtnLayout.setSpacing(0)
        hBtnLayout.setContentsMargins(0, 0, 0, 0)
        self.dataTable.setCellWidget(dataRow, 6, btnWidget)

        self.setDatasetProgress(dataId)

    #设置数据集的标注进度
    def setDatasetProgress(self, dataId: int):
        images:list[ImageData]=DO.query_image(dataset_id=dataId)
        labeledCount = sum(1 for img in images if img.labels is not None)
        totalCount = len(images)

        for i in range(self.dataTable.rowCount()):
            item = self.dataTable.item(i, 0)
            if item and int(item.text()) == dataId:
                progressWdg: ProgressWidget = self.dataTable.cellWidget(i, 5)
                progressWdg.setCount(labeledCount, totalCount)
                break

    def setProject(self,project:Project):
        """ Set the project data """
        self.projectID = project.id
        self.titleLbl.setText(project.name)
        self.descLbl.setText(project.description)

        #刷新数据集列表
        self.dataTable.setRowCount(0)  # Clear existing rows

        datasets: List[Database] = DO.query_dataset(project_id=self.projectID)
        for dataset in datasets:
            dataObj = {
                "id": dataset.id,
                "name": dataset.name,
                "version": dataset.version,
                "description": dataset.description,
                "date": dataset.created_at.strftime("%Y-%m-%d")
            }
            self.addDataItem(dataObj)

class ProgressWidget(QWidget):
    """ Progress Widget for displaying progress bars """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("ProgressWidget")

        self.labeledCount= 0
        self.totalCount= 0

        self.hLayout = QHBoxLayout(self)
        self.progressBar = ProgressBar()
        self.progressLbl = BodyLabel("0%")
        self.countLbl= BodyLabel("0/0")
        self.progressBar.setRange(0, 100)
        self.progressBar.setValue(50)
        self.hLayout.addWidget(self.countLbl)
        self.hLayout.addWidget(self.progressBar)
        self.hLayout.addWidget(self.progressLbl)
        self.hLayout.setContentsMargins(0, 0, 0, 0)
    
    def setCount(self, labeledCount: int, totalCount: int):
        """ Set the labeled and total count """
        self.labeledCount = labeledCount
        self.totalCount = totalCount
        self.countLbl.setText(f"{self.labeledCount}/{self.totalCount}")
        if self.totalCount > 0:
            progress = int((self.labeledCount / self.totalCount) * 100)
            self.progressBar.setValue(progress)
            self.progressLbl.setText(f"{progress}%")
        else:
            self.progressBar.setValue(0)
            self.progressLbl.setText("0%")
