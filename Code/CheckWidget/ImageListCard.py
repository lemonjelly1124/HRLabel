import glob
import os
import shutil
from PySide6.QtCore import Qt,Signal,QSize, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QSpacerItem,QSizePolicy
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QFileDialog
from qfluentwidgets import (PushButton,InfoIconWidget,InfoBarIcon,ScrollArea,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,HeaderCardWidget,SimpleCardWidget
                            ,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox,TransparentToolButton,CardWidget)
from Database.DataOperate import DataOperate as DO
from Database.BaseModel import *
from PySide6.QtWidgets import QFileDialog
from HRVision.utils.tools import async_run
class ImageListCard(HeaderCardWidget):

    onImageClicked = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("图片列表")
        self.setFixedHeight(190)
        self.headerLayout.setContentsMargins(12,0,6,0)
        self.headerView.setFixedHeight(28)
        self.__initWidget__()
        self.__initConnect__()

        self.imgPath=""


    def __initWidget__(self):
        """"""
        self.imageView =  QWidget()
        self.scrollArea =  HorizontalScrollArea()
        self.hLisatLayout = QHBoxLayout(self.imageView)
        self.scrollArea.setWidget(self.imageView)
        self.viewLayout.addWidget(self.scrollArea)

        self.importBtn=TransparentToolButton()
        self.dirBtn=TransparentToolButton()
        self.exportBtn=TransparentToolButton()
        self.clearBtn=TransparentToolButton()
        self.importBtn.setIcon(FluentIcon.PHOTO)
        self.dirBtn.setIcon(FluentIcon.FOLDER)
        self.exportBtn.setIcon(FluentIcon.IMAGE_EXPORT)
        self.clearBtn.setIcon(FluentIcon.DELETE)
        self.headerLayout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed))
        self.headerLayout.addWidget(self.importBtn)
        self.headerLayout.addWidget(self.dirBtn)    
        self.headerLayout.addWidget(self.exportBtn)
        self.headerLayout.addWidget(self.clearBtn)


        self.viewLayout.setContentsMargins(0, 0, 0, 0)
        self.hLisatLayout.setContentsMargins(0, 0, 0, 0)
        self.hLisatLayout.setAlignment(Qt.AlignLeft)

    def __initConnect__(self):
        """"""
        self.importBtn.clicked.connect(self.onImportBtnClicked)
        self.dirBtn.clicked.connect(self.onDirBtnClicked)
        self.clearBtn.clicked.connect(self.onClearBtnClicked)
        self.exportBtn.clicked.connect(self.onExportBtnClicked)
    
    def onImportBtnClicked(self):
        """ 点击导入按钮 """
        # def importImg():
        fileNames, _ = QFileDialog.getOpenFileNames(self, "选择图片", "", "Images (*.png *.xpm *.jpg *.bmp)")
        if fileNames:
            if len(fileNames)>100:
                MessageBox.warning("警告","一次最多导入100张图片",self.window())
                fileNames=fileNames[:100]
            for fileName in fileNames:
                self.insertImage(fileName)

        # async_run(importImg)

    def onDirBtnClicked(self):
        """ 点击选择图片文件夹按钮 """
        # 打开文件夹选择对话框
        folder_path = QFileDialog.getExistingDirectory(self, "选择包含图片的文件夹")
        
        if folder_path:
            # 支持的图片格式（可以根据需要扩展）
            image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
            
            # 获取当前文件夹中的文件（不遍历子文件夹）
            image_paths = []
            for file in os.listdir(folder_path):
                file_path = os.path.join(folder_path, file)
                if os.path.isfile(file_path) and any(file.lower().endswith(ext) for ext in image_extensions):
                    image_paths.append(file_path)
            if len(image_paths)>100:
                MessageBox.warning("警告","一次最多导入100张图片",self.window())
                image_paths=image_paths[:100]
            for image_path in image_paths:
                self.insertImage(image_path)

    def onExportBtnClicked(self):
        """ 点击导出按钮 """

        if self.imgPath=="":
            return
        fileName=os.path.basename(self.imgPath)
        newPath=QFileDialog.getSaveFileName(self, "导出图片", fileName, "Images (*.png *.jpg *.bmp)")
        if newPath:
            shutil.copy(self.imgPath,newPath[0])
            InfoBar.success("保存图片","保存图片成功",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())


    def onClearBtnClicked(self):
        """ 点击清空按钮 """
        # 清空图片列表
        while self.hLisatLayout.count():
            item = self.hLisatLayout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def insertImage(self,imagePath:str):
        """ Insert image into image list """
        imageLabel = ImageItem(imagePath)
        self.hLisatLayout.addWidget(imageLabel)
        imageLabel.clicked.connect(lambda:self.onImageItemClicked(imagePath))
    def onImageItemClicked(self,imagePath):

        if imagePath==self.imgPath:
            return
        self.imgPath=imagePath
        self.onImageClicked.emit(imagePath)

        for i in range(self.hLisatLayout.count()):
            item = self.hLisatLayout.itemAt(i).widget()
            if item.path==imagePath:
                item.icon.show()
            else:
                item.icon.hide()

    def nextImage(self):
        """ 点击下一张按钮 """
        for i in range(self.hLisatLayout.count()):
            item = self.hLisatLayout.itemAt(i).widget()
            if item.path==self.imgPath:
                if i<self.hLisatLayout.count()-1:
                    nextItem=self.hLisatLayout.itemAt(i+1).widget()
                    self.onImageItemClicked(nextItem.path)
                    break

    
    def preImage(self):
        """ 点击上一张按钮 """
        for i in range(self.hLisatLayout.count()):
            item = self.hLisatLayout.itemAt(i).widget()
            if item.path==self.imgPath:
                if i>0:
                    preItem=self.hLisatLayout.itemAt(i-1).widget()
                    self.onImageItemClicked(preItem.path)
                    break

class ImageItem(CardWidget):
    def __init__(self, image: str, parent: QWidget = None):
        super().__init__(parent)
        self.vLayout = QVBoxLayout(self)
        self.path=image

        self.imgLabel = ImageLabel()
        self.pathLabel = BodyLabel()
        self.icon=InfoIconWidget(InfoBarIcon.SUCCESS)
        self.pathLabel.setAlignment(Qt.AlignCenter)
        self.pathLabel.setText(os.path.basename(image))   
        self.pathLabel.setWordWrap(True)
        self.pathLabel.setFixedHeight(20)

        self.imgLabel.setImage(image)
        self.imgLabel.setFixedSize(136, 136)
        self.imgLabel.scaledToWidth(136)

        self.vLayout.addWidget(self.imgLabel,0,Qt.AlignCenter)
        self.vLayout.addWidget(self.pathLabel,0,Qt.AlignCenter)
        self.vLayout.addWidget(self.icon,0,Qt.AlignCenter)
        self.vLayout.setContentsMargins(3, 3, 3, 3)
        self.vLayout.setSpacing(0)

        self.icon.hide()

class HorizontalScrollArea(ScrollArea):
    """ Horizontal scroll area """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidgetResizable(True)
        self.setContentsMargins(0, 0, 0, 0)
        self.setStyleSheet("background-color: transparent;")

# 平滑滚动相关
        self.animation = QPropertyAnimation(self.horizontalScrollBar(), b"value")
        self.animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        self.animation.setDuration(300)  # 动画持续时间300ms
        
    def wheelEvent(self, event):
        scroll_bar = self.horizontalScrollBar()
        
        # 如果正在动画，停止当前动画
        if self.animation.state() == QPropertyAnimation.State.Running:
            self.animation.stop()
        
        # 计算新的目标位置
        delta = event.angleDelta().y()
        if delta == 0:
            return
        
        # 设置滚动步长（可根据需要调整）
        step = delta * 0.5  # 减小滚动步长使滚动更平滑
        
        target_value = scroll_bar.value() - step
        
        # 确保不超出范围
        target_value = max(scroll_bar.minimum(), min(target_value, scroll_bar.maximum()))
        
        # 设置动画参数
        self.animation.setStartValue(scroll_bar.value())
        self.animation.setEndValue(int(target_value))
        self.animation.start()
        
        event.accept()
    