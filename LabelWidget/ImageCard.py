from PySide6.QtCore import Qt,Signal,QRectF
from PySide6.QtGui import QImage,QPixmap,QFont,QColor,QPainter
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QSpacerItem,QSizePolicy
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,ToolButton,TransparentToolButton,TransparentPushButton,ListWidget,HeaderCardWidget,
                            ImageLabel,BodyLabel,setFont,ImageLabel,InfoBarIcon,InfoIconWidget)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from pathlib import Path
import os,ast
class ImageCard(HeaderCardWidget):
    onImageClicked = Signal(int)
    def __init__(self, parent=None):
        """ Initialize the ImageCard widget """
        super().__init__(parent)
        self.imageList= ListWidget()
        self.setFixedWidth(350)
        self.setTitle("图片列表")
        self.headerLayout.setContentsMargins(8, 8, 8, 0)
        self.viewLayout.setContentsMargins(8, 8, 8, 8)
        self.viewLayout.addWidget(self.imageList)

        self.headerLayout.setSpacing(0)
        self.headerLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.headerLayout.addWidget(InfoIconWidget(InfoBarIcon.INFORMATION))
        self.headerLayout.addSpacing(3)
        self.headerLayout.addWidget(BodyLabel("已查看"))
        self.headerLayout.addSpacing(5)
        self.headerLayout.addWidget(InfoIconWidget(InfoBarIcon.WARNING))
        self.headerLayout.addSpacing(3)
        self.headerLayout.addWidget(BodyLabel("未标注"))
        self.headerLayout.addSpacing(5)
        self.headerLayout.addWidget(InfoIconWidget(InfoBarIcon.SUCCESS))
        self.headerLayout.addSpacing(3)
        self.headerLayout.addWidget(BodyLabel("已标注"))
        self.headerLayout.addSpacing(5)
        self.headerLayout.addWidget(InfoIconWidget(InfoBarIcon.ERROR))
        self.headerLayout.addSpacing(3)
        self.headerLayout.addWidget(BodyLabel("异常"))

        self.datasetID = None

    
    def addImageItem(self,imgID:int,imgPath:str,labelStatus:InfoBarIcon=InfoBarIcon.INFORMATION):
        """ 添加一个新的ImageItem """
        listItem = QListWidgetItem(self.imageList)
        imgItem = ImageItem(imgID, imgPath, labelStatus)
        listItem.setSizeHint(imgItem.sizeHint())
        self.imageList.addItem(listItem)
        self.imageList.setItemWidget(listItem, imgItem)
        imgItem.onImageClicked.connect(self.onImageClicked)

    def setImageList(self,datasetID:int):
        """ 设置图片列表 """
        self.datasetID = datasetID

        labelIDArr = self.getLabelIDArr(datasetID)
        self.imageList.clear()
        images:list[ImageData]=DO.query_image(dataset_id=datasetID)
        for img in images:
            status = self.checkLabelItems(img.labels,labelIDArr)

            if not Path(img.path).exists():
                status = InfoBarIcon.ERROR

            self.addImageItem(img.id, img.path, status)
        
        if self.imageList.count() > 0:
            firstItem = self.imageList.item(0)
            firstImgItem:ImageItem = self.imageList.itemWidget(firstItem)
            firstImgItem.onImageClicked.emit(firstImgItem.imgID)
            self.imageList.setCurrentRow(0)
    
    def refreshImageStatus(self,imgID:int):
        """ 刷新当前选中的图片 """
        labelIDArr = self.getLabelIDArr(self.datasetID)
        for i in range(self.imageList.count()):
            item = self.imageList.item(i)
            imgItem:ImageItem = self.imageList.itemWidget(item)
            if imgItem.imgID == imgID:
                item = self.imageList.item(i)
                imgItem:ImageItem = self.imageList.itemWidget(item)
                imgData:ImageData = DO.query_image(id=imgItem.imgID)[0]
                imgItem.stuatsIcon.icon=self.checkLabelItems(imgData.labels,labelIDArr)

    def onNextImage(self,currImgID):
        for i in range(self.imageList.count()):
            item = self.imageList.item(i)
            imgItem:ImageItem = self.imageList.itemWidget(item)
            if imgItem.imgID == currImgID:
                nextIndex = (i + 1)
                if nextIndex < self.imageList.count():
                    nextItem = self.imageList.item(nextIndex)
                    nextImgItem:ImageItem = self.imageList.itemWidget(nextItem)
                    nextImgItem.onImageClicked.emit(nextImgItem.imgID)
                    self.imageList.setCurrentRow(nextIndex)
                    break
    def onPrevImage(self,currImgID):
        for i in range(self.imageList.count()):
            item = self.imageList.item(i)
            imgItem:ImageItem = self.imageList.itemWidget(item)
            if imgItem.imgID == currImgID:
                prevIndex = (i - 1)
                if prevIndex >= 0:
                    prevItem = self.imageList.item(prevIndex)
                    prevImgItem:ImageItem = self.imageList.itemWidget(prevItem)
                    prevImgItem.onImageClicked.emit(prevImgItem.imgID)
                    self.imageList.setCurrentRow(prevIndex)
                    break
    def deleteImageItem(self,imgID:int):
        """ 删除指定ID的图片 """
        for i in range(self.imageList.count()):
            item = self.imageList.item(i)
            imgItem:ImageItem = self.imageList.itemWidget(item)
            if imgItem.imgID == imgID:
                self.imageList.takeItem(i)

                nextIndex = i
                if nextIndex >= self.imageList.count():
                    nextIndex = self.imageList.count() - 1
                if nextIndex >= 0:
                    nextItem = self.imageList.item(nextIndex)
                    nextImgItem:ImageItem = self.imageList.itemWidget(nextItem)
                    nextImgItem.onImageClicked.emit(nextImgItem.imgID)
                    self.imageList.setCurrentRow(nextIndex)
                break

    
    def checkLabelItems(self,labelStr:str,labelIDArr:list[str]):
        """ 校验标签字符串 """
        status = None
        if labelStr=="[]":
            status = InfoBarIcon.INFORMATION
        elif labelStr is None or labelStr=="":
            status = InfoBarIcon.WARNING
        else:
            status = InfoBarIcon.SUCCESS
            if labelIDArr is not None:
                itemArr=ast.literal_eval(labelStr)
                for item in itemArr:
                    labelID = item.get("label_id", None)
                    # print(f"labelID:{labelID},labelIDArr:{labelIDArr}")
                    if labelID is None or labelID not in labelIDArr:
                        status = InfoBarIcon.ERROR
                        break
        return status
    
    def getLabelIDArr(self,datasetID:int):
        """ 获取当前数据集的标签ID列表 """
        dataset= Dataset.get(Dataset.id == datasetID)
        project_id = dataset.project.id

        labels=DO.query_label(project_id=project_id)

        labelIDArr = [label.id for label in labels]
        return labelIDArr


class ImageItem(QWidget):
    onImageClicked = Signal(int)
    def __init__(self,imgID:int,imgPath:str,labelStatus:InfoBarIcon=InfoBarIcon.INFORMATION, parent=None):
        super().__init__(parent)
        self.setObjectName("ImageItem")
        self.imgID = imgID
        self.imgPath = imgPath

        self.hLayout = QHBoxLayout(self)
        self.stuatsIcon=InfoIconWidget(labelStatus)
        self.nameLbl=BodyLabel()

        self.nameLbl.setText(os.path.normpath(imgPath).split("\\")[-1])

        self.hLayout.addWidget(self.stuatsIcon)
        self.hLayout.addWidget(self.nameLbl)
        self.hLayout.setContentsMargins(0,6,0,6)
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.onImageClicked.emit(self.imgID)
        super().mousePressEvent(event)

