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
        return __dict__

    #components
    def listComponents(self):
        return self.components

    def readComponent(self):
        pass

    def createComponent(self):
        pass

    def deleteComponent(self):
        pass

    def updateComponent(self):
        pass

    #itemFile
    def getItemFile(self):
        pass


