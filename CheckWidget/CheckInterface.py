from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox)
from Database.DataOperate import DataOperate as DO
from Database.BaseModel import *

class CheckInterface(QWidget):
    """ Check Interface Widget """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("CheckInterface")

        self.__initWidget__()
        self.__initConnect__()

    def __initWidget__(self):
        """ Initialize the widget layout """
    
    def __initConnect__(self):
        """ Initialize the connections """

