from api.component import Component

class CacheComponet(Component):
    def __init__(self, ns, cacheMData, parent=None):
        super(CacheComponet, self).__init__(ns=ns, sourceMData=cacheMData, parent=parent)

    def getPublishPath (self):
        path = self.parent.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        ver = 'v%03d_' % self.cacheVer
        cacheName = database.templateName(self.getDataDict) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)