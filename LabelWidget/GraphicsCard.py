
from PySide6.QtCore import Qt,Signal,QRectF,QPointF
from PySide6.QtGui import QImage,QColor,QCursor
from PySide6.QtWidgets import QApplication, QVBoxLayout, QWidget,QHBoxLayout,QSpacerItem,QSizePolicy,QListWidgetItem,QGraphicsItem
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

        self.currImgID = None  # 当前选中的图片ID
        self.datasetID = None  # 当前数据集ID

        self.__connect__()
    
    def __connect__(self):
        self.zoomInBtn.clicked.connect(self.zoomIn)
        self.zoomOutBtn.clicked.connect(self.zoomOut)
        self.fitBtn.clicked.connect(self.fitImage)
        self.moveBtn.clicked.connect(self.enableImageDrag)
        self.clearBtn.clicked.connect(self.clearLabels)
        self.saveBtn.clicked.connect(self.saveImageLabel)
        self.deleteBtn.clicked.connect(self.deleteCurrImage)

        
    def onItemFinished(self,item):
        if isinstance(item, LabelPolygonItem):
            print("多边形区域：", item.polygon())
        elif isinstance(item, LabelRectItem):
            print("矩形区域：", item.rect())
        item.isContinueEdit.connect(self.scene.setEditMode)
        item.datasetID = self.datasetID  # 设置数据集ID以获取标签列表
        menu=LabelMenu(dataset_id=self.datasetID)
        menu.move(QCursor.pos())
        menu.show()
        menu.onLabelItemClicked.connect(item.setLabel)

    def onRectBtnClicked(self):
        # self.graphicsview.fitInView(self.scene.imageItem(), Qt.KeepAspectRatio) 
        if not self.moveBtn.isChecked():
            self.scene.setEditMode(self.addRectBtn.isChecked())
        self.scene.addItemFunc = lambda: LabelRectItem()
        self.addPolygonBtn.setChecked(False)

    def onPolygonBtnClicked(self):
        # self.graphicsview.fitInView(self.scene.imageItem(), Qt.KeepAspectRatio)
        if not self.moveBtn.isChecked():
            self.scene.setEditMode(self.addPolygonBtn.isChecked())
        self.scene.addItemFunc = lambda: LabelPolygonItem()
        self.addRectBtn.setChecked(False)

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
        
        image = images[0]

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

    def onLabelColorChanged(self, lblID: int, newColor: QColor):
        print(f"处理标签颜色变化: 标签ID={lblID}, 新颜色={newColor.name()}")
        """ 处理标签列表颜色变化 """
        for item in self.scene.items():
            if isinstance(item, (LabelRectItem, LabelPolygonItem)) and item.LabelID == lblID:
                item.setPenColor(newColor)
    def saveImageLabel(self):
        itemArr=self.getItemsArr()  # 获取当前图像的标注项
        itemArrStr= str(itemArr)  # 转换为字符串格式
        affected_rows=DO.update_image(self.currImgID,labels=itemArrStr)
        if affected_rows > 0:
            InfoBar.success("保存成功", "图像标注已保存", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            self.onSaveImageLabel.emit(self.currImgID)

    def getItemsArr(self)->list:
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
                rectParts = itemData["rect"].split(",")
                rect = QRectF(float(rectParts[0]), float(rectParts[1]), float(rectParts[2]), float(rectParts[3]))
                rectItem = LabelRectItem()
                rectItem.setRect(rect)

                labelID = itemData.get("label_id", None)
                # labelColorStr= "#00FF00"  # 默认颜色为绿色
                label:list[LabelData]=DO.query_label(id=labelID)

                if label:
                    labelColor= QColor(label[0].color)
                    rectItem.setLabel(labelID, labelColor)
                self.scene.addItem(rectItem)
            elif itemData["type"] == "LabelPolygonItem":
                polygonParts = itemData["polygon"].split(",")
                polygon = [QPointF(float(polygonParts[i]), float(polygonParts[i + 1])) for i in range(0, len(polygonParts), 2)]
                labelID = itemData.get("label_id", None)
                polygonItem = LabelPolygonItem()
                polygonItem.setPolygon(polygon)
                polygonItem.setLabel(labelID, QColor(Qt.GlobalColor.green))

                self.scene.addItem(polygonItem)
            else:
                continue

    def fitImage(self):
        """ 自适应图片到视图 """
        if self.scene.imageItem():
            self.graphicsview.fitInView(self.scene.imageItem(), Qt.KeepAspectRatio)
    
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
            # self.onNextImage.emit(self.currImgID)
            self.onDeleteImage.emit(deleteID)
            # def delayed_emit():
            #     time.sleep(1)  # 延迟1秒发送信号
            #     self.onDeleteImage.emit(deleteID)

            # thread = threading.Thread(target=delayed_emit)
            # thread.start()
        
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
        elif event.key() == Qt.Key_Control:
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
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu=LabelMenu(dataset_id=self.datasetID)
            menu.move(event.screenPos())
            menu.show()
            menu.onLabelItemClicked.connect(self.setLabel)
        else:
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


class LabelPolygonItem(GraphicsPolygonItem):
    """ 自定义的多边形，添加了标签功能 """
    isContinueEdit = Signal(bool)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.LabelID=None
        self.datasetID=None  # 数据集ID，用于获取标签列表
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu=LabelMenu(dataset_id=self.datasetID)
            menu.move(event.screenPos())
            menu.show()
            menu.onLabelItemClicked.connect(self.setLabel)
        else:
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

class LabelMenu(RoundMenu):
    onLabelItemClicked = Signal(int,QColor)
    def __init__(self, title="",dataset_id="", parent=None):
        super().__init__(title, parent) 
        self.dataset_id = dataset_id
        self.updateLabelList()
    
    def updateLabelList(self):
        """ 更新标签列表 """
        # TODO      从数据库读取标签列表
        dataset= Dataset.get(Dataset.id == self.dataset_id)
        project_id = dataset.project.id

        labels=DO.query_label(project_id=project_id)
        if not labels:
            InfoBar.warning("标签列表为空", "请先添加标签", Qt.Horizontal, isClosable=True, duration=3000, position=InfoBarPosition.TOP, parent=self)
            return
        for label in labels:
            action = Action(FIF.PIN, label.name)
            self.addAction(action)
            action.triggered.connect(lambda checked, lblID=label.id, color=QColor(label.color): self.onLabelItemClicked.emit(lblID, color))
    
    def keyPressEvent(self, event):
        def handleKeyPress(index:int):
            actions = self.actions()
            if actions:
                actions[index].trigger()
                self.hide()
            
        """ 处理键盘按键事件 """
        Keys= {Qt.Key_1: 0,Qt.Key_2: 1,Qt.Key_3: 2,Qt.Key_4: 3,Qt.Key_5: 4,Qt.Key_6: 5,Qt.Key_7: 6,Qt.Key_8: 7,Qt.Key_9: 8}
        if event.key() in Keys:
            handleKeyPress(Keys[event.key()])
        else:
            super().keyPressEvent(event)
