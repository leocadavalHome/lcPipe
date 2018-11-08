import copy
from lcPipe.classes.component import Component
from lcPipe.classes.componentFile import ComponentFile
import logging

logger = logging.getLogger(__name__)


class Task(object):
    def __init__(self, projectName=None, _id=None, code=None, task=None, itemType=None, name=None, path=None,
                 workflow=None, frameRange=None, customData=None, status=None, workVer=0, publishVer=0,
                 source=None, components=None, caches=None):

        self.projectName = projectName
        self.code = code
        self.task = task
        self.itemType = itemType
        self.name = name

        self.workflow = workflow
        self.path = path

        self.frameRange = frameRange
        self.customData = customData

        self.status = status
        self.workVer = workVer
        self.publishVer = publishVer
        self.source = source
        self.components = components
        self.caches = caches

    def _validate(self):
        pass

    def getTaskDict(self):
        return self.__dict__

    #components
    def listComponents(self):
        return self.components

    def readComponent(self, ns=None):
        return Component(**self.components[ns])

    def createComponent(self, ns=None, **componentDict):
        if ns in self.components:
            logger.error('Namespace %s already exists' % ns)
            return
        else:
            comp = Component(ns=ns, **componentDict)
            noNSDict = copy.deepcopy(comp.__dict__)
            del (noNSDict['ns'])
            self.components[ns] = noNSDict
            return comp

    def deleteComponent(self, ns=None):
        del (self.components[ns])

    def updateComponent(self, ns=None, **componentDict):
        if ns in self.components:
            self.components[ns].update(componentDict)
        else:
            logger.error('Component %s non existent' % ns)

    #itemFile
    def createTaskFile(self, location):
        compFile = ComponentFile(path)


