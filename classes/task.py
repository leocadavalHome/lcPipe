class Task(object):
    def __init__(self, projectName=None, task=None, code=None, itemType=None, fromScene=False):

        self.projectName = projectName
        self.code = code
        self.task = task
        self.type = itemType
        self.name = None

        self.workflow = None
        self.projPrefix = None
        self.path = []
        self.filename = None
        self.frameRange = []

        self.status = None
        self.workVer = None
        self.publishVer = None
        self.source = {}
        self.components = {}
        self.caches = {}
        self.noData = True
        self.customData = {}
        self.fromScene = fromScene

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


