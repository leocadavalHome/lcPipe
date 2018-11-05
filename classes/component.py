class Component(object):
    def __init__(self, ns, componentMData, parent=None):

        self.ns = ns
        self.parent = parent
        self.code = componentMData['code']
        self.task = componentMData['task']
        self.type = componentMData['type']
        self.version = componentMData['version']
        self.updateMode = componentMData['updateMode']
        self.assembleMode = componentMData['assembleMode']
        self.onSceneParent = componentMData['onSceneParent']
        self.xform = componentMData['xform']
        self.proxyMode = componentMData['proxyMode']

        if 'cacheVer' in componentMData:
            self.cacheVer = componentMData['cacheVer']
        else:
            self.cacheVer = None

    def _validadte(self):
        pass

    def updateVersion(self):
        pass

    def updateCacheVersion(self):
        pass

    #itemFile
    def getComponentFile(self):
        pass