from lcPipe.api.component import Component
from lcPipe.api.source import Source
from lcPipe.core import database
import os.path

class CacheComponent(Component):
    def __init__(self, ns, cacheMData, parent=None):
        super(CacheComponent, self).__init__(ns=ns, componentMData=cacheMData, parent=parent)

    def getSourceItem(self):
        ns = [x for x in self.parent.source][0]
        source = Source(ns, self.parent.source[ns], parent = self.parent)
        return source.getItem()

    def getPublishPath(self):
        proj = database.getProjectDict()
        sourceItem = self.getSourceItem()
        path = sourceItem.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        ver = 'v%03d_' % self.cacheVer
        cacheName = database.templateName(self.getDataDict(), proj['cacheNameTemplate']) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)

    def checkForNewVersion(self):
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
        else:
            print 'No caches in source!!'
