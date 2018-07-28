from lcPipe.core import database

class RefInfo (object):
    def __init__(self, ref):

        self.ref = ref
        self.task = None
        self.code = None
        self.ver = None
        self.cacheVer = None
        self.wrapData()

    def wrapData(self):
        refInfo = database.referenceInfo(self.ref)
        self.task = refInfo['task']
        self.code = refInfo['code']
        self.ver = refInfo['ver']
        self.cacheVer = refInfo['cacheVer']