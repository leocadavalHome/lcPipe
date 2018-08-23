from lcPipe.api.component import Component
from lcPipe.api.source import Source
from lcPipe.api.refInfo import RefInfo
from lcPipe.core import database
import pymel.core as pm
import os.path
import logging
logger = logging.getLogger(__name__)

"""
Wraper for a cache scene component
"""

class CacheComponent(Component):

    def __init__(self, ns, cacheMData, parent=None):
        super(CacheComponent, self).__init__(ns=ns, componentMData=cacheMData, parent=parent)

    def getSourceItem(self):
        """
        Return the source item that generate the cache

        :return: api.Item
        """
        ns = [x for x in self.parent.source][0]
        source = Source(ns, self.parent.source[ns], parent = self.parent)
        return source.getItem()

    def getPublishPath(self, make=False):
        """
        Return the publish path for this component
        If make is true create the folder if needed

        :param make: boolean
        :return: str
        """
        proj = database.getProjectDict()
        sourceItem = self.getSourceItem()
        path = sourceItem.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        if make:
            if not os.path.exists(cachePath):
                os.makedirs(cachePath)

        ver = 'v%03d_' % self.cacheVer
        cacheName = database.templateName(self.getDataDict(), proj['cacheNameTemplate']) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)

    def checkDBForNewVersion(self):
        """
        Update version info on the database for this cache

        :return:
        """
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
                logger.info ('cache version %s ok' % self.cacheVer)
            self.putToParent()
        else:
            logger.warn('No caches in source!!')
        self.parent.putDataToDB()


    def addToScene(self):
        """
        Reference this cache on the current maya scene

        :return:
        """
        cacheFullPath = self.getPublishPath()
        pm.createReference(cacheFullPath, namespace=self.ns, groupReference=True, groupName='geo_group', type='Alembic')

    def importCache(self):
        """
        Import this cache on the current maya scene
        :return:
        """
        cacheFullPath = self.getPublishPath()
        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')

    def updateVersion(self, ref):
        """
        Check the scene reference ref against this cache component info version
        Return a empty dict if the version is ok, or a dict with the updated version
        :param ref:
        :return: dict
        """
        refInfo = RefInfo(ref)
        self.checkDBForNewVersion()

        resp = {}
        if self.cacheVer != refInfo.cacheVer:
            resp['cacheVer'] = self.cacheVer

        return resp