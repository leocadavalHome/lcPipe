import pymel.core as pm
import os.path
from lcPipe.core import database
import logging
logger = logging.getLogger(__name__)

"""
Item base class, a task of an asset or shot.
"""
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
        self.frameRange = []
        self.source = {}
        self.components = {}
        self.caches = {}
        self.noData = True
        self.customData = {}

        if self._getDataFromDB():

            self.noData=False
        else:
            logger.warn("The item found no data %s %s %s %s" % (self.projectName, self.task, self.code, self.type))


    def _getDataFromDB(self):
        """
        get data from the database and initialize values on object variables
        :return:
        """
        itemMData = database.getItemMData(projName=self.projectName, task=self.task, code=self.code,
                                          itemType=self.type, fromScene=self.fromScene)

        if not itemMData:
            return False
        try:
            self.name = itemMData['name']
            self.code = itemMData['code']
            self.task = itemMData['task']
            self.type = itemMData['type']
            self.proxyMode = ''
            self.workflow = itemMData['workflow']
            self.projPrefix = itemMData['projPrefix']
            self.workVer = itemMData['workVer']
            self.publishVer = itemMData['publishVer']
            self.path = itemMData['path']
            self.filename = itemMData['filename']
            self.status = itemMData['status']
            self.source = itemMData['source']
            self.frameRange = itemMData['frameRange']
            self.components = itemMData['components']
            self.customData = itemMData['customData']
            if 'caches' in itemMData:
                self.caches = itemMData['caches']
        except:
            return False

        return True

    def putDataToDB(self):
        """
        write object data on database
        :return:
        """
        try:
            database.putItemMData(itemMData=self.getDataDict(), projName=self.projectName, task=self.task,
                                  code=self.code, itemType=self.type)
        except:
            raise Exception('Item Class: problem writing to database')


    def getDataDict(self):
        """
        Return object data in a dictionary form
        :return: itemMData dictionary
        """
        itemMData={}
        try:
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
            itemMData['frameRange'] = self.frameRange
            itemMData['components'] = self.components
            itemMData['customData'] = self.customData
            if self.caches:
                itemMData['caches'] = self.caches
        except:
            logger.error('Cant get dataDict')

        return itemMData

    def getPath(self, dirLocation='workLocation', ext='ma'):
        """
        Return object respective diretory and file name, based on dirLocation parameter and extention parameter.
        Valid values for diLocation are: "workLocation","publishLocation", "cacheLocation",
        "imagesWorkLocation", "imagesPublishLocation"
        Extension parameter typically take maya file extensions, "ma", "abc" or image file extensions, "jpg", "gif", etc
        :param dirLocation: string
        :param ext: string (no point)
        :return: list [ dirPath, filename]
        """
        project = database.getProjectDict(self.projectName)
        location = project[dirLocation]
        taskFolder = self.task
        folderPath = os.path.join(*self.path)
        phase = project['workflow'][self.workflow][self.task]['phase']
        filename = self.filename
        proxyMode = self.proxyMode

        if ext:
            ext = '.' + ext

        else:
            ext = ''

        dirPath = os.path.join(location, phase, taskFolder, folderPath, filename, proxyMode)
        filename = filename + ext

        return dirPath, filename

    def getPublishPath (self, make=False):
        """
        Return publish path for this item. If make is true it will create the directory if it doesnt exist
        :param make:  Boolean
        :return: string
        """
        path = self.getPath(dirLocation='publishLocation')

        if make:
            if not os.path.exists(path[0]):
                os.makedirs(path[0])

        version = 'v%03d_' % self.publishVer
        return os.path.join(path[0], version + path[1])

    def getServerWorkPath(self, make=False):
        """
        Return the work path for this item. If make is true, it will create the directory if it doesnt exist
        :param make: Boolean
        :return: String
        """
        path = self.getPath()

        if make:
            if not os.path.exists(path[0]):
                os.makedirs(path[0])

        return os.path.join(*path)

    def getLocalWorkPath(self, make=False):
        """
        Return the work path for this item. If make is true, it will create the directory if it doesnt exist
        :param make: Boolean
        :return: String
        """
        path = self.getPath(dirLocation='localWorkLocation')

        if make:
            if not os.path.exists(path[0]):
                os.makedirs(path[0])

        return os.path.join(*path)


    def openServer(self):
        """
        open the file on disk relative to this item
        :return:
        """
        pm.openFile(self.getServerWorkPath(), f=True)

    def saveAsServer(self):
        """
        Save the currently open as a version of this item
        :return:
        """
        fileName = self.getServerWorkPath(make=True)
        pm.saveAs(fileName)

    def saveAsLocal(self):
        fileName = self.getLocalWorkPath(make=True)
        pm.saveAs(fileName)

    def publish(self):
        """
        Publish the current file on the publish directory and update version
        :return:
        """
        originalName = pm.sceneName()

        self.publishVer += 1

        fullPath = self.getPublishPath(make=True)

        # save scene
        pm.saveAs(fullPath)
        pm.renameFile(originalName)
        self.putDataToDB()

    def restoreVersion(self, version):
        pass

    def moveFiles(self, newPath):
        pass

    def removeFiles (self, publishes=True, restore=True):
        pass
