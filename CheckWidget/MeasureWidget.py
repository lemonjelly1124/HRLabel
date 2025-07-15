from PySide6.QtCore import Qt,Signal,QSize,QRectF,QPointF
from PySide6.QtGui import QImage,QPixmap,QFont,QPolygonF,QPainterPath,QColor
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QFileDialog,QWidget
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,HeaderCardWidget,SimpleCardWidget,ImageLabel,BodyLabel,setFont,
                            InfoBar,InfoBarPosition,PillPushButton,SwitchButton,DoubleSpinBox)
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

        self.setCCD3Visible(False)
        self.setVisible(not gData.isDebug)
    def __initWidget__(self):
        """初始化界面"""
        self.gLayout = QGridLayout()
        self.gLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(self.gLayout)
        self.gLayout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.gLayout.setSpacing(7)

        self.ccd3Lbl = BodyLabel("CCD3校验:")
        self.ccd3Switch = SwitchButton()
        self.camPixelLbl= BodyLabel("相机比例:")
        self.camPixelDsp = DoubleSpinBox()
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
        self.saveBtn=PrimaryPushButton("保存设置")

        self.ccd3Switch.setOnText("启用")
        self.ccd3Switch.setOffText("关闭")
        self.resultSwitch.setOnText("满足全部NG")
        self.resultSwitch.setOffText("满足一项NG")
        self.ccd3Switch.setChecked(False)
        self.camPixelDsp.setRange(0, 1)
        self.scoreDsp.setRange(0, 1)
        self.scoreDsp.setDecimals(2)
        self.minWDsp.setRange(0, 10)
        self.maxWDsp.setRange(0, 10)
        self.minHDsp.setRange(0, 10)
        self.maxHDsp.setRange(0, 10)
        self.minGrayDsp.setRange(0, 255)
        self.maxGrayDsp.setRange(0, 255)
        self.camPixelDsp.setDecimals(6)
        self.minWDsp.setDecimals(2)
        self.maxWDsp.setDecimals(2)
        self.minHDsp.setDecimals(2)
        self.maxHDsp.setDecimals(2)
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
        self.camPixelDsp.setSingleStep(0.000001)

        self.gLayout.addWidget(self.ccd3Lbl, 0, 0)
        self.gLayout.addWidget(self.ccd3Switch, 0, 1)
        self.gLayout.addWidget(self.camPixelLbl, 1, 0)
        self.gLayout.addWidget(self.camPixelDsp, 1, 1)
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
        self.gLayout.addWidget(self.saveBtn, 10, 0)


    def __initConnect__(self):
        """初始化连接"""
        self.saveBtn.clicked.connect(self.onSaveBtnClicked)
        self.ccd3Switch.checkedChanged.connect(self.setCCD3Visible)

    def onSaveBtnClicked(self):
        """保存设置按钮点击事件"""
        data = self.getMeasureData()
        gData.CCD3Measure = data
        gData.saveJson()


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
    
    def setCCD3Visible(self, visible: bool):
        """设置CCD3校验可见性"""
        self.camPixelLbl.setVisible(visible)
        self.camPixelDsp.setVisible(visible)
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
        self.saveBtn.setVisible(visible)

    def CCD3Measure(self,image:QImage,result:dict):
        item=result[0]
        if item['mask'] is not None:
            rect=item["rect"]
            boundW=rect['width']
            boundH=rect['height']
            if boundW> boundH:
                boundW, boundH = boundH, boundW

            rectF = QRectF(rect['x'], rect['y'], rect['width'], rect['height'])
            
            copyimg=image.copy(rectF.toRect())
            ndcopyimg= qimage_to_ndarray(copyimg)
            gray = np.mean(ndcopyimg)
            
            score=item["classScore"]
            if score < self.scoreDsp.value():
                return boundW, boundH, gray,score,[], False

            isWNG = False
            isHNG = False
            isGrayNG = False
            isNG= False
            ngArr=[]
            realW= boundW * self.camPixelDsp.value()*1000
            realH= boundH * self.camPixelDsp.value()*1000
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

            return realW, realH, gray,score,ngArr, isNG
        else:
            return None, None, None,None,[], False
