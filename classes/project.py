import pymel.core as pm
import sys
import pymongo
import pymongo.errors
import logging
from lcPipe.classes.connection import MongoDBConnection
from lcPipe.classes.task import Task

logger = logging.getLogger(__name__)

class Project(object):
    def __init__(self, projectName, prefix, **projectDict):
        self.projectName = projectName
        self.prefix = prefix
        self.status = 'active'
        self.locations = {}
        self.collections = {}
        self.folders = {}
        self.templates = {}
        self.settings = {}
        self.workflows = {}

        self.setDefaultData()

        if projectDict:
            self.setProjectValues(**projectDict)

    def _validate(self):
        pass

    def getProjectDict(self):
        projDict = self.__dict__
        return projDict

    def setProjectValues(self, **projectDict):
        self.__dict__.update(**projectDict)

    #items
    def createTask(self, **taskDict):
        con = MongoDBConnection()
        taskInstance = Task(projectName=self.projectName, **taskDict)
        collection = con.db.get_collection(self.projectName + '_' + taskInstance.itemType)
        exist = collection.find_one({'task': taskInstance.task, 'code': taskInstance.code})
        if not exist:
            collection.insert_one(taskInstance.__dict__)
            return taskInstance
        else:
            logger.error('task %s already exists' % taskInstance.code)

    def readTask(self, task=None, code=None):
        con = MongoDBConnection()
        itemType = self.getTaskType(task)
        collection = con.db.get_collection(self.projectName + '_' + itemType)
        taskDict = collection.find_one({'task': task, 'code': code})
        if taskDict:
            taskInstance = Task(**taskDict)
            return taskInstance
        else:
            logger.error('Cant find task')

    def updateTask(self, taskInstance, **taskDict):
        con = MongoDBConnection()
        itemType = self.getTaskType(taskInstance.task)
        collection = con.db.get_collection(self.projectName + '_' + itemType)
        taskInstance.__dict__.update(taskDict)
        collection.find_one_and_update({'task': taskInstance.task, 'code': taskInstance.code},
                                       {'$set': taskInstance.__dict__})

    def deleteTask(self, taskInstance):
        con = MongoDBConnection()
        itemType = self.getTaskType(taskInstance.task)
        collection = con.db.get_collection(self.projectName + '_' + itemType)
        collection.delete_one({'task': taskInstance.task, 'code': taskInstance.code})


    def getTaskType(self,task):
        if task == 'asset' or task == 'shot':
            return task

        resultTasks = []
        for workflow in self.workflows.itervalues():
            for key, values in workflow.iteritems():
                if key == task:
                    resultTasks.append(values['type'])

        if resultTasks:
            return resultTasks[0]
        else:
            print 'ERROR getTaskType: no task type found!'


    def setDefaultData(self):

        self.locations = {
            'workLocation': u'D:/JOBS/PIPELINE/pipeExemple/scenes',
            'localWorkLocation': u'D:/JOBS/PIPELINE/pipeExemple/local',
            'publishLocation': u'D:/JOBS/PIPELINE/pipeExemple/publishes',
            'imagesWorkLocation': u'D:/JOBS/PIPELINE/pipeExemple/sourceimages',
            'imagesPublishLocation': u'D:/JOBS/PIPELINE/pipeExemple/publishes/sourceimages',
            'soundLocation': u'D:/JOBS/PIPELINE/pipeExemple/sound',
            'playblastLocation': u'D:/JOBS/PIPELINE/pipeExemple/movies',
            'cacheLocation': u'D:/JOBS/PIPELINE/pipeExemple/cache/alembic'
        }
        self.collections = {
                            'asset': 1,
                            'shot': 1
                            }
        self.folders = {
            'assetFolders': {'character': {'parent': ''},
                             'props': {'parent': ''},
                             'sets': {'parent': ''},
                             'primary': {'parent': 'character'}},
            'shotFolders': {'ep001': {'parent': ''},
                            'ep002': {'parent': ''},
                            'ep003': {'parent': ''},
                            'seq0001': {'parent': 'ep001'}}
        }
        self.templates = {
            'cameraNameTemplate': ['$prefix', '$code', '_', '$name'],
            'assetNameTemplate': ['$prefix', '$code', '_', '$name', '_', '$task'],
            'cacheNameTemplate': ['$prefix', '$code', '$task']
        }

        self.settings = {
            'renderer': 'vray',
            'fps': '25fps',
            'mayaVersion': '2015',
            'resolution': [1920, 1080]
        }
        self.workflows = {
            'rig': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                              'source': []},
                    'proxy': {'type': 'asset', 'phase': 'preProd', 'short': 'prx',
                              'source': []},
                    'uvs': {'type': 'asset', 'phase': 'preProd', 'short': 'uvs',
                            'source': [('model', 'import')]},
                    'blendShape': {'type': 'asset', 'phase': 'preProd', 'short': 'bsp',
                                   'source': [('model', 'import')]},
                    'texture': {'type': 'asset', 'phase': 'preProd', 'short': 'tex',
                                'source': [('uvs', 'reference')]},
                    'xlo': {'type': 'asset', 'phase': 'preProd', 'short': 'xlo',
                            'source': [('texture', 'import')]},
                    'rig': {'type': 'asset', 'phase': 'preProd', 'short': 'rig',
                            'source': [('uvs', 'reference'), ('blendShape', 'import')]}},

            'static': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                 'source': []},
                       'proxy': {'type': 'asset', 'phase': 'preProd', 'short': 'prx',
                                 'source': []},
                       'gpu': {'type': 'asset', 'phase': 'preProd', 'short': 'gpu',
                               'source': [('model', 'reference')]},
                       'uvs': {'type': 'asset', 'phase': 'preProd', 'short': 'uvs',
                               'source': [('model', 'import')]},
                       'texture': {'type': 'asset', 'phase': 'preProd', 'short': 'tex',
                                   'source': [('uvs', 'reference')]},
                       'xlo': {'type': 'asset', 'phase': 'preProd', 'short': 'xlo',
                               'source': [('texture', 'import')]}},

            'group': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                'source': []},
                      'proxy': {'type': 'asset', 'phase': 'preProd', 'short': 'prx',
                                'source': []},
                      'gpu': {'type': 'asset', 'phase': 'preProd', 'short': 'gpu',
                              'source': [('model', 'reference')]}},

            'camera': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                 'source': []},
                       'rig': {'type': 'asset', 'phase': 'preProd', 'short': 'rig', 'source': []}},

            'shotCache': {'layout': {'type': 'shot', 'phase': 'prod', 'short': 'lay', 'source': [],
                                     'components': {}},
                          'animation': {'type': 'shot', 'phase': 'prod', 'short': 'ani',
                                        'source': [('layout', 'copy')]},
                          'render': {'type': 'shot', 'phase': 'postProd', 'short': 'rnd',
                                     'source': [('shotFinalizing', 'cache')]},
                          'shotFinalizing': {'type': 'shot', 'phase': 'prod', 'short': 'sfh',
                                             'source': [('animation', 'copy')]}},

            'shotXlo': {'layout': {'type': 'shot', 'phase': 'prod', 'short': 'lay', 'source': [],
                                   'components': {}},
                        'animation': {'type': 'shot', 'phase': 'prod', 'short': 'ani',
                                      'source': [('layout', 'copy')]},
                        'render': {'type': 'shot', 'phase': 'postProd', 'short': 'rnd',
                                   'source': [('shotFinalizing', 'xlo')]},
                        'shotFinalizing': {'type': 'shot', 'phase': 'prod', 'short': 'sfh',
                                           'source': [('animation', 'copy')]}}
        }