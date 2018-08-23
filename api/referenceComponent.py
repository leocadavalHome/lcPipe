import pymel.core as pm
from lcPipe.api.component import Component
from lcPipe.api.refInfo import RefInfo
import logging
import time
logger = logging.getLogger(__name__)


"""
Class to wrap the data for a reference file component
"""
class ReferenceComponent(Component):
    def __init__(self, ns, componentMData, parent=None):
        super(ReferenceComponent, self).__init__(ns=ns, componentMData=componentMData, parent=parent)

    def addToScene(self):
        """
        Find last publish of this component and reference on the current file
        :return:
        """
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.createReference(componentPath, namespace=self.ns)

    def replaceProxyMode(self):
        # todo replace proxy mode!!
        proxyItem = self.getItem(task=self.proxyMode)

        pass

    def updateVersion(self, ref):
        """
        Check the referenceFile ref version and compare with the data on database
        :param ref:
        :return:
        """

        refInfo = RefInfo(ref)
        self.checkDBForNewVersion()

        resp = {}
        if self.ver != refInfo.ver:
            resp['ver'] = self.ver

        return resp

