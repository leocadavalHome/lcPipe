import pymel.core as pm
import pymel.core.datatypes as dt
from lcPipe.api.source import Source
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent
import logging


logger = logging.getLogger(__name__)
logger.setLevel(10)

"""
Class of a special kind of component used on scene creation
"""
class SceneSource(Source):
    def __init__(self, ns, componentMData, parent=None):
        super(SceneSource, self).__init__(ns, componentMData, parent)

    def createGroup(self):
        logger.info('creating group')

        root = pm.group(empty=True, n=self.code)

        if self.onSceneParent:
            onSceneParentSearch = pm.ls(self.onSceneParent, r=True)
            if onSceneParentSearch and len(onSceneParentSearch) == 1:
                onSceneParent = onSceneParentSearch[0]
                pm.parent(root, onSceneParent)
            else:
                logger.warn('Found no onSceneParent %s' % onSceneParentSearch)

        if self.xform:
            n = dt.Matrix()
            n.setToIdentity()
            for transform in self.xform.itervalues():
                logger.debug(self.xform)
                logger.debug(transform)
                tempNode = pm.group(empty=True)
                pm.xform(tempNode, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                m = tempNode.getMatrix()
                n = n * m
                pm.delete(tempNode)

            #workaround to transform groupAssets
            root.setTransformation(n)



    def addReferenceToScene(self):
        """
        Reference this source on the current file. If there is transformation data, it will also transform the root
        :return: dictionary with the new added component
        """
        logger.info('addRefs')

        item = self.getItem()
        componentPath = item.getPublishPath()

        pm.createReference(componentPath, namespace=self.ns)

        refFile = pm.FileReference(namespace=self.ns)
        nodes = refFile.nodes()
        subRefs = pm.ls(refFile.nodes(), type='reference')
        for x in subRefs:
            nodes += x.nodes()
        roots = pm.ls(nodes, assemblies=True)

        if self.xform:
            if roots:
                n = dt.Matrix()
                n.setToIdentity()
                for transform in self.xform.itervalues():
                    tempNode = pm.group(empty=True)
                    pm.xform(tempNode, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                    m = tempNode.getMatrix()
                    n = n * m
                    pm.delete(tempNode)

                #workaround to transform groupAssets
                originalPar = roots[0].getParent()
                root = pm.group(roots)
                root.setTransformation(n)
                pm.parent(roots, originalPar)
                pm.delete(root)

        if self.onSceneParent:
            onSceneParentSearch = pm.ls(self.onSceneParent, r=True)
            if onSceneParentSearch and len(onSceneParentSearch) == 1:
                onSceneParent = onSceneParentSearch[0]
                pm.parent(roots, onSceneParent, r=True)
            else:
                logger.warn('Found no onSceneParent')

        newComponentDict = {'code': self.code, 'ver': item.publishVer, 'updateMode': self.updateMode,
                            'task': self.task, 'proxyMode': self.proxyMode, 'xform': self.xform,
                            'onSceneParent': self.onSceneParent, 'assembleMode': self.assembleMode, 'type': self.type}

        return newComponentDict

    def importToScene(self):
        """
        Import this source to the current file.
        :return:
        """
        item = self.getItem()
        componentPath = item.getPublishPath()
        nodes = pm.importFile(componentPath, defaultNamespace=True)
        root = pm.ls(nodes, assemblies=True)

        if self.xform:
            if root and len(root) == 1:
                n = dt.Matrix()
                n.setToIdentity()
                for transform in self.xform.itervalues():
                    tempNode = pm.group(empty=True)
                    pm.xform(tempNode, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                    m = tempNode.getMatrix ()
                    n = n * m
                    pm.delete(tempNode)
                root.setTransformation (n)

        return {}

    def copyToScene(self):
        """
        Open this source as the current file. Used to copy one item to another
        :return:
        """
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.openFile(componentPath, force=True)

        return item.components

    def addCacheToScene(self):
        """
        Add alembic cache to the current file
        :return:
        """
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

