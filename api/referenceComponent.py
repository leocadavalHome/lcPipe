import pymel.core as pm
from lcPipe.api.component import Component
from lcPipe.api.refInfo import RefInfo

class ReferenceComponent(Component):
    def __init__(self, ns, componentMData, parent=None):
        super(ReferenceComponent, self).__init__(ns=ns, componentMData=componentMData, parent=parent)

    def addToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.createReference(componentPath, namespace=self.ns)

    def replaceProxyMode(self):
        proxyItem = self.getItem(task=self.proxyMode)

        pass

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
        if self.ver != refInfo.ver:
            resp['ver'] = self.ver

        return resp

