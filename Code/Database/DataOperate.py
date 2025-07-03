from Database.BaseModel import *
from peewee import *
from playhouse.shortcuts import model_to_dict


class DataOperate:
    """ 数据操作类 """
    @staticmethod
    def isExistProject(project_name:str):
        """ 检查项目是否存在 """
        return Project.select().where(Project.name == project_name).exists()

    @staticmethod
    def insert_project(project:Project):
        """ 添加项目 """
        project_dict=model_to_dict(project, exclude=[Project.id])
        projectRes = Project.create(**project_dict)
        return projectRes
    
    @staticmethod
    def query_project(**kwargs):
        """
        条件查询项目
        支持参数:
        - id : 项目名 
        """
        query = Project.select()
        
        if 'id' in kwargs:
            query = query.where(Project.id == kwargs['id'])
        projects= []
        for project in query:
            projects.append(project)
        return projects
    
    @staticmethod
    def update_project(project_id: int,**kwargs):
        """
        更新项目
        索引:
        - project_id : 项目ID
        支持参数:
        - name : 项目名称
        - description : 项目描述
        """
        query = Project.update(**kwargs).where(Project.id == project_id)        
        return query.execute()
    
    @staticmethod
    def delete_project(**kwargs):
        """
        删除项目
        支持参数:
        - id : 项目ID
        --name : 项目名称
        """
        query = Project.delete()
        conditions = []
        if 'id' in kwargs:
            conditions.append(Project.id == kwargs['id'])
        if 'name' in kwargs:
            conditions.append(Project.name == kwargs['name'])
        query = query.where(*conditions)

        return query.execute()
    
    @staticmethod
    def isExistDataset(**kwargs):
        """
        检查数据集是否存在
        索引:
        -project_id : 项目ID
        支持参数:
        - version : 数据集版本
        - name : 数据集名称
        """
        existKey=[]
        query = Dataset.select()
        if 'version' in kwargs:
            query = query.where(Dataset.version == kwargs['version'] and Dataset.project == kwargs['project_id'])
            if query.exists():
                existKey.append('version')
        if 'name' in kwargs:
            query = query.where(Dataset.name == kwargs['name'] and Dataset.project == kwargs['project_id'])
            if query.exists():
                existKey.append('name')
        
        return query.exists()
    
    @staticmethod
    def insert_dataset(dataset:Dataset,**kwargs):
        """ 添加数据集 """
        dataset.save()
        return dataset
    
    def query_dataset(**kwargs):
        """
        条件查询数据集
        支持参数:
        - id : 数据集ID
        - project_id : 项目ID
        - name : 数据集名称
        - version : 数据集版本
        """
        query = Dataset.select()
        
        if 'id' in kwargs:
            query = query.where(Dataset.id == kwargs['id'])
        if 'project_id' in kwargs:
            query = query.where(Dataset.project == kwargs['project_id'])
        if 'name' in kwargs:
            query = query.where(Dataset.name == kwargs['name'])
        if 'version' in kwargs:
            query = query.where(Dataset.version == kwargs['version'])
        
        datasets = []
        for dataset in query:
            datasets.append(dataset)
        return datasets

    @staticmethod
    def update_dataset(dataset_id: int, **kwargs):
        """
        更新数据集
        索引:
        - dataset_id : 数据集ID
        支持参数:
        - name : 数据集名称
        - version : 数据集版本
        - description : 数据集描述
        """
        query = Dataset.update(**kwargs).where(Dataset.id == dataset_id)
        return query.execute()
    
    @staticmethod
    def delete_dataset(**kwargs):
        """
        删除数据集
        支持参数:
        - id : 数据集ID
        - name : 数据集名称
        - version : 数据集版本
        - project_id : 项目ID
        """
        query = Dataset.delete()
        conditions = []
        if 'id' in kwargs:
            conditions.append(Dataset.id == kwargs['id'])
        if 'name' in kwargs:
            conditions.append(Dataset.name == kwargs['name'])
        if 'version' in kwargs:
            conditions.append(Dataset.version == kwargs['version'])
        if 'project_id' in kwargs:
            conditions.append(Dataset.project == kwargs['project_id'])
        
        query = query.where(*conditions)
        return query.execute()
    
    @staticmethod
    def query_image(**kwargs):
        """
        条件查询图片数据
        支持参数:
        - id : 图片ID
        - dataset_id : 数据集ID
        - path : 图片路径
        """
        query = ImageData.select()
        
        if 'id' in kwargs:
            query = query.where(ImageData.id == kwargs['id'])
        if 'dataset_id' in kwargs:
            query = query.where(ImageData.dataset == kwargs['dataset_id'])
        
        images = []
        for image in query:
            images.append(image)
        return images
    
    @staticmethod
    def insert_image(image:ImageData):
        """ 添加图片数据 """
        image.save()
        return image
    
    @staticmethod
    def update_image(image_id: int, **kwargs):
        """
        更新图片数据
        索引:
        - image_id : 图片ID
        支持参数:
        - path : 图片路径
        - dataset_id : 数据集ID
        -labels : 标签信息 (JSON字符串)
        """
        query = ImageData.update(**kwargs).where(ImageData.id == image_id)
        return query.execute()
    
    @staticmethod
    def delete_image(**kwargs):
        """
        删除图片数据
        支持参数:
        - id : 图片ID
        - dataset_id : 数据集ID
        - path : 图片路径
        """
        query = ImageData.delete()
        conditions = []
        if 'id' in kwargs:
            conditions.append(ImageData.id == kwargs['id'])
        if 'dataset_id' in kwargs:
            conditions.append(ImageData.dataset == kwargs['dataset_id'])
        if 'path' in kwargs:
            conditions.append(ImageData.path == kwargs['path'])
        
        query = query.where(*conditions)
        return query.execute()

    @staticmethod
    def query_label(**kwargs):
        """
        条件查询标签数据
        支持参数:
        - id : 标签ID
        - project_id : 项目ID
        - name : 标签名称
        """
        query = LabelData.select()
        
        if 'id' in kwargs:
            query = query.where(LabelData.id == kwargs['id'])
        if 'project_id' in kwargs:
            query = query.where(LabelData.project == kwargs['project_id'])
        if 'name' in kwargs:
            query = query.where(LabelData.name == kwargs['name'])
        
        labels = []
        for label in query:
            labels.append(label)
        return labels
    
    @staticmethod
    def insert_label(label:LabelData):
        """ 添加标签数据 """
        label.save()
        return label
    
    @staticmethod
    def update_label(label_id: int, **kwargs):
        """
        更新标签数据
        索引:
        - label_id : 标签ID
        支持参数:
        - name : 标签名称
        - color : 标签颜色
        """
        query = LabelData.update(**kwargs).where(LabelData.id == label_id)
        return query.execute()
    
    @staticmethod
    def delete_label(**kwargs):
        """
        删除标签数据
        支持参数:
        - id : 标签ID
        - name : 标签名称
        - project_id : 项目ID
        """
        query = LabelData.delete()
        conditions = []
        if 'id' in kwargs:
            conditions.append(LabelData.id == kwargs['id'])
        if 'name' in kwargs:
            conditions.append(LabelData.name == kwargs['name'])
        if 'project_id' in kwargs:
            conditions.append(LabelData.project == kwargs['project_id'])
        
        query = query.where(*conditions)
        return query.execute()
