from lcPipe.api.component import Component
from lcPipe.core import database
import os.path
from lcPipe.api.item import Item

class XloComponent(Component):
    def __init__(self, ns, xloMData, parent=None):
        super(XloComponent, self).__init__(ns=ns, componentMData=xloMData, parent=parent)

    def getItem(self):
        return Item(task='xlo', code=self.code, itemType=self.type)

    def getCachePublishPath (self):
        item = self.getItem()
        path = item.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        ver = 'v%03d_' % self.cacheVer
        cacheName = database.templateName(self.getDataDict) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)