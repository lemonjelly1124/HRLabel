import json

from hrfluentwidgets import GraphicsView,GraphicsScene

import sys
from PySide6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem,QGraphicsPolygonItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QTouchEvent, QTransform,QPainter,QPolygonF,QPen,QBrush



def main():
    with open("C:\\Users\\14394\\Desktop\\measureData\\木板\\Labels\\Image_20251119190121430_result.json",'r') as f:
        result=json.load(f)
    app = QApplication(sys.argv)

    big_polygon=[]
    avoid_polygon=[]
    for item in result:
        if item['classType']==0:
            for point in item['mask']:
                big_polygon.append(QPointF(point[0],point[1]))
        elif item['classType']==1:
            for point in item['mask']:
                avoid_polygon.append(QPointF(point[0],point[1]))



    view = GraphicsView()
    scene = GraphicsScene()
    view.setScene(scene)
    scene.addPolygon(QPolygonF(big_polygon),QPen(Qt.red))
    scene.addPolygon(QPolygonF(avoid_polygon),QPen(Qt.green))
    view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
