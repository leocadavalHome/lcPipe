import pymel.core as pm
import pymel.core.datatypes as dt
from lcPipe.api.source import Source
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent
import logging

logger = logging.getLogger(__name__)

"""
Class of a special kind of component used on scene creation
"""
class SceneSource(Source):
    def __init__(self, ns, componentMData, parent=None):
        super(SceneSource, self).__init__(ns, componentMData, parent)

    def createGroup(self):
        logger.info('creating group')

        root = pm.group(empty=True, n=self.code)

        if len(self.xform) == 3:
            if root:
                rootGrp = pm.group(em=True, n=self.ns+':root_grp')
                cntrlGrp = pm.group(em=True, n=self.ns+':control_grp')
                transformGrp = pm.group (em=True, n=self.ns + ':transform_grp')

                pm.parent(root, transformGrp)

                bbox = transformGrp.getBoundingBox()
                radius = max(bbox.width(), bbox.depth())/2

                crv1 = pm.circle(n=self.ns+':innerControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius, d=3, ut=0, ch=0)[0]
                crv2 = pm.circle(n=self.ns+':midControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius*1.1, d=3, ut=0, ch=0)[0]
                crv3 = pm.circle(n=self.ns+':outerControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius*1.2, d=3, ut=0, ch=0)[0]

                pm.parent(crv1, crv2)
                pm.parent(crv2, crv3)
                pm.parent(crv3, cntrlGrp)
                pm.parent(cntrlGrp, transformGrp, rootGrp)

                pm.parentConstraint (crv1, transformGrp, mo=False)
                pm.scaleConstraint (crv1, transformGrp, mo=False)

                transform = self.xform['innerControl']
                pm.xform (crv1, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                transform = self.xform['midControl']
                pm.xform (crv2, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                transform = self.xform['outerControl']
                pm.xform (crv3, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])

                root = rootGrp

        elif len(self.xform) == 1:
            transform = self.xform['groupControl']
            pm.xform (root, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])

        if self.onSceneParent:
            onSceneParentSearch = pm.ls(self.onSceneParent, r=True)
            if onSceneParentSearch and len(onSceneParentSearch) == 1:
                onSceneParent = onSceneParentSearch[0]
                pm.parent(root, onSceneParent)
            else:
                logger.warn('Found no onSceneParent %s' % onSceneParentSearch)

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

        if len(self.xform) == 3:
            if roots:
                rootGrp = pm.group(em=True, n=self.ns+':root_grp')
                cntrlGrp = pm.group(em=True, n=self.ns+':control_grp')
                transformGrp = pm.group (em=True, n=self.ns + ':transform_grp')

                pm.parent (roots, transformGrp)

                bbox = transformGrp.getBoundingBox()
                radius = max(bbox.width(), bbox.depth())/2

                crv1 = pm.circle(n=self.ns+':innerControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius, d=3, ut=0, ch=0)[0]
                crv2 = pm.circle(n=self.ns+':midControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius*1.1, d=3, ut=0, ch=0)[0]
                crv3 = pm.circle(n=self.ns+':outerControl', c=(0, 0, 0), nr=(0, 1, 0), sw=360, r=radius*1.2, d=3, ut=0, ch=0)[0]

                pm.parent(crv1, crv2)
                pm.parent(crv2, crv3)
                pm.parent(crv3, cntrlGrp)
                pm.parent(cntrlGrp, transformGrp, rootGrp)

                pm.parentConstraint (crv1, transformGrp, mo=False)
                pm.scaleConstraint (crv1, transformGrp, mo=False)

                transform = self.xform['innerControl']
                pm.xform (crv1, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                transform = self.xform['midControl']
                pm.xform (crv2, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])
                transform = self.xform['outerControl']
                pm.xform (crv3, m=transform['xform'], rp=transform['rotatePivot'], sp=transform['scalePivot'])

                roots = rootGrp

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

