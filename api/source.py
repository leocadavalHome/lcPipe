import pymel.core as pm
from lcPipe.api.item import Item

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

        if self.cacheVer:
            componentMData['cacheVer'] = self.cacheVer

        return componentMData

    def getItem(self):
        return Item(task=self.task, code=self.code, itemType=self.type)

    def putToParent(self):
        self.parent['components'][self.ns] = self.getDataDict()

    def checkForNewVersion(self):
        item = self.getItem()
        if self.updateMode == 'last':
            self.ver = item.publishVer
        else:
            self.ver = int(self.updateMode)
        self.putToParent()

    def addToScene(self):
        pass

    def updateOnScene(self):
        pass