
from PySide6.QtCore import Qt,Signal,QRectF,QPointF,QTimer
from PySide6.QtGui import QImage,QColor,QCursor
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget,QHBoxLayout,QSpacerItem,QSizePolicy,QListWidgetItem,QGraphicsItem,QGraphicsRectItem
import os,ast
from hrfluentwidgets import (GraphicsView,GraphicsRectItem,GraphicsItemScene,GraphicsPolygonItem,GraphicsCaliperRectItem,GraphicsRotatedRectItem,GraphicsCaliperRotatedRectItem)
from Database.BaseModel import *
from Database.DataOperate import DataOperate as DO
from qfluentwidgets import ToggleButton,HeaderCardWidget,TransparentTogglePushButton,TransparentPushButton,RoundMenu, Action,ListWidget,BodyLabel,InfoBar,InfoBarPosition
from qfluentwidgets import FluentIcon as FIF

class GraphicsCard(HeaderCardWidget):
    onNextImage= Signal(int)
    onPrevImage = Signal(int)
    onSaveImageLabel = Signal(int)
    onDeleteImage = Signal(int)

    def __init__(self,parent=None):
        super().__init__()
        self.setWindowTitle("GraphicsView GraphicsCard")
        self.setTitle("图片标注")
        vLayout = QVBoxLayout()
        vLayout.setContentsMargins(0, 0, 0, 0)
        self.viewLayout.addLayout(vLayout)
        self.viewLayout.setContentsMargins(6, 0, 6, 0)
        self.headerView.setFixedHeight(28)

        '''ToolBar'''
        self.hToolLayout = QHBoxLayout()
        self.addRectBtn = TransparentTogglePushButton(FIF.ADD, "添加矩形")
        self.addPolygonBtn = TransparentTogglePushButton(FIF.ADD, "添加多边形")
        self.deleteBtn=TransparentPushButton(FIF.DELETE,"删除图片")
        self.zoomInBtn = TransparentPushButton(FIF.ZOOM_IN,"放大")
        self.zoomOutBtn = TransparentPushButton(FIF.ZOOM_OUT,"缩小")
        self.fitBtn= TransparentPushButton(FIF.FIT_PAGE,"自适应")
        self.moveBtn = TransparentTogglePushButton(FIF.MOVE,"移动视图")
        self.clearBtn=TransparentPushButton(FIF.ERASE_TOOL,"清除标注")
        self.saveBtn=TransparentPushButton(FIF.SAVE,"保存标注")

        self.hToolLayout.addWidget(self.addRectBtn)
        self.hToolLayout.addWidget(self.addPolygonBtn)
        self.hToolLayout.addWidget(self.deleteBtn)
        self.hToolLayout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.hToolLayout.addWidget(self.zoomInBtn)
        self.hToolLayout.addWidget(self.zoomOutBtn)
        self.hToolLayout.addWidget(self.fitBtn)
        self.hToolLayout.addWidget(self.moveBtn)
        self.hToolLayout.addWidget(self.clearBtn)
        self.hToolLayout.addWidget(self.saveBtn)
        """ToolBar"""

        self.addRectBtn.clicked.connect(self.onRectBtnClicked)
        self.addPolygonBtn.clicked.connect(self.onPolygonBtnClicked)

        self.graphicsview = GraphicsView(self)
        vLayout.addLayout(self.hToolLayout)
        vLayout.addWidget(self.graphicsview)

        self.scene = GraphicsItemScene(self)
        self.graphicsview.setScene(self.scene)

        self.scene.setContinueEditMode(True)
        self.scene.itemFinished.connect(self.onItemFinished)
        self.scene.itemRemoved.connect(self.onItemRemoved)

        self.currImgID = None  # 当前选中的图片ID
        self.datasetID = None  # 当前数据集ID

        self.__connect__()

        # self.scene.setImage(QImage("D:\\AIProgram\\dataset\\熔接痕\\images\\00-00-02-022_0.jpg"))
        # polygonStr="0.396952 0.380509 0.423262 0.416685 0.466016 0.428744 0.485749 0.463824 0.52631 0.518636 0.53508 0.539465 0.584411 0.581123 0.618395 0.608529 0.604144 0.619491 0.576738 0.601951 0.550428 0.573449 0.520829 0.538369 0.496711 0.506578 0.469305 0.471497 0.455054 0.450669 0.452861 0.444091 0.424359 0.434225 0.395856 0.4123 0.381605 0.395856"
        # polygonPoints=[]
        # for i in range(0,len(polygonStr.split()),2):
        #     point=QPointF(float(polygonStr.split()[i]),float(polygonStr.split()[i+1]))
        #     polygonPoints.append(QPointF(point.x()*640,point.y()*640))
        # self.scene.addItem(GraphicsPolygonItem(polygonPoints))

        # self.scene.setImage(QImage("D:\\AIProgram\\dataset\\项目1_split\\images\\1_1.jpg"))
        # rectStr="0.5 0.5 0.161868 0.167976"
        # rectParts=rectStr.split()
        # center=QPointF(float(rectParts[0])*640,float(rectParts[1])*640)
        # rect=QRectF(center.x()-float(rectParts[2])*640/2,center.y()-float(rectParts[3])*640/2,float(rectParts[2])*640,float(rectParts[3])*640)
        # self.scene.addItem(GraphicsRectItem(rect))

        # self.scene.setImage(QImage("D:\\AIProgram\\dataset\\模穴001\\images\\19-14-37-3737.bmp"))
        # rectStr="0.265738 0.192293 0.038133 0.017093"
        # rectParts=rectStr.split()
        # center=QPointF(float(rectParts[0])*2448,float(rectParts[1])*2048)
        # rect=QRectF(center.x()-float(rectParts[2])*2448/2,center.y()-float(rectParts[3])*2048/2,float(rectParts[2])*2448,float(rectParts[3])*2048)
        # self.scene.addItem(GraphicsRectItem(rect))
    
    def __connect__(self):
        self.zoomInBtn.clicked.connect(self.zoomIn)
        self.zoomOutBtn.clicked.connect(self.zoomOut)
        self.fitBtn.clicked.connect(self.fitImage)
        self.moveBtn.clicked.connect(self.enableImageDrag)
        self.clearBtn.clicked.connect(self.clearLabels)
        self.saveBtn.clicked.connect(self.saveImageLabel)
        self.deleteBtn.clicked.connect(self.deleteCurrImage)

    def onItemRemoved(self, item: QGraphicsItem):
        self.scene.tempItem=None

    def onItemFinished(self,item):
        # if isinstance(item, LabelPolygonItem):
        #     print("多边形区域：", item.polygon())
        # elif isinstance(item, LabelRectItem):
        #     print("矩形区域：", item.rect())
        item.isContinueEdit.connect(self.onItemHoverLeave)
        item.datasetID = self.datasetID  # 设置数据集ID以获取标签列表

        menu=LabelMenu(title="标签列表",dataset_id=self.datasetID)
        menu.showMenu(QCursor.pos())  # 显示菜单在鼠标位置
        menu.labelItemClicked.connect(item.setLabel)
        menu.cancelled.connect(item.onMenuHide)  # 菜单隐藏时恢复编辑状态
    

    def onRectBtnClicked(self):
        if not self.moveBtn.isChecked():
            self.scene.setEditMode(self.addRectBtn.isChecked())
        self.scene.addItemFunc = lambda: LabelRectItem()
        self.addPolygonBtn.setChecked(False)

    def onPolygonBtnClicked(self):
        if not self.moveBtn.isChecked():
            self.scene.setEditMode(self.addPolygonBtn.isChecked())
        self.scene.addItemFunc = lambda: LabelPolygonItem()
        self.addRectBtn.setChecked(False)

    def onItemHoverLeave(self,isEdit:bool):
        if (self.addRectBtn.isChecked() or self.addPolygonBtn.isChecked()) and isEdit:
            self.scene.setEditMode(True)
        else:
            self.scene.setEditMode(False)

    def setDataset(self, datasetID: int):
        """ 设置当前数据集ID """
        self.datasetID = datasetID

    def setImage(self, imgID: int):
        """ 设置场景的图像 """
        self.scene.clearOthers()  # 清除当前场景中的所有项

        self.currImgID = imgID
        images:list[ImageData]=DO.query_image(id=imgID)
        if not images:
            InfoBar.warning("加载图像失败", "未找到对应的图像数据", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            return
        image=None
        if( len(images) > 0):
            image = images[0]
        else:
            return

        if not os.path.exists(image.path):
            self.scene.setImage(QImage())
            InfoBar.error("加载图像失败", f"图像路径不存在: {image.path}", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            return
        img = QImage(image.path)
        self.scene.setImage(img)
        self.fitImage()
        if image.labels is not None or image.labels == "[]":
            itemArr=ast.literal_eval(image.labels)
            self.setItemsArr(itemArr)
        
        self.enableImageDrag()

    def onLabelColorChanged(self, lblID: int, newColor: QColor):
        # print(f"处理标签颜色变化: 标签ID={lblID}, 新颜色={newColor.name()}")
        """ 处理标签列表颜色变化 """
        for item in self.scene.items():
            if isinstance(item, (LabelRectItem, LabelPolygonItem)) and item.LabelID == lblID:
                item.setPenColor(newColor)
    def saveImageLabel(self):
        itemArr=self.getItemsArr()  # 获取当前图像的标注项
        itemArrStr= str(itemArr)  # 转换为字符串格式
        affected_rows=DO.update_image(self.currImgID,labels=itemArrStr)
        if affected_rows > 0:
            InfoBar.success("保存成功", "图像标注已保存", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self.window())
            self.onSaveImageLabel.emit(self.currImgID)

    def getItemsArr(self)->list:
        size=self.scene.image().size()

        itemArr= []
        for item in self.scene.items():
            if isinstance(item, (LabelRectItem)):
                rect=item.mapRectToScene(item.rect())  # 确保矩形坐标是场景坐标
                rectStr= f"{rect.x()},{rect.y()},{rect.width()},{rect.height()}"
                labelID=item.LabelID if item.LabelID is not None else -1
                itemData = {
                    "type": "LabelRectItem",
                    "rect": rectStr,
                    "label_id": labelID,
                }
                itemArr.append(itemData)
            elif isinstance(item, (LabelPolygonItem)):
                if item.polygon().size()<3:
                    continue
                polygon = item.mapToScene(item.polygon())  # 确保多边形坐标是场景坐标
                polygonStr = ",".join([f"{point.x()},{point.y()}" for point in polygon])
                labelID=item.LabelID if item.LabelID is not None else -1
                itemData = {
                    "type": "LabelPolygonItem",
                    "polygon": polygonStr,
                    "label_id": labelID,
                }
                itemArr.append(itemData)
        return itemArr
    
    def setItemsArr(self, itemsArr: list):
        """ 设置场景中的图形项 """
        for itemData in itemsArr:
            if itemData["type"] == "LabelRectItem":
                rectParts = itemData.get("rect", '').split(",")
                rect = QRectF(float(rectParts[0]), float(rectParts[1]), float(rectParts[2]), float(rectParts[3]))
                rectItem = LabelRectItem()
                rectItem.setRect(rect)
                rectItem.state=2
                rectItem.datasetID = self.datasetID  # 设置数据集ID以获取标签列表

                labelID = itemData.get("label_id", None)
                # labelColorStr= "#00FF00"  # 默认颜色为绿色
                label:list[LabelData]=DO.query_label(id=labelID)

                if label:
                    labelColor= QColor(label[0].color)
                    rectItem.setLabel(labelID, labelColor)
                rectItem.isContinueEdit.connect(self.onItemHoverLeave)
                self.scene.addItem(rectItem)
            elif itemData["type"] == "LabelPolygonItem":
                polygonParts = itemData["polygon"].split(",")
                polygon = [QPointF(float(polygonParts[i]), float(polygonParts[i + 1])) for i in range(0, len(polygonParts), 2)]
                labelID = itemData.get("label_id", None)
                polygonItem = LabelPolygonItem()
                polygonItem.state=2
                polygonItem.setPolygon(polygon)
                polygonItem.datasetID = self.datasetID  # 设置数据集ID以获取标签列表

                label:list[LabelData]=DO.query_label(id=labelID)
                if label:
                    labelColor= QColor(label[0].color)
                    polygonItem.setLabel(labelID, labelColor)
                polygonItem.isContinueEdit.connect(self.onItemHoverLeave)
                self.scene.addItem(polygonItem)
            else:
                continue

    def fitImage(self):
        """ 自适应图片到视图 """
        if self.scene.imageItem():
            self.graphicsview.fitInView(self.scene.itemsBoundingRect(), Qt.KeepAspectRatio)

    
    def zoomIn(self):
        """ 放大视图 """
        self.graphicsview.scale(1.2, 1.2)

    def zoomOut(self):
        """ 缩小视图 """
        self.graphicsview.scale(0.8, 0.8)

    def enableImageDrag(self):
        """ 切换鼠标状态为拖动图片 """
        ismove = self.moveBtn.isChecked()
        if ismove:
            self.graphicsview.setDragMode(GraphicsView.ScrollHandDrag)
        else:
            self.graphicsview.setDragMode(GraphicsView.NoDrag)

        self.scene.isEdit=not ismove
        for item in self.scene.items():
            if isinstance(item, (LabelRectItem, LabelPolygonItem)):
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, not ismove)
                item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, not ismove)
                item.setAcceptHoverEvents(not ismove)
    
    def clearLabels(self):
        self.scene.clearOthers()  # 清除当前场景中的所有标注项

    def deleteCurrImage(self):
        deleteID= self.currImgID
        affected_row=DO.delete_image(id=self.currImgID)
        if( affected_row > 0):
            InfoBar.success("删除成功", "图像已删除", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            # self.scene.setImage(None)
            self.onDeleteImage.emit(deleteID)

        
    def keyPressEvent(self, event):
        """ 处理键盘按键事件 """
        if event.key() == Qt.Key_A:
            if self.currImgID is None:
                InfoBar.warning("操作失败", "请选择一张图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            else:
                self.saveImageLabel()
                self.onPrevImage.emit(self.currImgID)
        elif event.key() == Qt.Key_S:
            if self.currImgID is None:
                InfoBar.warning("操作失败", "请选择一张图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            else:
                self.saveImageLabel()
        elif event.key() == Qt.Key_D:
            if self.currImgID is None:
                InfoBar.warning("操作失败", "请选择一张图片", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            else:
                self.saveImageLabel()
                self.onNextImage.emit(self.currImgID)
        elif event.key() == Qt.Key_T:
            print(self.scene.isEdit)
            items=self.scene.items()
            for item in items:
                if isinstance(item, (LabelRectItem)):
                    print("矩形形区域：", item.rect())
        elif event.key() == Qt.Key_Control:
            isEditing=False
            selectItems=self.scene.selectedItems()
            for selItem in selectItems:
                if isinstance(selItem, (LabelRectItem, LabelPolygonItem)):
                    if selItem.state==1:
                        isEditing=True
                        break
            if not isEditing:          
                self.moveBtn.setChecked(self.moveBtn.isChecked() ^ True)  # 切换移动按钮状态
                self.enableImageDrag()
        else:
            super().keyPressEvent(event)

    def enterEvent(self, event):
        """ 鼠标进入事件 """
        super().enterEvent(event)
        self.setFocus() 
class LabelRectItem(GraphicsRectItem):
    """ 自定义的矩形，添加了标签功能 """
    isContinueEdit = Signal(bool)
    def __init__(self, parent=None):
        super().__init__( parent)
        self.LabelID=None
        self.datasetID=None  # 数据集ID，用于获取标签列表

        self.isdeleted=False  # 是否已删除
    
    def __del__(self):
        if not self.isdeleted:
            self.hide()
            super().__del__()
    
    def mousePressEvent(self, event):
        flags:QGraphicsItem.GraphicsItemFlag=self.flags()

        if event.button() == Qt.MouseButton.RightButton:
            menu=LabelMenu(title="标签列表",dataset_id=self.datasetID)
            menu.showMenu(QCursor.pos())

            menu.labelItemClicked.connect(self.setLabel)
            menu.cancelled.connect(self.onMenuHide)  # 菜单隐藏时恢复编辑状态
        elif flags & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
            super().mousePressEvent(event)
    """进入时禁用scene编辑"""
    def hoverEnterEvent(self, event):
        self.isContinueEdit.emit(False)
        return super().hoverEnterEvent(event)
    """进入时恢复scene编辑"""
    def hoverLeaveEvent(self, event):
        self.isContinueEdit.emit(True)
        return super().hoverLeaveEvent(event)
     
    def setLabel(self, lblID: int,lblColor: QColor):
        """ 设置标签ID和颜色 """
        self.LabelID = lblID
        self.setPenColor(lblColor)
    def onMenuHide(self):
        """ 菜单隐藏时恢复编辑状态 """
        if(self.LabelID is None):
            self.hide()
            self.deleteLater()  # 如果没有标签ID，删除该项
            self.isdeleted=True
class LabelPolygonItem(GraphicsPolygonItem):
    """ 自定义的多边形，添加了标签功能 """
    isContinueEdit = Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.LabelID=None
        self.datasetID=None  # 数据集ID，用于获取标签列表
        self.handleSize=QPointF(6, 6)
        self.isdeleted=False  # 是否已删除

    
    def __del__(self):
        if not self.isdeleted:
            self.hide()  # 删除时隐藏
            super().__del__()
    
    def mousePressEvent(self, event):
        flags:QGraphicsItem.GraphicsItemFlag=self.flags()
        if event.button() == Qt.MouseButton.RightButton:
            menu=LabelMenu(title="标签列表",dataset_id=self.datasetID)
            menu.showMenu(QCursor.pos())  # 显示菜单在鼠标位置
            menu.labelItemClicked.connect(self.setLabel)
            menu.cancelled.connect(self.onMenuHide)  # 菜单隐藏时恢复编辑状态
        elif flags & QGraphicsItem.GraphicsItemFlag.ItemIsSelectable:
            super().mousePressEvent(event)
    """进入时禁用scene编辑"""
    def hoverEnterEvent(self, event):
        self.isContinueEdit.emit(False)
        return super().hoverEnterEvent(event)
    """离开时恢复scene编辑"""
    def hoverLeaveEvent(self, event):
        self.isContinueEdit.emit(True)
        return super().hoverLeaveEvent(event)

    def setLabel(self, lblID: int,lblColor: QColor):
        """ 设置标签ID和颜色 """
        self.LabelID = lblID
        self.setPenColor(lblColor)
    def onMenuHide(self):
        """ 菜单隐藏时恢复编辑状态 """
        if(self.LabelID is None):
            self.hide()
            self.deleteLater()  # 如果没有标签ID，删除该项
            self.isdeleted=True

class LabelMenu(RoundMenu):
    labelItemClicked = Signal(int,QColor)
    cancelled = Signal()  # 菜单隐藏时发出信号
    def __init__(self, title="",dataset_id="", parent=None):
        super().__init__(title, parent) 
        self.dataset_id = dataset_id


    def showMenu(self, pos: QPointF):
        """ 显示菜单 """
        self.updateLabelList()
        self.move(pos)
        self.show()
        self.setFocus()  # 确保菜单获得焦点
    def updateLabelList(self):
        """ 更新标签列表 """
        dataset= Dataset.get(Dataset.id == self.dataset_id)
        project_id = dataset.project.id

        labels=DO.query_label(project_id=project_id)
        if not labels:
            InfoBar.warning("标签列表为空", "请先添加标签", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self.window())
            self.setWindowFlag(Qt.Dialog, False)  # 模拟对话框行为，防止自动关闭
            self.setWindowModality(Qt.NonModal)
            return
        for label in labels:
            action = Action(FIF.PIN, label.name)
            self.addAction(action)
            color=QColor(label.color)
            action.triggered.connect(lambda checked,lblID=label.id,color=color:self.onActionTriggered(checked,lblID,color))
            
    def onActionTriggered(self, checked, lblID, color):
        """ 处理标签项点击事件 """
        self.labelItemClicked.emit(lblID, color)
    
    def keyPressEvent(self, event):
        def handleKeyPress(index:int):
            actions = self.actions()
            if actions and 0 <= index < len(actions):
                print("触发动作：", actions[index].text())
                actions[index].triggered.connect(lambda: QTimer.singleShot(100, self.close))
                actions[index].trigger()
        """ 处理键盘按键事件 """
        Keys= {Qt.Key_1: 1,Qt.Key_2: 2,Qt.Key_3: 3,Qt.Key_4: 4,Qt.Key_5: 5,Qt.Key_6:6,Qt.Key_7: 7,Qt.Key_8: 8,Qt.Key_9: 9}
        if event.key() in Keys:
            handleKeyPress(Keys[event.key()]-1)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        # 如果点击在菜单外部
        if not self.rect().contains(event.pos()):
            self.cancelled.emit()
        super().mousePressEvent(event)
    