from PySide6.QtCore import Qt,Signal,QSize
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox)
from Database.DataOperate import DataOperate as DO
from .ProjectDialog import ProjectDialog
from .ProjectCard import ProjectCard
from Database.BaseModel import *


class DataInterface(QWidget):
    """ Data Interface Widget """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataInterface")

        self.__initWidget__()
        self.__initConnect__()
        self.QueryProject(None)
    def __initWidget__(self):
        """ Initialize the widget layout """

        self.hLayout = QHBoxLayout(self)
        """左侧项目列表布局"""
        self.leftWidget=SimpleCardWidget()
        self.vLeftLayout = QVBoxLayout(self.leftWidget)
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

        self.leftWidget.setFixedWidth(250)
        self.hLayout.addWidget(self.leftWidget)
        """左侧项目列表布局"""

        """右侧数据集布局"""
        cardWdg=QWidget()
        vCardLayout = QVBoxLayout(cardWdg)
        vCardLayout.setContentsMargins(0, 0, 0, 0)
        self.projectCard = ProjectCard()
        vCardLayout.addWidget(self.projectCard)
        self.hLayout.addWidget(cardWdg)

        """右侧数据集布局"""
    def onAddProjectBtnClicked(self):
        """点击按钮添加新项目"""
        dialog= ProjectDialog(self)
        if dialog.exec():
            project= Project()
            project.name= dialog.lineName.text()
            project.description= dialog.lineDesc.text()

            projectRes=DO.insert_project(project)
            if projectRes.id is not None:
                InfoBar.success( "添加项目成功", "添加项目完成",orient=Qt.Horizontal, isClosable=True, duration=3000,position=InfoBarPosition.TOP,parent=self)
                self.addProjectItem(project.name, projectRes.id)
            else:
                InfoBar.warning("添加项目失败", "添加项目异常", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)

    def onProjectItemClicked(self,projectID):
        """点击项目item刷新右侧详情页"""
        projects = DO.query_project(id=projectID)
        self.projectCard.setProject(projects[0])
        self.projectCard.show()

    def onProjectEdited(self,id:int,name:str):
        """项目修改时通知列表修改"""
        for i in range(self.projectListWidget.count()):
            item = self.projectListWidget.item(i)
            projectItem:ProjectItem = self.projectListWidget.itemWidget(item)
            if projectItem.id == id:
                projectItem.nameLbl.setText(name)
                break    
    def onProjectDeleted(self, id: int):
        dlg= MessageBox("删除项目","是否确认删除该项目?\n"+self.projectCard.titleLbl.text(),parent=self)
        if dlg.exec() != MessageBox.Accepted:
            return
        affected_rows=DO.delete_project(id=id)
        """项目删除时通知列表删除"""
        for i in range(self.projectListWidget.count()):
            item = self.projectListWidget.item(i)
            projectItem:ProjectItem = self.projectListWidget.itemWidget(item)
            if projectItem.id == id:
                self.projectListWidget.takeItem(i)
                self.projectCard.hide()
                break    

    def __initConnect__(self):
        """ Initialize the connections for signals and slots """
        self.addBtn.clicked.connect(self.onAddProjectBtnClicked)
        self.projectCard.onProjectEdited.connect(self.onProjectEdited)
        self.projectCard.deleteBtn.clicked.connect(lambda: self.onProjectDeleted(self.projectCard.projectID))

    def addProjectItem(self, name: str, id: str):
        """ Add a project item to the project list """
        listItem= QListWidgetItem()
        projectItem= ProjectItem(name, id, self)
        projectItem.onItemClicked.connect(self.onProjectItemClicked)
        listItem.setSizeHint(projectItem.sizeHint())  # Set height to 60px
        self.projectListWidget.addItem(listItem)
        self.projectListWidget.setItemWidget(listItem,projectItem)

    def QueryProject(self, key: str):
        """ Query a project by its ID """
        projects = DO.query_project(key=key)
        for project in projects:
            self.addProjectItem(project.name, project.id)

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
    

    

        