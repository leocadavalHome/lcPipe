from lcPipe.api.item import Item
from lcPipe.api.refInfo import RefInfo
import logging
logger = logging.getLogger(__name__)
"""
Scene Components base class (camera, cache, reference, xlo)
"""

class Component(object):
    def __init__(self, ns, componentMData, parent=None):
        """
        :param ns: str
        :param componentMData: dict
        :param parent: api.Item
        """

        self.ns = ns
        self.parent = parent
        self.code = componentMData['code']
        self.task = componentMData['task']
        self.type = componentMData['type']
        self.ver = componentMData['ver']
        self.updateMode = componentMData['updateMode']
        self.assembleMode = componentMData['assembleMode']
        if 'xform' in componentMData:
            self.xform = componentMData['xform']
        else:
            self.xform = None
        if 'proxyMode' in componentMData:
            self.proxyMode = componentMData['proxyMode']
        else:
            self.proxyMode = None
        if 'cacheVer' in componentMData:
            self.cacheVer = componentMData['cacheVer']
        else:
            self.cacheVer = None

    def getDataDict(self):
        """
        Return a dict with this component metadata

        :return: dict
        """
        componentMData = {}
        componentMData['code'] = self.code
        componentMData['task'] = self.task
        componentMData['type'] = self.type
        componentMData['ver'] = self.ver
        componentMData['updateMode'] = self.updateMode
        componentMData['assembleMode'] = self.assembleMode
        if self.xform:
            componentMData['xform']=self.xform
        if self.proxyMode:
            componentMData['proxyMode']=self.proxyMode
        if self.cacheVer:
            componentMData['cacheVer'] = self.cacheVer

        return componentMData

    def getPath(self, dirLocation='workLocation', ext='ma'):
        """
        Return the path for this component on disk.
        dirLocation can be: workLocation, publishLocation,imagesWorkLocation, imagesPublishLocation, cacheLocation

        :param dirLocation: str
        :param ext: str
        :return: list [str, str] (dir, filename)
        """
        item = self.getItem()
        return item.getPath(dirLocation=dirLocation, ext=ext)

    def getItem(self):
        """
        Return the Item this component points to

        :return: api.Item
        """
        return Item(task=self.task, code=self.code, itemType=self.type)

    def putToParent(self):
        """
        Update the info of this component on the parent Item instance

        :return:
        """
        self.parent.components[self.ns] = self.getDataDict()

    def checkDBForNewVersion(self):
        """
        Update version info on the database for this component

        :return:
        """
        item = self.getItem()
        if self.ver != item.publishVer:
            if self.updateMode == 'last':
                self.ver = item.publishVer
                logger.info('version %s updated to %s' % (self.ver, item.publishVer))
            else:
                self.ver = int(self.updateMode)
            self.putToParent()
        else:
            logger.info ('version %s ok' % self.ver)
        self.parent.putDataToDB()

    def getPublishPath(self):
        """
        Return the publish path for this component on disk.

        :return: str
        """
        item = self.getItem()
        return item.getPublishPath()

    def addToScene(self):
        pass

    def updateVersion(self, ref):
        """
        Check the scene reference Ref against this component version

        :param ref: pymel.fileReference
        :return: dict
        """
        refInfo = RefInfo(ref)
        self.checkDBForNewVersion()

        resp = {}
        if self.ver != refInfo.ver:
            resp['ver'] = self.ver

        if self.cacheVer != refInfo.cacheVer:
            resp['cacheVer'] = self.cacheVer

        return resp