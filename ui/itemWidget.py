import pymel.core as pm
from lcPipe.core import assemble
from lcPipe.core import database
from lcPipe.core import publish
from lcPipe.core import version
import shotManager

reload(database)
reload(publish)
reload(assemble)
reload(version)


### INTERFACE
class ItemWidget(object):
    def __init__(self, name, imgPath, label, parentWidget, color=(0, .2, .50)):
        self.widgetName = None
        self.parentWidget = parentWidget

        self.infoWidget = None

        self.name = name
        self.label = label
        self.imgPath = imgPath
        self.color = color

        self.selected = False
        self.task = None
        self.code = None
        self.publishVer = 0
        self.workVer = 0

    def getItem(self):
        projName = self.parentWidget.projectName

        type = database.getTaskType(self.task)
        collection = database.getCollection(type, projName)

        if self.task == 'asset':
            searchTask = 'model'
        elif self.task == 'shot':
            searchTask = 'layout'
        else:
            searchTask = self.task

        item = collection.find_one({'task': searchTask, 'code': self.code})
        return item

    def dClickCallBack(self, *args):
        if self.task == 'asset' or self.task == 'shot':
            self.parentWidget.refreshList(path=self.parentWidget.path, task=self.task, code=self.code)

    def clickCallBack(self, *args):
        if self.selected:
            pm.iconTextButton(self.name, e=True, backgroundColor=self.color)
            self.parentWidget.selectedItem = None
            self.selected = False
        else:
            if self.parentWidget.selectedItem:
                pm.iconTextButton(self.parentWidget.selectedItem.name, e=True,
                                  backgroundColor=self.parentWidget.selectedItem.color)
                self.parentWidget.selectedItem.selected = False
            pm.iconTextButton(self.name, e=True, backgroundColor=(.27, .27, .27))
            self.parentWidget.selectedItem = self
            self.selected = True
            if self.infoWidget:
                self.infoWidget.putInfo(self)

    def dragCallback(self, dragControl, x, y, modifiers):
        return [self.task, self.code]

    def removeCallback(self, *args):
        print 'remove Item'
        type = database.getTaskType(self.task)
        database.removeItem(type, self.code)
        pm.evalDeferred('cmds.deleteUI("' + self.widgetName + '")')
        self.parentWidget.itemList.remove(self)

    def openCallback(self, *args):
        print 'open'
        projName = self.parentWidget.projectName
        item = self.getItem()
        print item

        if item['status'] == 'notCreated':
            return pm.confirmDialog(title='error', ma='center', message='This scene is not assembled yet',
                                    button=['OK'], defaultButton='OK', dismissString='OK')

        version.open(type=item['type'], task=item['task'], code=item['code'])

    def assembleCallback(self, *args):
        print 'assemble'
        item = self.getItem()
        type = database.getTaskType(self.task)
        if item['status'] == 'notCreated':
            assemble.assemble(type, self.task, self.code)
        else:
            resp = pm.confirmDialog(title='Confirm',
                                    message='This item is already assembled \n Do you want to reassemble?',
                                    button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            if resp == 'Yes':
                assemble.assemble(type, self.task, self.code)

    def shotManagerCallback(self, *args):
        item = self.getItem()
        shotMng = shotManager.ShotManager(item)
        shotMng.projectName = self.parentWidget.projectName
        shotMng.createShotManager()

    def addToLayout(self):
        self.widgetName = pm.iconTextButton(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color,
                                            style='iconAndTextHorizontal', image=self.imgPath, label=self.label, h=100,
                                            w=220, doubleClickCommand=self.dClickCallBack, command=self.clickCallBack,
                                            dragCallback=self.dragCallback)
        pm.popupMenu(parent=self.widgetName)
        if self.task == 'asset':
            pm.menuItem(label='remove asset', c=self.removeCallback)
        elif self.task == 'shot':
            pm.menuItem(label='shot manager', c=self.shotManagerCallback)
            pm.menuItem(label='remove shot', c=self.removeCallback)
        else:
            pm.menuItem(label='assemble', c=self.assembleCallback)
            pm.menuItem(label='open', c=self.openCallback)
