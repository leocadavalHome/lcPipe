import pymel.core as pm
import os.path
from lcPipe.core import database


class Item(object):
    def __init__(self, projName=None, task=None, code=None, itemType=None, fromScene=False):

        self.projectName = projName
        self.fromScene = fromScene
        self.code = code
        self.task = task
        self.type = itemType
        self.name = None
        self.workflow = None
        self.projPrefix = None
        self.workVer = None
        self.publishVer = None
        self.path = []
        self.filename = None
        self.status = None
        self.source = {}
        self.components = {}
        self.caches = {}

        if not self._getDataFromDB():
            raise Exception("The item found no data")

    def _getDataFromDB(self):
        itemMData = database.getItemMData(projName=self.projectName, task=self.task, code=self.code,
                                          itemType=self.type, fromScene=self.fromScene)
        if not itemMData:
            return False

        self.name = itemMData['name']
        self.code = itemMData['code']
        self.task = itemMData['task']
        self.type = itemMData['type']
        self.workflow = itemMData['workflow']
        self.projPrefix = itemMData['projPrefix']
        self.workVer = itemMData['workVer']
        self.publishVer = itemMData['publishVer']
        self.path = itemMData['path']
        self.filename = itemMData['filename']
        self.status = itemMData['status']
        self.source = itemMData['source']
        self.components = itemMData['components']

        if 'caches' in itemMData:
            self.caches = itemMData['caches']

        return True

    def _putDataToDB(self):
        try:
            database.putItemMData(itemMData=self.getDataDict(), projName=self.projectName, task=self.task,
                                  code=self.code, itemType=self.type)
        except:
            raise Exception('Item Class: problem writing to database')


    def getDataDict(self):
        itemMData={}
        itemMData['name'] = self.name
        itemMData['code'] = self.code
        itemMData['task'] = self.task
        itemMData['type'] = self.type
        itemMData['workflow'] = self.workflow
        itemMData['projPrefix'] = self.projPrefix
        itemMData['workVer'] = self.workVer
        itemMData['publishVer'] = self.publishVer
        itemMData['path'] = self.path
        itemMData['filename'] = self.filename
        itemMData['status'] = self.status
        itemMData['source'] = self.source
        itemMData['components'] = self.components

        if 'caches' in itemMData:
            itemMData['caches'] = self.caches

        return itemMData

    def getPath(self, dirLocation='workLocation', ext='ma'):
        project = database.getProjectDict(self.projectName)
        location = project[dirLocation]
        taskFolder = self.task
        folderPath = os.path.join(*self.path)
        phase = project['workflow'][self.workflow][self.task]['phase']
        filename = self.filename

        if ext:
            ext = '.' + ext

        else:
            ext = ''

        dirPath = os.path.join(location, phase, taskFolder, folderPath)
        filename = filename + ext

        return dirPath, filename

    def getPublishPath (self):
        path = self.getPath(dirLocation='publishLocation')
        version = 'v%03d_' % self.publishVer
        return os.path.join(path[0], version + path[1])

    def getWorkPath(self):
        path = self.getPath()
        return os.path.join(*path)

    def open(self):
        pm.openFile(self.getWorkPath(), f=True)

    def publish(self):
        originalName = pm.sceneName()

        self.publishVer += 1

        fullPath = self.getPublishPath()
        dirPath = self.getPath(dirLocation='publishLocation')[0]
        if not os.path.exists(dirPath):
            print ('creating:' + dirPath)
            os.makedirs(dirPath)

        # save scene
        pm.saveAs(fullPath)
        pm.renameFile(originalName)
        self._putDataToDB()

    def restoreVersion(self, version):
        pass

    def moveFiles(self, newPath):
        pass

    def removeFiles (self, publishes=True, restore=True):
        pass
