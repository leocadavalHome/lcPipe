from lcPipe.api.item import Item
from lcPipe.api.refInfo import RefInfo

class Component(object):
    def __init__(self, ns, componentMData, parent=None):
        self.ns = ns
        self.parent = parent
        self.code = componentMData['code']
        self.task = componentMData['task']
        self.type = componentMData['type']
        self.ver = componentMData['ver']
        self.updateMode = componentMData['updateMode']
        self.assembleMode = componentMData['assembleMode']

        if 'cacheVer' in componentMData:
            self.cacheVer = componentMData['cacheVer']
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

    def getPath(self, dirLocation='workLocation', ext='ma'):
        item = self.getItem()
        return item.getPath(dirLocation=dirLocation, ext=ext)

    def getItem(self):
        return Item(task=self.task, code=self.code, itemType=self.type)

    def putToParent(self):
        self.parent.components[self.ns] = self.getDataDict()

    def checkDBForNewVersion(self):
        item = self.getItem()
        if self.ver != item.publishVer:
            if self.updateMode == 'last':
                self.ver = item.publishVer
                print 'version %s updated to %s' % (self.ver, item.publishVer)
            else:
                self.ver = int(self.updateMode)
            self.putToParent()
        else:
            print 'version %s ok' % self.ver
        self.parent.putDataToDB()

    def getPublishPath (self):
        item = self.getItem()
        return item.getPublishPath()

    def addToScene(self):
        pass

    def updateVersion(self, ref):
        refInfo = RefInfo(ref)
        self.checkDBForNewVersion()

        if self.code != refInfo.code:
            print self.code
            print refInfo.code

        if self.task != refInfo.task:
            print self.task
            print refInfo.task

        resp = {}
        if self.ver != refInfo.ver:
            resp['ver'] = self.ver

        if self.cacheVer != refInfo.cacheVer:
            resp['cacheVer'] = self.cacheVer

        return resp