from lcPipe.api.item import Item
import logging
logger = logging.getLogger(__name__)


class Source(object):
    def __init__(self, ns, sourceMData, parent=None):
        self.ns = ns
        self.parent = parent
        self.code = sourceMData['code']
        self.task = sourceMData['task']
        self.type = sourceMData['type']
        self.ver = sourceMData['ver']
        self.updateMode = sourceMData['updateMode']
        self.assembleMode = sourceMData['assembleMode']
        if 'xform' in sourceMData:
            self.xform = sourceMData['xform']
        else:
            self.xform = None
        if 'proxyMode' in sourceMData:
            self.proxyMode = sourceMData['proxyMode']
        else:
            self.proxyMode = None
        if 'cacheVer' in sourceMData:
            self.cacheVer = sourceMData['cacheVer']
        else:
            self.cacheVer = None

    def getDataDict(self):
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

    def getItem(self):
        return Item(task=self.task, code=self.code, itemType=self.type)

    def putToParent(self):
        item = self.getItem()
        item.components[self.ns] = self.getDataDict()

    def checkForNewVersion(self):
        item = self.getItem()
        if self.ver != item.publishVer:
            if self.updateMode == 'last':
                self.ver = item.publishVer
                logger.info('version %s updated to %s' % (self.ver, item.publishVer))
            else:
                self.ver = int(self.updateMode)
            self.putToParent()
        else:
            logger.info('version %s ok' %  self.ver)
        self.parent.putDataToDB ()

    def addToScene(self):
        pass

    def updateOnScene(self):
        pass