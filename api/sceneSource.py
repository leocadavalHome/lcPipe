import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.source import Source
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent

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

        return {}

    def copyToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.openFile(componentPath, force=True)

        return item.components

    def addCacheToScene(self):
        item = self.getItem()
        for cache_ns, cacheMData in item.caches.iteritems():
            cache = CacheComponent(cache_ns, cacheMData, item)

            if cache.cacheVer == 0:
                print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
                continue

            cacheFullPath = cache.getPublishPath()
            pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True,
                               groupName='geo_group', type='Alembic')

        return item.caches

    def addXloToScene(self):
        item = self.getItem()

        for xlo_ns, xloMData in item.components.iteritems():
            xlo = XloComponent (xlo_ns, xloMData, item)

            if xlo.code == '9999':
                xloMData = database.getItemMData (task=xlo['task'], code=xlo['code'], itemType=xlo['type'])
            else:
                xloMData = database.getItemMData (task='xlo', code=xlo['code'], itemType=xlo['type'])

            if xloMData['publishVer'] == 0:
                print 'Component %s not yet published!!' % (xlo_ns + ':' + xloMData['task'] + xloMData['code'])
                parcial = True
                continue
            else:
                version = 'v%03d_' % xloMData['publishVer']

            empty = False
            path = database.getPath (xloMData, dirLocation='publishLocation')
            xloPath = os.path.join (path[0], version + path[1])
            pm.createReference (xloPath, namespace=xlo_ns)


        for cache_ns, cacheMData in item.caches.iteritems():
            cache = CacheComponent(cache_ns, cacheMData, item)

            if cache.cacheVer == 0:
                print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
                continue

            cacheFullPath = cache.getPublishPath()
            pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')

        return item.caches

