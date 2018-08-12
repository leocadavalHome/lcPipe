import pymel.core as pm
from lcPipe.api.source import Source
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent
import logging
logger = logging.getLogger(__name__)


class SceneSource(Source):
    def __init__(self, ns, componentMData, parent=None):
        super(SceneSource, self).__init__(ns, componentMData, parent)

    def addReferenceToScene(self):
        logger.info('addRefs')
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.createReference(componentPath, namespace=self.ns)

        newComponentDict = {'code': self.code, 'ver': item.publishVer, 'updateMode': self.updateMode,
                            'task': self.task, 'proxyMode': "", 'assembleMode': self.assembleMode, 'type': self.type}

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
            cache = CacheComponent(cache_ns, cacheMData, self.parent)

            if cache.cacheVer == 0:
                logger.warn('Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code']))
                continue

            cacheFullPath = cache.getPublishPath()
            if cache_ns != 'cam':
                pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True,
                                    groupName=cache_ns+':geo_group', type='Alembic')
            else:
                pm.AbcImport(cache.getPublishPath (), mode='import', fitTimeRange=True, setToStartFrame=True,connect='/')

        return item.caches

    def addXloToScene(self):
        item = self.getItem()
        for xlo_ns, xloMData in item.components.iteritems():
            if xlo_ns =='cam':
                continue

            task = xloMData['task']
            xloMData['task'] = 'xlo'
            xlo = XloComponent(xlo_ns, xloMData, parent=self.parent)

            if xlo.ver == 0:
                logger.warn ('Component %s not yet published!!' % (xlo_ns + ':' + xlo.task + xlo.code))
                continue

            pm.createReference(xlo.getPublishPath(), namespace=xlo_ns)
            item.components[xlo_ns]['assembleMode'] = 'xlo'
            item.components[xlo_ns]['task'] = task

        for cache_ns, cacheMData in item.caches.iteritems():
            cache = CacheComponent(cache_ns, cacheMData, self.parent)

            if cache.cacheVer == 0:
                logger.warn ('Component %s not yet published!!' % (cache_ns + ':' + cache.task+ cache.code))
                continue

            pm.AbcImport(cache.getPublishPath(), mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')
            item.components[cache_ns]['cacheVer'] = cache.cacheVer

        return item.components

