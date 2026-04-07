from PySide6.QtCore import Qt,Signal,QSize,QRectF,QPointF
from PySide6.QtGui import QImage,QPixmap,QFont,QPolygonF,QPainterPath,QColor
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QFileDialog,QWidget,QFrame
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,HeaderCardWidget,SimpleCardWidget,ImageLabel,BodyLabel,setFont,
                            InfoBar,InfoBarPosition,PillPushButton,SwitchButton,DoubleSpinBox,ScrollArea,RoundMenu)
from Database.DataOperate import DataOperate as DO
from Database.BaseModel import *
from qfluentwidgets import FluentIcon as FIF
from GlobalData import gData
import numpy as np
import cv2
from HRVision.Controller.ProcessQt import qimage_to_ndarray
class MeasureWidget(HeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setObjectName("MeasureWidget")
        self.setTitle("规格设置")
        self.headerLayout.setContentsMargins(12,0,6,0)
        self.viewLayout.setContentsMargins(6,6,6,6)
        self.headerView.setFixedHeight(28)
        self.__initWidget__()
        self.__initConnect__()

        self.addLabelCheckItem("标签1","0")
        self.addLine()
        self.addLabelCheckItem("标签2","0")
        self.addLine()
        self.addLabelCheckItem("标签3","0")
        self.addLine()
        self.addLabelCheckItem("标签4","0")

    def __initWidget__(self):
        """初始化界面"""
        self.vViewLayout=QVBoxLayout()
        self.vViewLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(self.vViewLayout)


        self.scorllWidget = ScrollArea(self)
        self.scorllWidget.setStyleSheet("border: none; background: transparent;")
        self.scorllWidget.setWidgetResizable(True)
        self.vViewLayout.addWidget(self.scorllWidget)

        self.viewWidget= QWidget()
        self.vLayout = QVBoxLayout(self.viewWidget)
        self.vLayout.setContentsMargins(0, 0, 10, 0)
        self.vLayout.setAlignment(Qt.AlignTop)

        self.scorllWidget.setWidget(self.viewWidget)


        self.gLayout = QGridLayout()
        self.gLayout.setContentsMargins(0, 0, 0, 0)
        self.camPixelLbl= BodyLabel("相机比例:")
        self.camPixelDsp = DoubleSpinBox()
        self.ymalBtn = PushButton(FIF.DOCUMENT, "选择标签文件")

        self.camPixelLbl.setFixedWidth(60)
        self.camPixelDsp.setRange(0, 1)
        self.camPixelDsp.setDecimals(6)
        self.camPixelDsp.setSingleStep(0.000001)  # 设置最小步长为0.000001

        self.gLayout.addWidget(self.camPixelLbl, 0, 0)
        self.gLayout.addWidget(self.camPixelDsp, 0, 1)

        self.vViewLayout.insertLayout(0, self.gLayout)
        self.vViewLayout.insertWidget(1,self.ymalBtn,0,Qt.AlignLeft)
    
    def __initConnect__(self):
        """初始化连接"""
        self.ymalBtn.clicked.connect(self.onYAMLBtnClicked)

    def addLabelCheckItem(self,labelName:str,labelType:str=""):
        """添加标签校验项"""
        labelCheckItem = LabelCheckWidget(labelName,labelType)
        self.vLayout.addWidget(labelCheckItem)
        return labelCheckItem

    def addLine(self):
        """添加水平分割线"""
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFixedHeight(2)  # 设置线条高度
        line.setStyleSheet("background-color: #CCCCCC;")
        self.vLayout.addWidget(line)
    
    def onYAMLBtnClicked(self):
        """点击选择YAML文件"""
        fileName, _ = QFileDialog.getOpenFileName(self, "选择YAML文件", "", "YAML Files (*.yaml *.yml)")
        if fileName:
            labelNames = []
            with open(fileName, 'r', encoding='utf-8') as file:
                for line in file:
                    if line.strip().startswith('names:'):
                        names_str = line.split('names:', 1)[1].strip()
                        names = [name.strip('"\' ') for name in names_str.strip('[]').split(',')]
                        labelNames.extend(names)
                        break
            
            for i in reversed(range(self.vLayout.count())):
                item= self.vLayout.itemAt(i)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
                    widget.deleteLater()
            for i,labelName in enumerate(labelNames):
                self.addLabelCheckItem(labelName,str(i))
                self.addLine()

    def CheckResult(self, image:QImage,result: dict):
        checkedArr= []
        for resObj in result:
            className = resObj.get('className', '')
            classType = resObj.get('classType', '')
            for i in range(self.vLayout.count()):
                item = self.vLayout.itemAt(i).widget()
                
                if isinstance(item, LabelCheckWidget) and item.labelName == className:
                    realW, realH, gray,score,ngArr, isNG=item.LabelMeasure(image,resObj,self.camPixelDsp.value())
                    data={"realW": realW, "realH": realH, "gray": gray, "score": score, "ngArr": ngArr, "isNG": isNG}
                    resObj['data'] = data

            checkedArr.append(resObj)

        return checkedArr
class LabelCheckWidget(QWidget):
    def __init__(self,labelName:str,labelType:str,parent=None):
        super().__init__(parent)
        self.labelName = labelName
        self.labelType = labelType

        # print(f"LabelCheckWidget: {self.labelName}, {self.labelType}")

        self.__initWidget__()
        self.__initConnect__()

        self.setFixedWidth(250)
        self.setCheckVisible(False)

    def __initWidget__(self):
        """初始化界面"""
        self.gLayout = QGridLayout(self)
        self.gLayout.setContentsMargins(0, 0, 0, 0)
        self.gLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.gLayout.setSpacing(7)

        self.ccd3Lbl = BodyLabel(self.labelName)
        self.ccd3Switch = SwitchButton()
        self.resultLbl = BodyLabel("NG判定:")
        self.resultSwitch = SwitchButton()
        self.minWLbl = BodyLabel("宽度最小值:")
        self.minWDsp=DoubleSpinBox()
        self.maxWLbl = BodyLabel("宽度最大值:")
        self.maxWDsp=DoubleSpinBox()
        self.minHLbl = BodyLabel("长度最小值:")
        self.minHDsp=DoubleSpinBox()
        self.maxHLbl = BodyLabel("长度最大值:")
        self.maxHDsp=DoubleSpinBox()
        self.minGrayLbl = BodyLabel("灰度最小值:")
        self.minGrayDsp = DoubleSpinBox()
        self.maxGrayLbl = BodyLabel("灰度最大值:")
        self.maxGrayDsp = DoubleSpinBox()
        self.scoreLbl = BodyLabel("分数:")
        self.scoreDsp = DoubleSpinBox()

        self.ccd3Switch.setOnText("启用")
        self.ccd3Switch.setOffText("关闭")
        self.resultSwitch.setOnText("满足全部NG")
        self.resultSwitch.setOffText("满足一项NG")
        self.ccd3Switch.setChecked(False)
        self.scoreDsp.setRange(0, 1)
        self.scoreDsp.setDecimals(2)
        self.minWDsp.setRange(0, 10)
        self.maxWDsp.setRange(0, 10)
        self.minHDsp.setRange(0, 10)
        self.maxHDsp.setRange(0, 10)
        self.minGrayDsp.setRange(0, 255)
        self.maxGrayDsp.setRange(0, 255)
        self.minWDsp.setDecimals(5)
        self.maxWDsp.setDecimals(5)
        self.minHDsp.setDecimals(5)
        self.maxHDsp.setDecimals(5)

        self.minWDsp.hBoxLayout.setSpacing(0)
        self.maxWDsp.hBoxLayout.setSpacing(0)
        self.minHDsp.hBoxLayout.setSpacing(0)
        self.maxHDsp.hBoxLayout.setSpacing(0)
        self.minGrayDsp.setDecimals(0)
        self.maxGrayDsp.setDecimals(0)
        self.minWDsp.setSuffix("mm")
        self.maxWDsp.setSuffix("mm")
        self.minHDsp.setSuffix("mm")
        self.maxHDsp.setSuffix("mm")
        self.minGrayDsp.setSuffix("灰度")
        self.maxGrayDsp.setSuffix("灰度")
        self.minWDsp.setSingleStep(0.1)
        self.maxWDsp.setSingleStep(0.1)
        self.minHDsp.setSingleStep(0.1)
        self.maxHDsp.setSingleStep(0.1)
        self.minGrayDsp.setSingleStep(1)
        self.maxGrayDsp.setSingleStep(1)
        self.scoreDsp.setSingleStep(0.01)

        self.gLayout.addWidget(self.ccd3Lbl, 0, 0)
        self.gLayout.addWidget(self.ccd3Switch, 0, 1)
        self.gLayout.addWidget(self.minWLbl, 2, 0)
        self.gLayout.addWidget(self.minWDsp, 2, 1)
        self.gLayout.addWidget(self.maxWLbl, 3, 0)
        self.gLayout.addWidget(self.maxWDsp, 3, 1)
        self.gLayout.addWidget(self.minHLbl, 4, 0)
        self.gLayout.addWidget(self.minHDsp, 4, 1)
        self.gLayout.addWidget(self.maxHLbl, 5, 0)
        self.gLayout.addWidget(self.maxHDsp, 5, 1)
        self.gLayout.addWidget(self.minGrayLbl, 6, 0)
        self.gLayout.addWidget(self.minGrayDsp, 6, 1)
        self.gLayout.addWidget(self.maxGrayLbl, 7, 0)
        self.gLayout.addWidget(self.maxGrayDsp, 7, 1)
        self.gLayout.addWidget(self.scoreLbl, 8, 0)
        self.gLayout.addWidget(self.scoreDsp, 8, 1)
        self.gLayout.addWidget(self.resultLbl, 9, 0)
        self.gLayout.addWidget(self.resultSwitch, 9, 1)

    def __initConnect__(self):
        """初始化连接"""
        self.ccd3Switch.checkedChanged.connect(self.setCheckVisible)

    def setCheckVisible(self, visible: bool):
        """设置CCD3校验可见性"""
        self.minWLbl.setVisible(visible)
        self.minWDsp.setVisible(visible)
        self.maxWLbl.setVisible(visible)
        self.maxWDsp.setVisible(visible)
        self.minHLbl.setVisible(visible)
        self.minHDsp.setVisible(visible)
        self.maxHLbl.setVisible(visible)
        self.maxHDsp.setVisible(visible)
        self.minGrayLbl.setVisible(visible)
        self.minGrayDsp.setVisible(visible)
        self.maxGrayLbl.setVisible(visible)
        self.maxGrayDsp.setVisible(visible)
        self.resultLbl.setVisible(visible)
        self.resultSwitch.setVisible(visible)
        self.scoreLbl.setVisible(visible)
        self.scoreDsp.setVisible(visible)
    
    def getMeasureData(self):
        """获取测量数据"""
        data = {
            'minW': self.minWDsp.value(),
            'maxW': self.maxWDsp.value(),
            'minH': self.minHDsp.value(),
            'maxH': self.maxHDsp.value(),
            'minGray': self.minGrayDsp.value(),
            'maxGray': self.maxGrayDsp.value(),
            'camPixel': self.camPixelDsp.value(),
            'score': self.scoreDsp.value(),
            'isNGAll': self.resultSwitch.isChecked()
        }
        return data
    
    def setMeasureData(self,):
        """设置测量数据"""
        data=gData.CCD3Measure
        self.ccd3MeasureData = data
        self.minWDsp.setValue(data.get('minW',0))
        self.maxWDsp.setValue(data.get('maxW',0))
        self.minHDsp.setValue(data.get('minH',0))
        self.maxHDsp.setValue(data.get('maxH',0))
        self.minGrayDsp.setValue(data.get('minGray',0))
        self.maxGrayDsp.setValue(data.get('maxGray',0))
        self.camPixelDsp.setValue(data.get('camPixel',0))
        self.scoreDsp.setValue(data.get('score',0.0))
        self.resultSwitch.setChecked(data.get('isNGAll',False))
    
    def LabelMeasure(self,image:QImage,resultObj:dict,camPixel:float):
        rect= resultObj['rect']
        rectF = QRectF(rect['x'], rect['y'], rect['width'], rect['height'])
        if resultObj['mask'] is not None:
            # 获取最小外接旋转矩形
            points=[]
            for point in resultObj['mask']:
                points.append([point[0],point[1]])
            np_points = np.array(points, dtype=np.float32)
            rectmin = cv2.minAreaRect(np_points)
            center, (boundW, boundH), angle = rectmin
        elif resultObj['mask'] is None:
            boundW=rect['width']
            boundH=rect['height']

        if boundW > boundH:
                boundW, boundH = boundH, boundW

        copyimg=image.copy(rectF.toRect())
        ndcopyimg= qimage_to_ndarray(copyimg)
        gray = np.mean(ndcopyimg)
        
        score=resultObj["classScore"]
        if score < self.scoreDsp.value():
            return boundW, boundH, gray,score,[], False

        isWNG = False
        isHNG = False
        isGrayNG = False
        isNG= False
        ngArr=[]
        realW= boundW * camPixel
        realH= boundH * camPixel
        if realW < self.minWDsp.value() or realW > self.maxWDsp.value():
            isWNG = True
            ngArr.append("宽度")
        if realH < self.minHDsp.value() or realH > self.maxHDsp.value():
            isHNG = True
            ngArr.append("长度")
        if gray < self.minGrayDsp.value() or gray > self.maxGrayDsp.value():
            isGrayNG = True
            ngArr.append("灰度")
        
        if self.resultSwitch.isChecked():
            isNG = isWNG and isHNG and isGrayNG
        else:
            isNG = isWNG or isHNG or isGrayNG

        if self.ccd3Switch.isChecked() == False:
            isNG = False

        return realW, realH, gray,score,ngArr, isNG

