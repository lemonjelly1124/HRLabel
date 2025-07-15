from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,
                            InfoBar,InfoBarPosition,MessageBox)
from Database.DataOperate import DataOperate as DO
from Database.BaseModel import *
from .CheckCard import CheckCard
from .ParameterCard import ParameterCard
from .ImageListCard import ImageListCard
from HRVision.Controller.Process import Executor,Client,ProcessSocket
from HRVision.Controller.ProcessQt import ndarray_to_qimage,qimage_to_ndarray
from HRVision.utils.tools import delay_execute,async_run
from GlobalData import gData
import time
from .MeasureWidget import MeasureWidget
class CheckInterface(QWidget):
    """ Check Interface Widget """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CheckInterface")

        self.__initWidget__()
        self.__initConnect__()


        self.executor:Executor=None
        self.client:Client=None

    def __initWidget__(self):
        """ Initialize the widget layout """
        self.hLayout = QHBoxLayout(self)
        self.vLeftLayout = QVBoxLayout()
        self.vRightLayout = QVBoxLayout()
        self.checkCard = CheckCard()
        self.parameterCard = ParameterCard()
        self.measureWidget = MeasureWidget()
        self.imageListCard = ImageListCard()

        self.parameterCard.setFixedWidth(280)
        self.measureWidget.setFixedWidth(280)


        self.vLeftLayout.addWidget(self.checkCard)
        self.vLeftLayout.addWidget(self.imageListCard)
        self.vRightLayout.addWidget(self.parameterCard)
        self.vRightLayout.addWidget(self.measureWidget)

        self.hLayout.addLayout(self.vLeftLayout)
        self.hLayout.addLayout(self.vRightLayout)
    
    def __initConnect__(self):
        """ Initialize the connections """
        self.parameterCard.startBtn.clicked.connect(self.onStartBtnClicked)
        self.imageListCard.onImageClicked.connect(self.onImageClicked)
        self.parameterCard.stopBtn.clicked.connect(self.onStopBtnClicked)
        self.checkCard.leftBtn.clicked.connect(self.imageListCard.preImage)
        self.checkCard.rightBtn.clicked.connect(self.imageListCard.nextImage)


    def onStartBtnClicked(self):
        if self.parameterCard.enableLocatBtn.isChecked():
            if not self.parameterCard.identifyModelPath:
                InfoBar.warning("模型测试","请选择识别模型",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
                return 
            if not self.parameterCard.locatModelPath:
                InfoBar.warning("模型测试","请选择定位模型",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
                return 
        else:
            if not self.parameterCard.identifyModelPath:
                InfoBar.warning("模型测试","请选择识别模型",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
                return
        
        if not self.parameterCard.enableLocatBtn.isChecked():
            args = [self.parameterCard.identifyModelPath if item == '*weights' else item for item in gData.args]
        else:
            args = [self.parameterCard.identifyModelPath if item == '*weights' else item for item in gData.args1]
            args = [self.parameterCard.locatModelPath if item == '*weights1' else item for item in args]

        def start():
            print(args)
            self.executor = Executor(gData.url, args, gData.env, gData.ip, gData.port)
            self.client = self.executor.start()
        async_run(start)
        self.parameterCard.startBtn.setEnabled(False)
        self.parameterCard.stopBtn.setEnabled(True)
    
    def onStopBtnClicked(self):
        if self.executor:
             self.executor.stop()
            
        if self.client:
            self.client.stop()
        self.parameterCard.startBtn.setEnabled(True)
        self.parameterCard.stopBtn.setEnabled(False)
    
    def onImageClicked(self,path):
        process_socket = ProcessSocket(uid="unique_process_id")
        image = QImage(path)
        # process_socket.inputJson = {"param1": "value1", "param2": "value2"}
        ndimage=qimage_to_ndarray(image)
        process_socket.inputImage["image"] = ndimage

        try:
            self.checkCard.setImage(path)
            if self.client is None:
                InfoBar.warning("模型测试","模型未打开",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
                return 
            if not self.client.is_connected():
                InfoBar.warning("模型测试","模型打开失败",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
                return 
            success = self.client.execute(process_socket, timeOut=1000)

            if success:
                self.checkCard.setResult(process_socket.outputJson['result'])
                if self.measureWidget.ccd3Switch.isChecked():
                    w,h,gray,score,ngArr,isNg= self.measureWidget.CCD3Measure(image, process_socket.outputJson['result'])
                    print(f"宽度: {w}, 长度: {h}, 灰度: {gray}, 分数: {score}, NG项: {ngArr}, 是否NG: {isNg}")
                    self.checkCard.setGraphicsTextItem(w, h, gray, score, ngArr, isNg)
            else:
                InfoBar.error("模型测试","模型计算超时",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
        except Exception as e:
            InfoBar.error("模型测试",f"模型计算异常: {str(e)}",Qt.Horizontal,True,2500,InfoBarPosition.TOP,self.window())
        finally:
            pass


    
    
    



