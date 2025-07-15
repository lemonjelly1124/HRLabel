from PySide6.QtCore import Qt,Signal,QRectF,QPointF
from PySide6.QtGui import QImage,QColor,QCursor,QPainter,QFont
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget,QHBoxLayout,QSpacerItem,QSizePolicy,QListWidgetItem,QGraphicsItem,QGraphicsTextItem
import os,ast
from hrfluentwidgets import (GraphicsView,GraphicsRectItem,GraphicsItemScene,GraphicsPolygonItem)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from qfluentwidgets import ToggleButton,HeaderCardWidget,TransparentTogglePushButton,TransparentPushButton,RoundMenu, Action,ListWidget,BodyLabel,InfoBar,InfoBarPosition,PrimaryToolButton,SwitchButton
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
        
        self.outlineLbl=BodyLabel("显示轮廓")
        self.outlineBtn=SwitchButton()
        self.leftBtn=PrimaryToolButton(FIF.LEFT_ARROW)
        self.rightBtn=PrimaryToolButton(FIF.RIGHT_ARROW)

        self.outlineBtn.setOnText("显示")
        self.outlineBtn.setOffText("隐藏")
        self.outlineBtn.setChecked(True)

        self.vLayout=QVBoxLayout()
        self.hToolLayout=QHBoxLayout()
        self.hViewLayout=QHBoxLayout()

        self.hToolLayout.addWidget(self.leftBtn)
        self.hToolLayout.addWidget(self.outlineLbl)
        self.hToolLayout.addWidget(self.outlineBtn)
        self.hToolLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.hToolLayout.addWidget(self.rightBtn)
        self.hViewLayout.addWidget(self.graphicsView)

        self.vLayout.addLayout(self.hToolLayout)
        self.vLayout.addLayout(self.hViewLayout)
        self.viewLayout.addLayout(self.vLayout)

    def __initConnect__(self):
        """ Initialize the connections """
        self.leftBtn.clicked.connect(self.onLeftBtnClicked)
        self.rightBtn.clicked.connect(self.onRightBtnClicked)
        self.outlineBtn.checkedChanged.connect(self.onOutlineBtnClicked)

    def setGraphicsTextItem(self,w,h,gray,score,ngArr,isNg):
        sceneH= self.graphicsScene.height()
        size=sceneH/750
        self.ngItem=QGraphicsTextItem("NG")
        self.ngArrItem= QGraphicsTextItem("")
        self.wItem= QGraphicsTextItem("宽度:")
        self.hItem= QGraphicsTextItem("长度:")
        self.grayItem= QGraphicsTextItem("灰度:")
        self.scoreItem= QGraphicsTextItem("分数:")

        self.ngItem.setFont(QFont("Arial", size*20, QFont.Weight.Bold))
        self.ngItem.setPos(size*10, size*10)

        self.ngArrItem.setFont(QFont("Arial", size*16, QFont.Weight.Bold))
        self.ngArrItem.setPos(size*10, size*40)
        self.wItem.setFont(QFont("Arial", size*16, QFont.Weight.Bold))
        self.wItem.setPos(size*10, size*70)
        self.hItem.setFont(QFont("Arial", size*16, QFont.Weight.Bold))
        self.hItem.setPos(size*10, size*100)
        self.grayItem.setFont(QFont("Arial", size*16, QFont.Weight.Bold))
        self.grayItem.setPos(size*10, size*130)
        self.scoreItem.setFont(QFont("Arial", size*16, QFont.Weight.Bold))
        self.scoreItem.setPos(size*10, size*160)

        self.graphicsScene.addItem(self.ngItem)
        self.graphicsScene.addItem(self.ngArrItem)
        self.graphicsScene.addItem(self.wItem)
        self.graphicsScene.addItem(self.hItem)
        self.graphicsScene.addItem(self.grayItem)
        self.graphicsScene.addItem(self.scoreItem)

        if isNg:
            self.ngItem.setPlainText("NG")
            self.ngItem.setDefaultTextColor(QColor("#ff0000"))
        else:
            self.ngItem.setPlainText("OK")
            self.ngItem.setDefaultTextColor(QColor("#00ff00"))
        
        if ngArr is not None:
            ngStr=''
            for i in ngArr:
                ngStr+=i+","
            self.ngArrItem.setPlainText("NG项:"+ngStr[:-1])
            self.ngArrItem.setDefaultTextColor(QColor("#ff0000"))

        if w is not None:
            self.wItem.setPlainText(f"宽度: {w:.2f} um")
            self.wItem.setDefaultTextColor(QColor("#36e1ff"))
        else:
            self.wItem.setVisible(False)

        if h is not None:
            self.hItem.setPlainText(f"长度: {h:.2f} um")
            self.hItem.setDefaultTextColor(QColor("#36e1ff"))
        else:
            self.hItem.setVisible(False)
        
        if gray is not None:
            self.grayItem.setPlainText(f"灰度: {gray:.2f}")
            self.grayItem.setDefaultTextColor(QColor("#36e1ff"))
        else:
            self.grayItem.setVisible(False)

        if score is not None:
            self.scoreItem.setPlainText(f"分数: {score:.2f}")
            self.scoreItem.setDefaultTextColor(QColor("#36e1ff"))
        else:
            self.scoreItem.setVisible(False)

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

    def onOutlineBtnClicked(self, checked:bool):
        """ 点击轮廓按钮 """
        items= self.graphicsScene.items()
        for item in items:
            if isinstance(item, (GraphicsRectItem, GraphicsPolygonItem, ScoreRectItem, ScorePolygonItem)):
                item.setVisible(checked)
        self.graphicsScene.update()
    def setImage(self,path:str):
        """ Set the image for the card """
        self.graphicsScene.clearOthers()
        self.graphicsScene.setImage(QImage(path))
        self.graphicsView.fitInView(self.graphicsScene.imageItem(), Qt.KeepAspectRatio)
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
                rectItem.setVisible(self.outlineBtn.isChecked())
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
                polygon.setVisible(self.outlineBtn.isChecked())
    
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


        