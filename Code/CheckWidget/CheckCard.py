from PySide6.QtCore import Qt,Signal,QRectF,QPointF
from PySide6.QtGui import QImage,QColor,QCursor,QPainter,QFont
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget,QHBoxLayout,QSpacerItem,QSizePolicy,QListWidgetItem,QGraphicsItem
import os,ast
from hrfluentwidgets import (GraphicsView,GraphicsRectItem,GraphicsItemScene,GraphicsPolygonItem,GraphicsCaliperRectItem,GraphicsRotatedRectItem,GraphicsCaliperRotatedRectItem)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from qfluentwidgets import ToggleButton,HeaderCardWidget,TransparentTogglePushButton,TransparentPushButton,RoundMenu, Action,ListWidget,BodyLabel,InfoBar,InfoBarPosition,PrimaryToolButton
from qfluentwidgets import FluentIcon as FIF
from HRVision.utils.tools import delay_execute
class CheckCard(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CheckCard")
        self.setTitle("模型校验")
        self.headerLayout.setContentsMargins(12,0,6,0)
        self.viewLayout.setContentsMargins(0,0,0,0)
        self.headerView.setFixedHeight(28)
        self.__initWidget__()
        self.__initConnect__()
    
    def __initWidget__(self):
        """ Initialize the widget layout """
        self.graphicsView=GraphicsView(self)
        self.graphicsScene=GraphicsItemScene(self.graphicsView)
        self.graphicsView.setScene(self.graphicsScene)
        self.graphicsView.setDragMode(GraphicsView.ScrollHandDrag)

        self.leftBtn=PrimaryToolButton(FIF.LEFT_ARROW)
        self.rightBtn=PrimaryToolButton(FIF.RIGHT_ARROW)

        self.leftBtn.setFixedHeight(80)
        self.rightBtn.setFixedHeight(80)

        self.viewLayout.addWidget(self.leftBtn)
        self.viewLayout.addWidget(self.graphicsView)
        self.viewLayout.addWidget(self.rightBtn)
    def __initConnect__(self):
        """ Initialize the connections """
        self.leftBtn.clicked.connect(self.onLeftBtnClicked)
        self.rightBtn.clicked.connect(self.onRightBtnClicked)

    def onLeftBtnClicked(self):
        """ 点击左按钮 """
        self.leftBtn.setEnabled(False)
        def leftBtnEnable():
            self.leftBtn.setEnabled(True)
        delay_execute(leftBtnEnable,0.5)

    def onRightBtnClicked(self):
        """ 点击右按钮 """
        self.rightBtn.setEnabled(False)

        def btnEnable():
            self.rightBtn.setEnabled(True)
        delay_execute(btnEnable,0.5)

    def setImage(self,path:str):
        """ Set the image for the card """
        self.graphicsScene.clearOthers()
        self.graphicsScene.setImage(QImage(path))
    def setResult(self,result):
        """ Set the result for the card """
        for item in result:
            if 'mask' in item and item['mask'] is None:
                rect=item["rect"]
                rectItem=ScoreRectItem()
     
                rectItem.setRect(QRectF(rect['x'],rect['y'],rect['width'],rect['height']))
                rectItem.setScore(item["classScore"])
                rectItem.className=item["className"]
                self.graphicsScene.addItem(rectItem)
                # print(rectItem.isSelected())
            elif item['mask'] is not None:
                rect=item["rect"]
                polygon=ScorePolygonItem()
                polygon.boundRect=QRectF(rect['x'],rect['y'],rect['width'],rect['height'])
                points=[]
                for point in item['mask']:
                    points.append(QPointF(point[0],point[1]))
                polygon.setPolygon(points)
                polygon.setScore(item["classScore"])
                self.className=item["className"]
                self.graphicsScene.addItem(polygon)
    
class ScoreRectItem(GraphicsRectItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)
        self.setAcceptHoverEvents(False)
        self.score=0
        self.className=""

    def mousePressEvent(self, event):
        pass

    def setScore(self,score):
        self.score=score
    
    def paint(self, painter:QPainter, option, widget=None):
        painter.save()
        pen=painter.pen()
        pen.setColor(self.penColor)
        pen.setWidth(2)
        painter.setPen(pen)

        scoreRect=QRectF(self.rect().x(),self.rect().y()-35,70,35)
        painter.fillRect(scoreRect,self.penColor)
        painter.drawRect(scoreRect)

        nameW=len(self.className)*28+10
        nameRect=QRectF(self.rect().x()+70,self.rect().y()-35,nameW,35)
        painter.fillRect(nameRect,self.penColor)
        painter.drawRect(nameRect)

        pen.setColor("white")
        painter.setPen(pen)
        font=painter.font()
        font.setPixelSize(28)
        font.setWeight(QFont.Weight.ExtraBold)
        
        painter.setFont(font)
        painter.drawText(scoreRect,Qt.AlignCenter,f"{self.score:.2f}")
        painter.drawText(nameRect,Qt.AlignCenter,self.className)

        super().paint(painter, option, widget)
        painter.restore()

class ScorePolygonItem(GraphicsPolygonItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsScenePositionChanges, False)
        self.setAcceptHoverEvents(False)
        self.score=0

        self.boundRect=QRectF()
        self.className=""

    def mousePressEvent(self, event):
        pass

    def setScore(self,score):
        self.score=score
    
    
    def paint(self, painter, option, widget=None):
        painter.save()
        pen=painter.pen()
        pen.setColor(self.penColor)
        pen.setWidth(2)
        painter.setPen(pen)

        scoreRect=QRectF(self.boundRect.topLeft().x(),self.boundRect.topLeft().y()-35,70,35)
        painter.fillRect(scoreRect,self.penColor)
        painter.drawRect(scoreRect)

        nameW=len(self.className)*28+10
        nameRect=QRectF(self.boundRect.x()+70,self.boundRect.y()-35,nameW,35)
        painter.fillRect(nameRect,self.penColor)
        painter.drawRect(nameRect)

        pen.setColor("white")
        painter.setPen(pen)
        font=painter.font()
        font.setPixelSize(28)
        font.setWeight(QFont.Weight.ExtraBold)
        painter.setFont(font)
        painter.drawText(scoreRect,Qt.AlignCenter,f"{self.score:.2f}")
        painter.drawText(nameRect,Qt.AlignCenter,self.className)

        super().paint(painter, option, widget)
        painter.restore()


        