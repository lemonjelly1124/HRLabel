import queue
import socket
import json
import sys
import os
import threading
import traceback

import cv2
import numpy
import psutil

path = os.getcwd()
sys.path.append(path)
os.chdir(path)

from ultralytics.utils.plotting import colors
import PyQt5.QtWidgets
from ProcessServer import *

import PyQt5.QtWidgets
from PyQt5.QtCore import QElapsedTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import (QApplication, 
                             QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
                             QWidget, QHBoxLayout, QTextEdit)

class Signal(QObject):
    updateText = pyqtSignal(str)

if __name__ == '__main__':
    psutil.Process(psutil.Process().pid).nice(psutil.HIGH_PRIORITY_CLASS)
    app = QApplication(sys.argv)
            
    mainWidget = QWidget()
    view = QGraphicsView()
    scene = QGraphicsScene()
    item = QGraphicsPixmapItem()
    scene.addItem(item)
    view.setScene(scene)
    textEdit = QTextEdit()
    hl = QHBoxLayout()
    hl.addWidget(view,2)
    hl.addWidget(textEdit,1)
    mainWidget.setLayout(hl)
    
    signal_ = Signal()
    signal_.updateText.connect(textEdit.append)
    
    model = None
    timer = QElapsedTimer()
    
    class StreamToTextEdit:
        def __init__(self, text_edit):
            self.text_edit = text_edit

        def write(self, message):
            signal_.updateText.emit(message.strip())

        def flush(self):
            pass

    sys.stdout = StreamToTextEdit(textEdit)
    sys.stderr = StreamToTextEdit(textEdit)

    def ModelResultToUser(results:list) -> str:
        _json = []
        if results[0].boxes is not None:
            res = results[0]
            names = res.names
            if res.masks is None:
                for box, score, cls in zip(res.boxes.xyxy, res.boxes.conf, res.boxes.cls):
                    x1, y1, x2, y2 = map(float, box)
                    name = names[int(cls)]
                    color = colors(int(cls))
                    _rect = {"x": x1, "y": y1, "width": x2-x1, "height": y2-y1}
                    _json.append({
                        "rect":_rect, 
                        "mask": None,
                        "color": color,
                        "classType": int(cls),
                        "className": name,
                        "classScore": float(score)
                        })
            else:
                for box, score, cls, mask in zip(res.boxes.xyxy, res.boxes.conf, res.boxes.cls, res.masks.xy):
                    x1, y1, x2, y2 = map(float, box)
                    name = names[int(cls)]
                    color = colors(int(cls))
                    _rect = {"x": x1, "y": y1, "width": x2-x1, "height": y2-y1}
                    _mask = mask.tolist()
                    _json.append({
                        "rect":_rect, 
                        "mask": _mask,
                        "color": color,
                        "classType": int(cls),
                        "className": name,
                        "classScore": float(score)
                        })
        
        if len(_json) > 0:
            boxes = []
            scores = []
            for item in _json:
                boxes.append([item["rect"]["x"], item["rect"]["y"], item["rect"]["width"], item["rect"]["height"]])
                scores.append(item["classScore"])
            indices = cv2.dnn.NMSBoxes(boxes, scores, 0, 0.4)
            filtered = []
            for i in indices:
                filtered.append(_json[i])
            _json = filtered
            
        return _json

    def ProcessRequest(client:Client, _socket:dict, message:str):
        client.replyRequest(_socket)
        
    def ProcessEvent(_socket:ProcessSocket):
        try:
            global res_infos
            global run_finished
            
            res_infos = []
            run_finished = 0
            timer.start()
            src = _socket.inputImage['image']
            if src is not None:
                if len(src.shape) == 3:
                    if src.shape[2] == 4:
                        src = cv2.cvtColor(src, cv2.COLOR_RGBA2RGB)
                    elif src.shape[2] == 1:
                        src = cv2.cvtColor(src, cv2.COLOR_GRAY2RGB)
                elif len(src.shape) == 2:
                    src = cv2.cvtColor(src, cv2.COLOR_GRAY2RGB)
                    
                result = model.predict(src)
                res_arr = ModelResultToUser(result)
                # _socket.outputImage['image'] = HRVision.ToQImage(img)
                _socket.outputJson['have'] = len(res_arr) > 0 
                _socket.outputJson['result'] = res_arr
                _socket.outputJson['err_code'] = ""
                # src = cv2.cvtColor(src, cv2.COLOR_BGR2RGB)
                # mainWidget.setImage(HRVision.ToQImage(src))
                print("run time: ", str(timer.elapsed()) ,"ms")
                # print(res)
            else:
                # _socket.outputImage['image'] = _socket.inputImage['image']
                _socket.outputJson['result'] = ""
                _socket.outputJson['err_code'] = "image is empty"
                
                # print("detect count:", 0 ,"\trun time: ", str(timer.elapsed()) ,"ms")
        except Exception as ex:
            traceback.print_exc()
            _socket.outputJson['result'] = ""
            _socket.outputJson['err_code'] = "unknow Exception"
            _socket.outputJson['err_info'] = traceback.format_exc()

        _socket.reply()
    
    exitLoop = False 
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    hostname = socket.gethostname()
    # ip = socket.gethostbyname(hostname)
    ip = "127.0.0.1"
    if "/ip" in sys.argv:
        idx = sys.argv.index("/ip")
        if idx + 1 < len(sys.argv):
            ip = str(sys.argv[idx+1])
    host = ip
    print("ip: ", host)
    if "/port" in sys.argv:
        idx = sys.argv.index("/port")
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx+1])
        else:
            port = 1234
    else:
        port = 1234
    print("port: ", port)
    
    if "/weights" in sys.argv:
        idx = sys.argv.index("/weights")
        if idx + 1 < len(sys.argv):
            weights = str(sys.argv[idx+1])
        else:
            weights = './AIModels/yolov8s.pt'
    else:
        weights = './AIModels/yolov8s.pt'
    print("weights: ", weights)
    
    if "/display" in sys.argv:
        idx = sys.argv.index("/display")
        if idx + 1 < len(sys.argv):
            display = sys.argv[idx+1] == 'True'
        else:
            display = True
    else:
        display = True
    print("display: ", display)
    
    try:
        #绑定地址
        socket_server.bind((host, port))
        #设置监听
        socket_server.listen(5)
        print("服务器启动成功")
    except Exception as e:
        print("服务器启动失败")
        traceback.print_exc()
    
    client_socket = None
    def run():
        from ultralytics import YOLO
        from ultralytics import RTDETR
        global model
        if ("detr" in weights.lower()):
            model = RTDETR(weights)
        else:
            model = YOLO(weights)
        img = numpy.zeros((640, 640, 3), dtype=numpy.uint8)
        model.predict(img)
        global client_socket
        while exitLoop is False:
            try:
                # socket_server.accept()返回一个元组, 元素1为客户端的socket对象, 元素2为客户端的地址(ip地址，端口号)
                client_socket, address = socket_server.accept()

                client = Client(client_socket, ProcessEvent, ProcessRequest)
                
                print("新的设备连接: " + str(address))
                
                while exitLoop is False:
                    recvmsg = client_socket.recv(8192)
                    if len(recvmsg) == 0:
                        break
                        # raise Exception("socket is closed")
                    # print(recvmsg)
                    client.receiveClientMsg(recvmsg)
                client_socket.close()
            except Exception as e:
                traceback.print_exc()
                break
        app.quit()
                
            
    th = threading.Thread(target=run)
    th.start()
    
    # th1 = threading.Thread(target=process)
    # th2 = threading.Thread(target=process)
    
    # th1.start()
    # th2.start()
    if display is True:
        mainWidget.show()
        app.exec_()
    else:
        app.exec_()
    exitLoop = True
    #关闭服务器端    
    if client_socket is not None:
        client_socket.close()
    socket_server.close()
    
    th.join()
