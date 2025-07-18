from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox)
from Database.DataOperate import DataOperate as DO
from .ProjectDialog import ProjectDialog
from .ProjectCard import ProjectCard
from Database.BaseModel import *

class ProjectListCard(SimpleCardWidget):
    """ Project List Card Widget """
    projectItemClicked=Signal(int)
    hideProjectCard=Signal()
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vLeftLayout = QVBoxLayout(self)
        self.topHLayout = QHBoxLayout()
        self.searchLineEdit = LineEdit()
        self.addBtn = ToolButton(FluentIcon.ADD)
        self.projectListWidget = ListWidget()
        self.searchLineEdit.setPlaceholderText("搜索项目")

        self.topHLayout.addWidget(self.searchLineEdit)
        self.topHLayout.addWidget(self.addBtn)
        self.topHLayout.setContentsMargins(5, 5, 5, 0)
        self.vLeftLayout.addLayout(self.topHLayout)
        self.vLeftLayout.addWidget(self.projectListWidget)
        self.vLeftLayout.setContentsMargins(3,3,3,3)

        self.setFixedWidth(250)

        self.addBtn.clicked.connect(self.onAddProjectBtnClicked)
        self.QueryProject(None)

        self.searchLineEdit.textChanged.connect(self.onSearchTextChanged)


    def addProjectItem(self, name: str, id: str):
        """ Add a project item to the project list """
        listItem= QListWidgetItem()
        projectItem= ProjectItem(name, id, self)
        projectItem.onItemClicked.connect(self.projectItemClicked)
        listItem.setSizeHint(projectItem.sizeHint())  # Set height to 60px
        self.projectListWidget.addItem(listItem)
        self.projectListWidget.setItemWidget(listItem,projectItem)

    def QueryProject(self, key: str):
        """ Query a project by its ID """
        while self.projectListWidget.count() > 0:
            item = self.projectListWidget.takeItem(0)
            del item
        if( key is None) or (key.strip() == ""):
            projects = DO.query_project()
        else:
            projects = DO.query_project(name=key)
        for project in projects:
            self.addProjectItem(project.name, project.id)
    
    def onProjectEdited(self,id:int,name:str):
        """项目修改时通知列表修改"""
        for i in range(self.projectListWidget.count()):
            item = self.projectListWidget.item(i)
            projectItem:ProjectItem = self.projectListWidget.itemWidget(item)
            if projectItem.id == id:
                projectItem.nameLbl.setText(name)
                break    
    def onProjectDeleted(self, id: int):
        """项目删除时通知列表删除"""
        for i in range(self.projectListWidget.count()):
            item = self.projectListWidget.item(i)
            projectItem:ProjectItem = self.projectListWidget.itemWidget(item)
            if projectItem.id == id:
                self.projectListWidget.takeItem(i)
                self.hideProjectCard.emit()
                break    
    
    def onAddProjectBtnClicked(self):
        dialog= ProjectDialog(self.window())
        if dialog.exec():
            project= Project()
            project.name= dialog.lineName.text()
            project.description= dialog.lineDesc.text()

            projectRes=DO.insert_project(project)
            if projectRes.id is not None:
                InfoBar.success( "添加项目成功", "添加项目完成",orient=Qt.Horizontal, isClosable=True, duration=3000,position=InfoBarPosition.TOP,parent=self.window())
                self.addProjectItem(project.name, projectRes.id)
            else:
                InfoBar.warning("添加项目失败", "添加项目异常", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self.window())
    
    def onSearchTextChanged(self, text: str):
        """ Search project by name """
        if text.strip() == "":
            self.QueryProject(None)
        else:
            self.QueryProject(text.strip())


class ProjectItem(QWidget):
    """ Project Item Widget """
    onItemClicked=Signal(int)
    def __init__(self,name:str,id:str,parent=None):
        super().__init__(parent)
        self.setObjectName("ProjectItem")

        self.name = name
        self.id = id
        self.__initWidget__()

    def __initWidget__(self):
        self.hLayout = QHBoxLayout(self)
        self.iconLbl= ImageLabel("hr.svg")
        self.nameLbl = BodyLabel(self.name)
        self.iconLbl.setFixedSize(50, 50)

        self.hLayout.addWidget(self.iconLbl)
        self.hLayout.addWidget(self.nameLbl)
        self.hLayout.setContentsMargins(5,5,5,5)
    
    def mousePressEvent(self, event):
        """Handle mouse press event"""
        if event.button() == Qt.LeftButton:
            self.onItemClicked.emit(self.id)
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        return super().mouseMoveEvent(event)
    