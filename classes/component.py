import logging

logger = logging.getLogger(__name__)

class Component(object):
    def __init__(self, ns=None, code=None, task=None, itemType=None, version=None, updateMode=None,
                 assembleMode=None, onSceneParent=None, xform=None, proxyMode=None, cacheVer=None):

        self.ns = ns
        self.code = code
        self.task = task
        self.itemType = itemType
        self.version = version
        self.updateMode = updateMode
        self.assembleMode = assembleMode
        self.onSceneParent = onSceneParent
        self.xform = xform
        self.proxyMode = proxyMode
        self.cacheVer = cacheVer

    def _validate(self):
        pass

    def updateVersion(self):
        pass

    def updateCacheVersion(self):
        pass

    #itemFile
    def getComponentFile(self):
        pass