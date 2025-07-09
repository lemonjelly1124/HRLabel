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
        self.vLayout = QVBoxLayout()
        self.checkCard = CheckCard()
        self.parameterCard = ParameterCard()
        self.imageListCard = ImageListCard()

        self.vLayout.addWidget(self.checkCard)
        self.vLayout.addWidget(self.imageListCard)
        self.hLayout.addLayout(self.vLayout)
        self.hLayout.addWidget(self.parameterCard)
    
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
                # print("Output ", process_socket.outputJson)
                self.checkCard.setResult(process_socket.outputJson['result'])

                # with open('outputJson.json', 'w', encoding='utf-8') as json_file:
                    # json.dump(process_socket.outputJson, json_file, ensure_ascii=False, indent=4)
            else:
                print("Process execution failed or timed out.")
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            pass


    
    
    



