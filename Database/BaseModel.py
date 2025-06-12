from peewee import *
import datetime

# 连接SQLite数据库
db = SqliteDatabase('HRLabel.db')

# 定义基础模型类
class BaseModel(Model):
    class Meta:
        database = db


#定义项目模型
class Project(BaseModel):
    id= AutoField(primary_key=True)
    name = CharField(unique=True)
    description = TextField(null=True)
    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return "项目名称:"+self.name+"项目ID:"+str(self.id)+"项目描述:"+self.description if self.description else "无描述"
#定义数据集模型
class Dataset(BaseModel):
    id = AutoField(primary_key=True)
    project = ForeignKeyField(Project, backref='datasets')
    name = CharField()
    description = TextField(null=True)
    version= CharField(default='1.0')
    created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return self.name

#定义图片数据模型
class ImageData(BaseModel):
    id = AutoField(primary_key=True)
    dataset= ForeignKeyField(Dataset, backref='images')
    path= CharField(null=True)
    labels = TextField(null=False)  # 存储标签信息的JSON字符串
#     created_at = DateTimeField(default=datetime.datetime.now)

#定义标签类模型
class LabelData(BaseModel):
    id = AutoField(primary_key=True)
    name = CharField()
    color = CharField()  # 存储颜色的十六进制字符串
    project = ForeignKeyField(Project, backref='labels')
    # created_at = DateTimeField(default=datetime.datetime.now)

    def __str__(self):
        return f"标签名称: {self.name}, 颜色: {self.color}, 所属项目ID: {self.project.id}, 所属项目名称: {self.project.name}"
    
# 连接数据库并创建表
db.connect()
db.create_tables([Project,Dataset,ImageData,LabelData])