import json,os
from Transform.TransformBase import TransformBase

class GlobalData:
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 1234
        self.url = r"D:\AIProgram\AiDetect.exe"
        self.args = [r'D:\AIProgram\AITest.py', "/ip", self.ip, '/port', str(self.port), '/display','True','/weights','*weights','/model','rtdetr']
        self.args1 = [r'D:\AIProgram\AIRegionTest.py', "/ip", self.ip, '/port', str(self.port), '/display','True','/weights','*weights','/model','yolo','/weights1','*weights1','/model1','rtdetr']
        self.env = r'D:\AIProgram'
        self.splitSize=640

        self.watcherConfig={
            'script_path':r'AITrain.py',
            'exe_path':r'D:\AIProgram\AiDetect.exe',
            'working_directory':r'D:\AIProgram',
            'model':'yolo',
            'weights':'yolo11n.pt', 
            'data':r'数据集.yaml', 
            'epochs':100, 
            'batch_size':-1, 
            'workers':4,
            'project':'train',
            'name':'temp',
            'exist_ok':True
        }

        self.datasetPath='D:/AIProgram/dataset'
        self.errorLogDir='D:/AIProgram/errorlog'
        self.trainDir='D:/AIProgram/train'

        self.models=['yolo','rtdetr']
        self.weights=['yolo11l.pt','rtdetr-l.pt','yolo11l-seg.pt']
        self.isDebug=False

        self.loadJson()

    def saveJson(self):
        data={
            'ip':self.ip,
            'port':self.port,
            'url':self.url,
            'args':self.args,
            'args1':self.args1,
            'env':self.env,
            'splitSize':self.splitSize,
            'watcherConfig':self.watcherConfig,
            'datasetPath':self.datasetPath,
            'errorLogDir':self.errorLogDir,
            'models':self.models,
            'weights':self.weights,
            'isDebug':self.isDebug
        }
        with open('config.json','w') as f:
            json.dump(data,f,indent=4)

    def loadJson(self):
        if not os.path.exists('config.json'):
            self.saveJson()
        else:
            with open('config.json','r') as f:
                data=json.load(f)
                self.ip=data.get('ip', self.ip) 
                self.port=data.get('port', self.port)
                self.url=data.get('url',self.url)
                self.args=data.get('args', self.args)
                self.args1=data.get('args1', self.args1)
                self.env=data.get('env', self.env)
                self.splitSize=data.get('splitSize', self.splitSize)
                self.watcherConfig=data.get('watcherConfig', self.watcherConfig)
                self.datasetPath=data.get('datasetPath', self.datasetPath)
                self.errorLogDir=data.get('errorLogDir', self.errorLogDir)
                self.models=data.get('models',self.models)
                self.weights=data.get('weights',self.weights)
                self.isDebug=data.get('isDebug',False)

gData=GlobalData()
transform= TransformBase()
