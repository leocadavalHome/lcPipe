class Item(object):
    def __init__(self, projectName=None, code=None, itemType=None, name=None, path=None, workflow=None, frameRange=None):

        self.projectName = projectName
        self.code = code
        self.type = itemType
        self.name = name
        self.workflow = workflow
        self.path = path
        self.status = None
        self.frameRange = frameRange
        self.task = 'item'

    def _validate(self):
        pass

    def getItemDict(self):
        pass

    #components
    def listComponents(self):
        pass

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


