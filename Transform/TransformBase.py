import os,json,ast
from PySide6.QtCore import QFile,QTextStream,QRectF,QPointF
from PySide6.QtGui import QPolygonF,QImage
class TransformBase:
    def __init__(self) -> None:
        """"""


    def labelToDict(self, label:str) -> dict:
        """将label字符串转换为dict类型"""
        try:
            return ast.literal_eval(label)
        except Exception:
            return []

    def transformYolo(self,fileName:str,labelStr:str,width:int,height:int,labelDict:dict)->str:
        """
        转换为yolo格式
        """
        if(width<0):
            width=-width
        if(height<0):
            height=-height

        labelArr=self.labelToDict(labelStr)

        labelStr=""
        for labelObj in labelArr:
            if labelObj["type"]=="LabelRectItem":
                rectParts=labelObj["rect"].split(",")
                rect = QRectF(float(rectParts[0]), float(rectParts[1]), float(rectParts[2]), float(rectParts[3]))
                centerX=round(rect.center().x()/width,6)
                centerY=round(rect.center().y()/height,6)
                w=round(rect.width()/width,6)
                h=round(rect.height()/height,6)
                if w<0:
                    w=-w
                if h<0:
                    h=-h

                labelStr=labelStr+str(labelDict[str(labelObj["label_id"])])+" "+str(centerX)+" "+str(centerY)+" "+str(w)+" "+str(h)+"\n"
            elif labelObj["type"]=="LabelPolygonItem":
                polygonParts = labelObj["polygon"].split(",")
                polygon = [QPointF(float(polygonParts[i]), float(polygonParts[i + 1])) for i in range(0, len(polygonParts), 2)]

                polygonStr=""
                for point in polygon:
                    polygonStr+=str(round(point.x()/width,6))+" "+str(round(point.y()/height,6))+" "
                polygonStr=polygonStr[:-1]
                labelStr=labelStr+str(labelDict[str(labelObj["label_id"])])+" "+polygonStr+"\n"
        
        return labelStr

    def splitImage(self,imagePath:str,labelStr:str,splitSize:int)->list[QImage]:
        """
        切分图片
        """
        labelArr=self.labelToDict(labelStr)

        imgList:list[QImage]=[]
        
        for labelObj in labelArr:
            if labelObj["type"]=="LabelPolygonItem":
                polygonParts = labelObj["polygon"].split(",")
                polygonlist = [QPointF(float(polygonParts[i]), float(polygonParts[i + 1])) for i in range(0, len(polygonParts), 2)]
                polygonF=QPolygonF(polygonlist)

                center=polygonF.boundingRect().center()

                qimage=QImage(imagePath)
                qimage=qimage.copy(center.x()-splitSize/2,center.y()-splitSize/2,splitSize,splitSize)
                imgList.append(qimage)
            elif labelObj["type"]=="LabelRectItem":
                rectParts=labelObj["rect"].split(",")
                rect = QRectF(float(rectParts[0]), float(rectParts[1]), float(rectParts[2]), float(rectParts[3]))
                center=rect.center()
                qimage=QImage(imagePath)
                qimage=qimage.copy(center.x()-splitSize/2,center.y()-splitSize/2,splitSize,splitSize)
                imgList.append(qimage)
        return imgList
    
    def transformRtdetr(self,fileName:str,labelStr:str,splitSize:int,labelDict:dict)->list[str]:

        """
        转换为rtdetr格式
        """
        labelStrArr:list[str]=[]
        labelArr=self.labelToDict(labelStr)
        for i,labelObj in enumerate(labelArr):
            if labelObj["type"]=="LabelPolygonItem":
                polygonParts = labelObj["polygon"].split(",")
                polygonlist = [QPointF(float(polygonParts[i]), float(polygonParts[i + 1])) for i in range(0, len(polygonParts), 2)]
                polygonF=QPolygonF(polygonlist)

                center=polygonF.boundingRect().center()
                leftTop=QPointF(center.x()-splitSize/2,center.y()-splitSize/2)

                polygonStr=""
                for point in polygonlist:
                    polygonStr+=str(round((point.x()-leftTop.x())/splitSize,6))+" "+str(round((point.y()-leftTop.y())/splitSize,6))+" "
                polygonStr=polygonStr[:-1]

                labelStr=str(labelDict[str(labelObj["label_id"])])+" "+polygonStr+"\n"
                labelStrArr.append(labelStr)
            elif labelObj["type"]=="LabelRectItem":
                rectParts=labelObj["rect"].split(",")
                rect = QRectF(float(rectParts[0]), float(rectParts[1]), float(rectParts[2]), float(rectParts[3]))
                center=rect.center()
                leftTop=QPointF(center.x()-splitSize/2,center.y()-splitSize/2)
                rectStr=str(round((center.x()-leftTop.x())/splitSize,6))+" "+str(round((center.y()-leftTop.y())/splitSize,6))+" "+str(round(rect.width()/splitSize,6))+" "+str(round(rect.height()/splitSize,6))+"\n"

                
                labelStr=str(labelDict[str(labelObj["label_id"])])+" "+rectStr
                labelStrArr.append(labelStr)


        return labelStrArr



