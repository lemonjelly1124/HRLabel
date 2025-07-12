from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont,QCursor
from typing import List
import json,os
from pathlib import Path
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QSpacerItem,QSizePolicy
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,MessageBox,ImageLabel,BodyLabel,TableWidget,setFont,
                            ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,ProgressRing,RoundMenu,Action,TransparentToolButton)
from Database.DataOperate import DataOperate as DO
from .ProjectDialog import ProjectDialog
from .DatasetDialog import DatasetDialog
from HRVision.utils.tools import async_run
from Database.BaseModel import *
from PySide6.QtWidgets import QFileDialog
from GlobalData import gData,transform
class ProjectCard(SimpleCardWidget):
    """ Project Card Widget """
    projectEdited = Signal(int, str)
    projectDeleted = Signal(int)
    onLabelDatasetBtnClicked = Signal(int)
    importFinished= Signal(int, int,int)  #state,count,datasetID
    checkLabeledFinished= Signal(dict)  #dataId,isDir

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

        self.editBtn.setToolTip("编辑项目")
        self.deleteBtn.setToolTip("删除项目")
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

        self.importFinished.connect(self.onImportFinished)
        self.checkLabeledFinished.connect(self.onCheckLabeledFinished)

    
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

        self.projectDeleted.emit(self.projectID)


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
                self.projectEdited.emit(self.projectID, project.name)
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
    
    def onImportImageBtnClicked(self, datasetId: int):
        """点击导入图片按钮"""
        fileDialog = QFileDialog(self)
        fileDialog.setFileMode(QFileDialog.ExistingFiles)
        fileDialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp *.tiff)")
        if fileDialog.exec():

            def importImages():
                selectedFiles = fileDialog.selectedFiles()
                if len(selectedFiles)>0:
                    if len(selectedFiles) > 300:
                        selectedFiles = selectedFiles[:300]
                        self.importFinished.emit(1, len(selectedFiles),datasetId)  # Emit signal with state 1 for limited import
                    for filePath in selectedFiles:
                        qimage=QImage(filePath)
                        image=ImageData()
                        image.path = os.path.normpath(filePath)
                        image.dataset = datasetId
                        image.sizeW=qimage.width()
                        image.sizeH=qimage.height()
                        DO.insert_image(image)

                    self.importFinished.emit(2, len(selectedFiles),datasetId)  # Emit signal with state 2 for successful import
                else:
                    self.importFinished.emit(3, 0,datasetId)
            InfoBar.info("导入图片", "正在导入图片，请稍等...", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            async_run(importImages)

    def onImportFinished(self, state: int, count: int,datasetId: int = None):
        if state==1:
            InfoBar.warning("导入图片", "已限制导入图片数量为300张", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
        if state==2:
            InfoBar.success("导入图片", f"成功导入 {count} 张图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            self.setDatasetProgress(datasetId)  # 更新数据集的标注进度
        if state==3:
            InfoBar.warning("导入图片", "未选择图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
    
    def onImportLabeledAction(self,dataId,isDir:False):
        """导入标注数据"""
        labelFilePath=[]
        if isDir:
                # 弹出文件夹选择对话框
            folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹", "", QFileDialog.ShowDirsOnly)
            if not folder_path:
                return []
            # 使用 pathlib 查找文件
            folder = Path(folder_path)
            labelFilePath = list(folder.rglob("*.json"))
        else:
            labelFilePath, _ = QFileDialog.getOpenFileNames(self, "选择标注数据文件", "", "JSON Files (*.json)")

        if not labelFilePath:
            InfoBar.warning("导入标注数据", "未选择标注数据文件", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
        else:
            InfoBar.info("导入标注数据", "正在校验标注数据,共"+str(len(labelFilePath))+"份数据", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
        async_run(lambda: self.checkLabelDatata(labelFilePath, dataId))

    def checkLabelDatata(self, labelFilePath: list, datasetId: int) :
        """校验标注文件数据，判断对应图片是否存在"""
        dataset:Dataset = DO.query_dataset(id=datasetId)[0]
        projectID= dataset.project.id

        decodeErrCount= 0  # 记录无法解析的JSON文件数量
        contentErrCount= 0  # 记录内容不符合要求的JSON文件数量
        imgErrCount= 0  # 记录图片不存在的数量
        successCount= 0  # 记录成功转换的标注文件数量
        for filePath in labelFilePath:
            if os.path.exists(filePath) is False:
                continue
            
            data=None
            with open(filePath, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    f.close()
                except json.JSONDecodeError:
                    decodeErrCount += 1
                    print(f"标注文件 {filePath} 无法解析为JSON")
                    continue

            imageHeight=data.get("imageHeight", 0)
            imageWidth=data.get("imageWidth", 0)
            imagePath=data.get("imagePath", "")
            if imageHeight==0:
                print(f"标注文件 {filePath} 中的 imageHeight 为0")
                contentErrCount += 1
                continue
            if imageWidth==0:
                print(f"标注文件 {filePath} 中的 imageWidth 为0")
                contentErrCount += 1
                continue
            if imagePath=="":
                print(f"标注文件 {filePath} 中的 imagePath 为空")
                contentErrCount += 1
                continue
            # 检查图片是否存在
            absolutePath=os.path.dirname(filePath)+ "\\"+imagePath
            normalized_path = os.path.normpath(absolutePath)  # 规范化路径,去掉路径中的"/../"和"//"
            if not os.path.exists(normalized_path):
                print(f"图片 {normalized_path} 不存在")
                imgErrCount += 1
                continue

            labelStr=transform.transfromToLabels(data.get("shapes",[]),projectID)  # 转换标注数据

            imageData:ImageData = ImageData()
            imageData.path = normalized_path
            imageData.dataset = datasetId
            imageData.sizeW = imageWidth
            imageData.sizeH = imageHeight
            imageData.labels = labelStr
            
            imageData=DO.insert_image(imageData)  # 插入图片数据
            if( imageData.id is not None):
                successCount += 1
        info = {
            "decodeErrCount": decodeErrCount,
            "contentErrCount": contentErrCount,
            "imgErrCount": imgErrCount,
            "successCount": successCount,
            "datasetId": datasetId
        }
        self.checkLabeledFinished.emit(info) 
    def onCheckLabeledFinished(self, info: dict):
        decodeErrCount = info.get("decodeErrCount", 0)
        contentErrCount = info.get("contentErrCount", 0)
        imgErrCount = info.get("imgErrCount", 0)
        successCount = info.get("successCount", 0)
        datasetId = info.get("datasetId", 0)

        if decodeErrCount > 0:
            InfoBar.error("导入标注数据", f"有 {decodeErrCount} 个标注文件无法解析为JSON格式", Qt.Horizontal, isClosable=True, duration=5000, position=InfoBarPosition.TOP, parent=self)
        if contentErrCount > 0:
            InfoBar.error("导入标注数据", f"有 {contentErrCount} 个标注文件内容不符合要求", Qt.Horizontal, isClosable=True, duration=5000, position=InfoBarPosition.TOP, parent=self)
        if imgErrCount > 0:
            InfoBar.error("导入标注数据", f"有 {imgErrCount} 个标注文件中的图片不存在", Qt.Horizontal, isClosable=True, duration=5000, position=InfoBarPosition.TOP, parent=self)
        if successCount > 0:
            InfoBar.success("导入标注数据", f"成功导入 {successCount} 张图片的标注数据", Qt.Horizontal, isClosable=True, duration=5000, position=InfoBarPosition.TOP, parent=self)
            self.setDatasetProgress(datasetId)
    
    def onMoreBtnClicked(self, datasetId: int):
        """ """
        menu= RoundMenu("",self)
        # menu.setAttribute(Qt.WA_DeleteOnClose)
        delAction= Action(FluentIcon.DELETE, "删除数据集")
        fileImportAction= Action(FluentIcon.FOLDER_ADD, "导入标注数据")
        dirImportAction= Action(FluentIcon.DICTIONARY_ADD, "导入标注数据")
        fileImportAction.setToolTip("选择文件")
        dirImportAction.setToolTip("选择文件夹")
        menu.addAction(delAction)
        menu.addAction(fileImportAction)
        menu.addAction(dirImportAction)

        menu.show()
        point= QCursor.pos()
        menu.move(point.x()-170, point.y()-40)


        delAction.triggered.connect(lambda: self.onDeleteDatasetBtnClicked(datasetId))
        fileImportAction.triggered.connect(lambda: self.onImportLabeledAction(dataId=datasetId,isDir=False))
        dirImportAction.triggered.connect(lambda: self.onImportLabeledAction(dataId=datasetId,isDir=True))
     
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
        labelBtn=HyperlinkButton()
        delBtn=HyperlinkButton()
        moreBtn= TransparentToolButton(FluentIcon.MORE)
        hBtnLayout = QHBoxLayout(btnWidget)
        importBtn.setText("导入")
        labelBtn.setText("标注")
        delBtn.setText("删除")
        moreBtn.setToolTip("更多操作")

        labelBtn.clicked.connect(lambda: self.onLabelDatasetBtnClicked.emit(dataId))
        importBtn.clicked.connect(lambda: self.onImportImageBtnClicked(dataId))
        delBtn.clicked.connect(lambda:self.onDeleteDatasetBtnClicked(dataId))
        moreBtn.clicked.connect(lambda: self.onMoreBtnClicked(dataId))

        hBtnLayout.addWidget(importBtn)
        hBtnLayout.addWidget(labelBtn)
        hBtnLayout.addWidget(delBtn)
        hBtnLayout.addWidget(moreBtn)

        hBtnLayout.setSpacing(0)
        hBtnLayout.setContentsMargins(0, 0, 0, 0)
        self.dataTable.setCellWidget(dataRow, 6, btnWidget)

        self.setDatasetProgress(dataId)


        if gData.isDebug:
            delBtn.hide()
        else:
            moreBtn.hide()

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


