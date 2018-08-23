import pymel.core as pm
import os.path
from lcPipe.api.source import Source
from lcPipe.api.component import Component
from lcPipe.core import database
from lcPipe.api.item import Item
from lcPipe.api.refInfo import RefInfo
import logging
logger = logging.getLogger(__name__)


class XloComponent(Component):
    def __init__(self, ns, xloMData, parent=None):
        super(XloComponent, self).__init__(ns=ns, componentMData=xloMData, parent=parent)

    def getSourceItem(self):
        ns = [x for x in self.parent.source][0]
        source = Source(ns, self.parent.source[ns], parent = self.parent)
        return source.getItem()

    def getItem(self):
        if self.ns != 'cam':
            return Item(task='xlo', code=self.code, itemType=self.type)
        else:
            return Item (task='rig', code=self.code, itemType=self.type)

    def checkDBForNewCacheVersion(self):
        sourceItem = self.getSourceItem()
        if sourceItem.caches:
            cacheMDataOnSource = sourceItem.caches[self.ns]

            if cacheMDataOnSource['cacheVer'] == 0:
                logger.warn('checkVersions: Cache not yet published!!')
                return

            if self.cacheVer != cacheMDataOnSource['cacheVer']:
                self.cacheVer = cacheMDataOnSource['cacheVer']
                logger.info('cache version %s updated to %s' % (self.cacheVer, cacheMDataOnSource['cacheVer']))
            else:
                logger.info('cache version %s ok' % self.cacheVer)
            self.putToParent()
        else:
            logger.warn('No caches in source!!')
        self.parent.putDataToDB()

    def getCachePublishPath(self, make=False):
        item = self.getItem()
        path = item.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        if make:
            if not os.path.exists(cachePath):
                os.makedirs(cachePath)

        ver = 'v%03d_' % self.cacheVer
        cacheName = database.templateName(self.getDataDict()) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)

    def addToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.createReference(componentPath, namespace=self.ns)

    def updateVersion(self, ref):
        refInfo = RefInfo(ref)
        self.checkDBForNewVersion()
        self.checkDBForNewCacheVersion()

        resp = {}
        if self.ver != refInfo.ver:
            resp['ver'] = self.ver

        if self.cacheVer != refInfo.cacheVer:
            resp['cacheVer'] = self.cacheVer

        return resp