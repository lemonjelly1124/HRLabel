from PySide6.QtCore import Qt,Signal
from PySide6.QtGui import QImage,QPixmap,QFont,QColor
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QSpacerItem,QSizePolicy
from qfluentwidgets import (PushButton,PrimaryPushButton,TransparentTogglePushButton,FluentIcon,LineEdit,ToolButton,TransparentToolButton,TransparentPushButton,ListWidget,HeaderCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ColorPickerButton)
from hrfluentwidgets import GraphicsView,GraphicsRectItem,GraphicsItemScene,GraphicsPolygonItem,GraphicsCaliperRectItem
from LabelWidget.LabelCard import LabelCard,LabelItem
from LabelWidget.ImageCard import ImageCard
from LabelWidget.GraphicsCard import GraphicsCard
class LabelInterface(QWidget):
    """ Label Interface Widget """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("LabelInterface")

        self.__initWidget__()
        self.__initConnect__()

        self.datasetID = None
    
    def __initWidget__(self):
        """ Initialize the widget layout """
        self.hLayout = QHBoxLayout(self)
        self.vRightLayout = QVBoxLayout()


        """左侧Graphics布局"""
        self.graphCard=GraphicsCard()
        self.hLayout.addWidget(self.graphCard)
        '''左侧Graphics布局'''

        """右上标签列表布局"""
        self.labelCard = LabelCard()
        self.vRightLayout.addWidget(self.labelCard)
        '''右上标签列表布局'''

        """右下图片列表布局"""
        self.imageCard = ImageCard()
        self.vRightLayout.addWidget(self.imageCard)
        '''右下图片列表布局'''
        self.vRightLayout.setStretch(0, 1)
        self.vRightLayout.setStretch(1, 2)
        self.hLayout.addLayout(self.vRightLayout)

        
    def __initConnect__(self):
        self.labelCard.onLabelColorChanged.connect(self.graphCard.onLabelColorChanged)
        self.imageCard.onImageClicked.connect(self.graphCard.setImage)

        self.graphCard.onNextImage.connect(self.imageCard.onNextImage)
        self.graphCard.onPrevImage.connect(self.imageCard.onPrevImage)
        self.graphCard.onSaveImageLabel.connect(self.imageCard.refreshImageStatus)
        self.graphCard.onDeleteImage.connect(self.imageCard.deleteImageItem)

    def setDataset(self, datasetID):
        """ 设置当前数据集 """
        self.datasetID = datasetID
        self.imageCard.setImageList(datasetID)
        self.labelCard.setLabelList(datasetID)
        self.graphCard.setDataset(datasetID)


        