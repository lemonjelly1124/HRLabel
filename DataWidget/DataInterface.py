from PySide6.QtCore import Qt,Signal,QSize,QFile,QTextStream
from PySide6.QtGui import QImage,QPixmap,QFont
from PySide6.QtWidgets import QHBoxLayout,QVBoxLayout,QGridLayout,QWidget,QStackedWidget,QListWidgetItem,QTableWidgetItem,QHeaderView,QFileDialog
from qfluentwidgets import (PushButton,PrimaryPushButton,FluentIcon,LineEdit,ToolButton,ListWidget,SimpleCardWidget,ImageLabel,BodyLabel,TableWidget,setFont,ProgressBar,HyperlinkButton,InfoBar,InfoBarPosition,MessageBox)
from Database.DataOperate import DataOperate as DO
from .ProjectDialog import ProjectDialog
from .ProjectCard import ProjectCard
from .ProjectListCard import ProjectListCard
from .TrainDialog import TrainDialog
from .TrainModelDialog import TrainModelDialog
from Database.BaseModel import *
from GlobalData import gData
from Transform.TransformBase import TransformBase
import os,shutil
from HRVision.utils import GenerateTrainWatcher, GetTrainWatcherList, TrainWatcher
from datetime import datetime

class DataInterface(QWidget):
    signalError=Signal(TrainWatcher)
    signalProgramStart=Signal(TrainWatcher)
    signalProgramEnd=Signal(TrainWatcher)
    signalTrainBatchEnd=Signal(TrainWatcher)
    signalModelLoad=Signal(TrainWatcher)
    signalPretrainRoutineStart=Signal(TrainWatcher)
    signalPretrainRoutineEnd=Signal(TrainWatcher)


    """ Data Interface Widget """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("DataInterface")
    
        self.watcher=None
        self.currProjectName=''
        self.modelPath=''
        self.isTraining=False

        self.isTrainSplit=False


        self.__initWidget__()
        self.__initConnect__()
    def __initWidget__(self):
        """ Initialize the widget layout """
        self.hLayout = QHBoxLayout(self)
        """左侧项目列表布局"""
        self.projectListCard=ProjectListCard()

        self.hLayout.addWidget(self.projectListCard)
        """左侧项目列表布局"""

        """右侧数据集布局"""
        cardWdg=QWidget()
        vCardLayout = QVBoxLayout(cardWdg)
        vCardLayout.setContentsMargins(0, 0, 0, 0)
        self.projectCard = ProjectCard()
        vCardLayout.addWidget(self.projectCard)
        self.hLayout.addWidget(cardWdg)

        """右侧数据集布局"""

        self.projectCard.hide()

    def onProjectItemClicked(self,projectID):
        """点击项目item刷新右侧详情页"""
        projects = DO.query_project(id=projectID)
        self.projectCard.setProject(projects[0])
        self.isInTraining()

        self.projectCard.show()
    
    def isInTraining(self):
        if(self.currProjectName==self.projectCard.titleLbl.text()):
            self.projectCard.trainProgress.show()
            self.projectCard.saveBtn.show()
            self.projectCard.stopBtn.setVisible(self.isTraining)
            self.projectCard.trainBtn.setVisible(not self.isTraining)
        else:
            self.projectCard.trainProgress.hide()
            self.projectCard.saveBtn.hide()
            self.projectCard.stopBtn.hide()
            self.projectCard.trainBtn.show()
        


    def __initConnect__(self):
        """ Initialize the connections for signals and slots """
        self.projectCard.onProjectEdited.connect(self.projectListCard.onProjectEdited)
        self.projectCard.onProjectDeleted.connect(self.projectListCard.onProjectDeleted)
        self.projectCard.trainBtn.clicked.connect(self.onTrainBtnClicked)
        self.projectCard.saveBtn.clicked.connect(self.onSaveBtnClicked)
        self.projectCard.exportBtn.clicked.connect(self.onExportBtnClicked)
        self.projectCard.stopBtn.clicked.connect(self.onStopBtnClicked)


        self.projectListCard.onProjectItemClicked.connect(self.onProjectItemClicked)
        self.projectListCard.onHideProjectCard.connect(self.projectCard.hide)


    def onTrainBtnClicked(self):
        """点击训练按钮"""
        # trainDlg=TrainDialog(self.window())
        # if trainDlg.exec() == MessageBox.Accepted:
        #     gData.watcherConfig['epochs']=trainDlg.spnEpochs.value()
        #     gData.watcherConfig['batch_size']=trainDlg.spnBatchSize.value()
        #     gData.watcherConfig['workers']=trainDlg.spnWorkers.value()
        #     gData.watcherConfig['model']='detr'
        #     gData.watcherConfig['weights']=trainDlg.cmbWeights.currentText()

        checkedRows=0
        for i in range(self.projectCard.dataTable.rowCount()):
            item = self.projectCard.dataTable.item(i, 0)
            if item is not None and item.checkState() == Qt.Checked:
                checkedRows+=1
        if checkedRows==0:
            InfoBar.error("训练模型", "请至少选择一个数据集进行训练", duration=3000, position=InfoBarPosition.TOP, parent=self.window())
            return


        trainDlg=TrainModelDialog(self.window())
        if trainDlg.exec() == MessageBox.Accepted:
            gData.watcherConfig['epochs']=trainDlg.spnEpochs.value()
            gData.watcherConfig['batch_size']=trainDlg.spnBatchSize.value()
            gData.watcherConfig['workers']=trainDlg.spnWorkers.value()
            gData.watcherConfig['model']=gData.models[trainDlg.cmbModel.currentIndex()]
            gData.watcherConfig['weights']=gData.weights[trainDlg.cmbModel.currentIndex()]
            gData.saveJson()

            self.isTrainSplit=trainDlg.chkSplit.isChecked()
            if(self.isTrainSplit):
                gData.watcherConfig['weights']=gData.weights[2]

            self.prepareImageData()

            self.startTrain()

    def onSaveBtnClicked(self):
        """点击保存按钮"""
        if self.modelPath=='':
            InfoBar.error("保存失败", "请先训练模型", duration=3000, position=InfoBarPosition.TOP, parent=self.window())
            return
        savePath=QFileDialog.getSaveFileName(self.window(), "选择模型保存路径", gData.datasetPath, "Model Files (*.pt)")[0]
        if savePath=='':
            return
        shutil.copy(self.modelPath,savePath)
        InfoBar.info("模型保存", "保存成功", duration=3000, position=InfoBarPosition.TOP, parent=self.window())
    
    def onExportBtnClicked(self):
        trainDlg=TrainModelDialog(self.window())
        if trainDlg.exec() == MessageBox.Accepted:
            self.isTrainSplit=trainDlg.chkSplit.isChecked()
            self.prepareImageData()

    def onStopBtnClicked(self):
        """点击停止按钮"""
        if self.watcher is not None:
            self.watcher.stop()
            self.isTraining=False
            self.isInTraining()

    def prepareImageData(self):
        InfoBar.info("模型训练", "正在初始化数据集", Qt.Horizontal, isClosable=True, duration=10000, position=InfoBarPosition.TOP, parent=self.window())

        if self.isTrainSplit:
            labelDict=self.createCrackYaml(self.projectCard.projectID,isSplit=True)
        else:
            labelDict=self.createCrackYaml(self.projectCard.projectID)      #key标签,value索引

        datasetIDs = []
        for row in range(self.projectCard.dataTable.rowCount()):
            item = self.projectCard.dataTable.item(row, 0)  # 获取第一列的item
            if item is not None and item.checkState() == Qt.Checked:
                datasetIDs.append(int(item.text()))

        imageArr:list[ImageData]=[]
        for datasetID in datasetIDs:
            images=DO.query_image(dataset_id=datasetID)
            imageArr.extend(images)

        imagesDir=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"/images/"
        labelsDir=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"/labels/"
        imagesSplitDir=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"_split/images/"
        labelsSplitDir=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"_split/labels/"


        # 清空imagesDir文件夹
        if os.path.exists(imagesDir):
            shutil.rmtree(imagesDir)
            # 清空labelsDir文件夹
        if os.path.exists(labelsDir):
            shutil.rmtree(labelsDir)
        
        if not os.path.exists(imagesDir):
            os.makedirs(imagesDir)
        if not os.path.exists(labelsDir):
            os.makedirs(labelsDir)

        if not os.path.exists(imagesSplitDir) and self.isTrainSplit:
            os.makedirs(imagesSplitDir)
        if not os.path.exists(labelsSplitDir) and self.isTrainSplit:
            os.makedirs(labelsSplitDir)
        
        transform=TransformBase()

        for imageObj in imageArr:
            path=imageObj.path
            imageName=os.path.basename(path)
            if not os.path.exists(path):
                continue
            if imageObj.labels is None or imageObj.labels == "[]":
                continue
            
            if self.isTrainSplit:

                #写入标签数据
                labelStrArr=transform.transformRtdetr(imageName,imageObj.labels,gData.splitSize,labelDict)
                for i in range(len(labelStrArr)):
                    with open(labelsSplitDir+imageName.split(".")[0]+"_"+str(i)+".txt", "w") as f:
                        f.write(labelStrArr[i])
                #写入裁切图片
                imgList=transform.splitImage(path,imageObj.labels,gData.splitSize)
                for i in range(len(imgList)):
                    imgList[i].save(imagesSplitDir+imageName.split(".")[0]+"_"+str(i)+".jpg")
            else:
                os.makedirs(imagesDir,exist_ok=True)
                os.makedirs(labelsDir,exist_ok=True)
                shutil.copy2(path,imagesDir+imageName)

                labelStr=transform.transformYolo(imageName,imageObj.labels,imageObj.sizeW,imageObj.sizeH,labelDict)
                with open(labelsDir+imageName.split(".")[0]+".txt", "w") as f:
                    f.write(labelStr)

        InfoBar.success("模型训练", "数据集初始化完成", Qt.Horizontal, isClosable=True, duration=10000, position=InfoBarPosition.TOP, parent=self.window())
    
    def createCrackYaml(self,projectID:int,isSplit=False)->dict:

        labelArr:list[LabelData]=DO.query_label(project_id=projectID)
        if not isSplit:
            yamlPath=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+".yaml"
        else:
            yamlPath=gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"_split.yaml"

        file=QFile(yamlPath)
        file.open(QFile.WriteOnly)
        out=QTextStream(file)

        
        if not isSplit:
            out<<"path: "+gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"\n"
        else:
            out<<"path: "+gData.datasetPath+'/'+self.projectCard.titleLbl.text()+"_split\n"
        out<<"train: images\n"
        out<<"val: images\n\n"
        out<<"nc: "+str(len(labelArr))+"\n"
        out<<"names: ["

        labelDict={}
        for i in range(len(labelArr)):
            out<<"\""+labelArr[i].name+"\""
            if i!=len(labelArr)-1:
                out<<","
            labelDict[str(labelArr[i].id)]=i
        out<<"]\n"
        file.close()
    
        return labelDict

    def startTrain(self):
        # 删除缓存文件夹
        if os.path.exists(gData.trainDir+'/temp'):
            shutil.rmtree(gData.trainDir+'/temp')
        if not os.path.exists(gData.trainDir+'/temp'):
            os.makedirs(gData.trainDir+'/temp')
        if self.watcher is None:
            self.watcher=GenerateTrainWatcher(GetTrainWatcherList()[0])
            
            self.watcher.add_callback('on_error',lambda x:self.signalError.emit(x))
            self.watcher.add_callback('on_program_start', lambda x:self.signalProgramStart.emit(x))
            self.watcher.add_callback('on_program_end', lambda x:self.signalProgramEnd.emit(x))
            self.watcher.add_callback('on_train_batch_end', lambda x:self.signalTrainBatchEnd.emit(x))

            self.watcher.add_callback('on_model_load', lambda x: self.signalModelLoad.emit(x))
            self.watcher.add_callback('on_pretrain_routine_start', lambda x: self.signalPretrainRoutineStart.emit(x))
            self.watcher.add_callback('on_pretrain_routine_end', lambda x: self.signalPretrainRoutineEnd.emit(x))

            self.signalError.connect(self.onError)
            self.signalProgramStart.connect(self.onProgramStart)
            self.signalProgramEnd.connect(self.onProgramEnd)
            self.signalTrainBatchEnd.connect(self.onTrainBatchEnd)
            self.signalModelLoad.connect(self.onModelLoad)
            self.signalPretrainRoutineStart.connect(self.onPretrainRoutineStart)
            self.signalPretrainRoutineEnd.connect(self.onPretrainRoutineEnd)
        

        self.currProjectName=self.projectCard.titleLbl.text()
        print(gData.watcherConfig)
        yamlPath=''
        if self.isTrainSplit:
            yamlPath=gData.datasetPath+'/'+self.currProjectName+"_split.yaml"
        else:
            yamlPath=gData.datasetPath+'/'+self.currProjectName+".yaml"
        print(yamlPath)
        self.watcher.start(script_path=gData.watcherConfig['script_path'], 
                exe_path=gData.watcherConfig['exe_path'],
                working_directory=gData.watcherConfig['working_directory'],
                model=gData.watcherConfig['model'],
                weights=gData.watcherConfig['weights'], 
                data=yamlPath,
                epochs=gData.watcherConfig['epochs'], 
                batch_size=gData.watcherConfig['batch_size'], 
                workers=gData.watcherConfig['workers'],
                project=gData.watcherConfig['project'],
                name=gData.watcherConfig['name'],
                exist_ok=gData.watcherConfig['exist_ok'])
        

    def onError(self,x):
        print(x.error_message)
        # 使用GlobalData中的路径
        log_path = os.path.join(gData.errorLogDir, datetime.now().strftime('%Y-%m-%d %H-%M-%S')+'.txt')
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"{x.error_message}\n")

        InfoBar.error("模型训练", "训练出错:"+x.error_message, Qt.Horizontal, isClosable=True, duration=120000, position=InfoBarPosition.TOP, parent=self.window())
        self.projectCard.trainBtn.setEnabled(True)
    def onProgramStart(self,x):
        print("训练开始")
        self.projectCard.trainProgress.setValue(0)
        self.isTraining=True
        self.isInTraining()
        self.projectCard.saveBtn.setEnabled(False)

        InfoBar.info("模型训练", "训练开始", Qt.Horizontal, isClosable=True, duration=30000, position=InfoBarPosition.TOP, parent=self.window())
    
    def onProgramEnd(self,x):
        print("训练结束")
        self.isTraining=False
        self.isInTraining()
        if self.watcher.status==TrainWatcher.Status.COMPLETED :
            # if self.isTrainSplit:

            InfoBar.success("模型训练", "训练完成", Qt.Horizontal, isClosable=True, duration=120000, position=InfoBarPosition.TOP, parent=self.window())
            srcDir=gData.trainDir+'/temp'
            if self.isTrainSplit:
                dstDir=gData.trainDir+'/'+self.currProjectName+'_split/'+datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                self.modelPath=dstDir+'/weights/best.pt'
            else:
                dstDir=gData.trainDir+'/'+self.currProjectName+'/'+datetime.now().strftime("%Y-%m-%d %H-%M-%S")
                self.modelPath=dstDir+'/weights/best.pt'
            self.copy_all_files(srcDir,dstDir)
            self.projectCard.saveBtn.setEnabled(True)
        elif self.watcher.status==TrainWatcher.Status.FAILED:
            InfoBar.error("模型训练", "训练失败", Qt.Horizontal, isClosable=True, duration=120000, position=InfoBarPosition.TOP, parent=self.window())
    def onTrainBatchEnd(self,x:TrainWatcher):
        print(f'Progressing... {x.progress():.2f}...batch {x.batch}...batchs {x.batchs}...epoch {x.epoch}....epochs {x.epochs}')
        self.projectCard.trainProgress.setValue(int(x.progress()))

    def onModelLoad(self,x):
        print("模型加载完成")
        InfoBar.info("模型训练", "模型加载完成", Qt.Horizontal, isClosable=True, duration=30000, position=InfoBarPosition.TOP, parent=self.window())
    
    def onPretrainRoutineStart(self,x):
        print("预训练开始")
        InfoBar.info("模型训练", "预训练开始", Qt.Horizontal, isClosable=True, duration=30000, position=InfoBarPosition.TOP, parent=self.window())
    
    def onPretrainRoutineEnd(self,x):
        print("预训练结束")
        InfoBar.info("模型训练", "预训练结束", Qt.Horizontal, isClosable=True, duration=30000, position=InfoBarPosition.TOP, parent=self.window())

    
    def copy_all_files(self,src_dir, dst_dir):
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dst_path = os.path.join(dst_dir, item)
            
            if os.path.isdir(src_path):
                # 如果是子文件夹，递归调用
                self.copy_all_files(src_path, dst_path)
            else:
                # 如果是文件，直接复制
                shutil.copy2(src_path, dst_path)
                print(f"已复制: {src_path} -> {dst_path}")

        

        