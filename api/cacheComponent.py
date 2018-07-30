from lcPipe.api.component import Component
from lcPipe.api.source import Source
from lcPipe.api.refInfo import RefInfo
from lcPipe.core import database
import pymel.core as pm
import os.path


class CacheComponent(Component):
    def __init__(self, ns, cacheMData, parent=None):
        super(CacheComponent, self).__init__(ns=ns, componentMData=cacheMData, parent=parent)

    def getSourceItem(self):
        ns = [x for x in self.parent.source][0]
        source = Source(ns, self.parent.source[ns], parent = self.parent)
        return source.getItem()

    def getPublishPath(self, make=False):
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
        sourceItem = self.getSourceItem()
        if sourceItem.caches:
            cacheMDataOnSource = sourceItem.caches[self.ns]

            if cacheMDataOnSource['cacheVer'] == 0:
                print 'checkVersions: Cache not yet published!!'
                return

            if self.cacheVer != cacheMDataOnSource['cacheVer']:
                self.cacheVer = cacheMDataOnSource['cacheVer']
                print 'cache version %s updated to %s' % (self.cacheVer, cacheMDataOnSource['cacheVer'])
            else:
                print 'cache version %s ok' % self.cacheVer
            self.putToParent()
        else:
            print 'No caches in source!!'
        self.parent.putDataToDB()


    def addToScene(self):
        cacheFullPath = self.getPublishPath()
        pm.createReference(cacheFullPath, namespace=self.ns, groupReference=True, groupName='geo_group', type='Alembic')

    def importCache(self):
        cacheFullPath = self.getPublishPath()
        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')

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
        if self.cacheVer != refInfo.cacheVer:
            resp['cacheVer'] = self.cacheVer

        return resp