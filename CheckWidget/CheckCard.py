from PySide6.QtCore import Qt,Signal,QRectF,QPointF
from PySide6.QtGui import QImage,QColor,QCursor
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget,QHBoxLayout,QSpacerItem,QSizePolicy,QListWidgetItem,QGraphicsItem
import os,ast
from hrfluentwidgets import (GraphicsView,GraphicsRectItem,GraphicsItemScene,GraphicsPolygonItem,GraphicsCaliperRectItem,GraphicsRotatedRectItem,GraphicsCaliperRotatedRectItem)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from qfluentwidgets import ToggleButton,HeaderCardWidget,TransparentTogglePushButton,TransparentPushButton,RoundMenu, Action,ListWidget,BodyLabel,InfoBar,InfoBarPosition
from qfluentwidgets import FluentIcon as FIF

class CheckCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CheckCard")
        self.setTitle("检查卡")
        
        self.__initWidget__()
        self.__initConnect__()
    
    def __initWidget__(self):
        """ Initialize the widget layout """
    
    def __initConnect__(self):
        """ Initialize the connections """

    def setCheckData(self, checkData):
        """ Set the check data for the card """
        self.checkData = checkData
        self.setTitle(f"检查卡 - {checkData.name}")
        self.setDescription(checkData.description)
        # Additional setup can be done here, such as populating data into the cardq
        