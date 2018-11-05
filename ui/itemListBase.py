import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import fileFunctions
from lcPipe.ui.itemBase import ItemBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(10)


class ItemListBase(object):
    def __init__(self):
        self.parentWidget = None
        self.widgetName = None
        self.folderTreeWidget = None
        self.infoWidget = None
        self.itemList = []
        self.selectedItem = None
        self.type = None
        self.task = None
        self.path = None
        self.viewOption = 1
        proj = database.getProjectDict()
        self.projectName = proj['projectName']

    def createList(self, parentWidget):
        self.parentWidget = parentWidget
        form = pm.formLayout(numberOfDivisions=100)
        a = pm.scrollLayout(childResizable=True)
        self.widgetName = pm.flowLayout(p=a, backgroundColor=(.17, .17, .17), columnSpacing=5, h=1000, wrap=True)
        pm.formLayout(form, edit=True,
                      attachForm=[(a, 'left', 5), (a, 'bottom', 5),
                                  (a, 'right', 5), (a, 'top', 5)
                                  ],
                      attachControl=[],
                      attachPosition=[],
                      attachNone=())
        self.addMenus()

    def addMenus(self):
        pass

    def refreshList(self, path=None, task=None, code=None, itemMData=None):
        color = (0, 0, 0)
        x = None

        itemListProj = database.getProjectDict()

        if itemMData:
            self.path = itemMData['path']
            self.task = itemMData['task']
            self.type = itemMData['type']
        else:
            self.path = path
            self.task = task
            self.type = database.getTaskType(task[0])
            logger.debug ('task %s, type %s' % (task[0], self.type))

        collection = database.getCollection(self.type)

        if code:
            result = collection.find({'path': self.path, 'code': code})
        else:
            if self.task == ['asset']:
                result = collection.find({'path': self.path, 'task': 'model'})
            elif self.task == ['shot']:
                result = collection.find({'path': self.path, 'task': 'layout'})
            else:
                result = collection.find({'path': self.path, 'task': {'$in': self.task}})

        flowChilds = pm.flowLayout(self.widgetName, q=True, ca=True)
        if flowChilds:
            for i in flowChilds:
                pm.deleteUI(i)

        self.itemList = []
        self.selectedItem = None

        for itemMData in result:
            logger.debug(itemMData)
            if not code and (task == 'asset' or task == 'shot'):
                templateToUse = [x for x in itemListProj['assetNameTemplate'] if x != '$task']
                name = database.templateName(itemMData, template=templateToUse)
                taskLabel = task.upper()
                createdColor = (0, .2, .50)
                notCreatedColor = (0, .2, .50)
            else:
                name = database.templateName(itemMData)
                taskLabel = itemMData['task'].upper()
                notCreatedColor = (.2, .2, .2)
                createdColor = (1, .8, .20)

            status = itemMData['status']
            if status == 'notCreated':
                color = notCreatedColor
            elif status == 'created':
                color = createdColor

            thumbPath = fileFunctions.getThumb(itemMData)
            x = ItemBase(name=name, itemName=itemMData['name'], imgPath=thumbPath, label=taskLabel, status=itemMData['status'],
                         parentWidget=self, color=color)
            x.infoWidget = self.infoWidget

            if code:
                x.task = itemMData['task']
                x.workVer = itemMData['workVer']
                x.publishVer = itemMData['publishVer']
            else:
                x.task = itemMData['task']
                x.workVer = 0
                x.publishVer = 0

            x.code = itemMData['code']
            self.itemList.append(x)
            x.addToLayout(self.viewOption)


