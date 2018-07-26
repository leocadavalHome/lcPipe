import pymel.core as pm
import os.path
from api.source import Source
from core import database

class SceneSource(Source):
    def __init__(self, ns, componentMData, parent=None):
        super(SceneSource, self).__init__(ns, componentMData, parent)

    def addReferenceToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.createReference(componentPath, namespace=self.ns)

        newComponentDict = {'code': self.code, 'ver': item.publishVer, 'updateMode': self.updateMode,
                            'task': self.task, 'assembleMode': self.assembleMode, 'type': self.type}

        return newComponentDict

    def importToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.importFile(componentPath, defaultNamespace=True)

        newComponentDict = {}

        return newComponentDict

    def copyToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.openFile(componentPath, force=True)

        newComponentDict = item.components

        return newComponentDict

    def addCacheToScene(self):
        item = self.getItem()

        path = item.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        for cache_ns, cacheMData in item.caches.iteritems():
            cache = CacheComponet(cache_ns, cacheMData, item)

            if cache.cacheVer == 0:
                print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
                continue

            ver = 'v%03d_' % cacheMData['cacheVer']
            cacheName = database.templateName(cacheMData) + '_' + cache_ns
            cacheFileName = ver + cacheName + '.abc'
            cacheFullPath = os.path.join(cachePath, cacheFileName)

            pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True,
                               groupName='geo_group', type='Alembic')

        newComponentsDict = item.caches

        return newComponentsDict