import pymel.core as pm
from lcPipe.core import database
import logging
logger = logging.getLogger(__name__)

### INTERFACE
class ItemBase(object):
    def __init__(self, name, itemName, imgPath, label, status, parentWidget, color=(0, .2, .50)):
        self.widgetName = None
        self.parentWidget = parentWidget
        self.shotMngClass = None
        self.infoWidget = None

        self.name = name
        self.itemName = itemName
        self.label = label
        self.imgPath = imgPath
        self.color = color
        self.status = status
        self.selected = False
        self.task = None
        self.code = None
        self.publishVer = 0
        self.workVer = 0

    def getItem(self):
        projName = self.parentWidget.projectName
        itemType = database.getTaskType(self.task)
        collection = database.getCollection(itemType, projName)

        if self.task == 'asset':
            searchTask = 'model'
        elif self.task == 'shot':
            searchTask = 'layout'
        else:
            searchTask = self.task

        item = collection.find_one({'task': searchTask, 'code': self.code})

        return item

    def dClickCallBack(self, *args):
        pass

    def clickCallBack(self, *args):
        if self.selected:
            pm.layout(self.name, e=True, backgroundColor=self.color)
            self.parentWidget.selectedItem = None
            self.selected = False
        else:
            if self.parentWidget.selectedItem:
                pm.layout(self.parentWidget.selectedItem.name, e=True,
                          backgroundColor=self.parentWidget.selectedItem.color)
                self.parentWidget.selectedItem.selected = False
            pm.layout(self.name, e=True, backgroundColor=(.27, .27, .27))
            self.parentWidget.selectedItem = self
            self.selected = True
            if self.infoWidget:
                self.infoWidget.putInfo(self)

    def dragCallback(self, dragControl, x, y, modifiers):
        return [self.task, self.code]

    def removeCallback(self, *args):
        logger.debug('remove Item')
        resp = pm.confirmDialog (title='Confirm',
                                 message='Are you sure to remove this asset? No Undo!',
                                 button=['Yes', "No", 'Cancel'], defaultButton='Yes',
                                 cancelButton='No', dismissString='No')
        if resp == 'Yes':
            itemType = database.getTaskType(self.task)
            database.removeItem(itemType, self.code)
            pm.evalDeferred('cmds.deleteUI("' + self.widgetName + '")')
            self.parentWidget.itemList.remove(self)

    def addToLayout(self, option):
        if option == 1:
            self.widgetName = pm.columnLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color,w=140, h=75, dragCallback=self.dragCallback)
            pm.text(label=self.itemName,  font="boldLabelFont")
            pm.separator(h=5)
            pm.rowLayout(nc=2)
            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack, doubleClickCommand=self.dClickCallBack, h=50, w=50)
            pm.columnLayout()
            pm.text(label=self.label,  font="smallPlainLabelFont")
            pm.separator(h=2, st='in')
            pm.text(label='code:%s' % self.code,   font="smallPlainLabelFont")
            pm.text(label='user: non',  font="smallPlainLabelFont")
            pm.text(label=self.status, font = "smallObliqueLabelFont")
            self.addMenus()

        elif option == 2:
            self.widgetName = pm.columnLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color,
                                               w=100, h=45, dragCallback=self.dragCallback)
            pm.text(label=self.itemName, font="smallBoldLabelFont")
            pm.rowLayout(nc=5)
            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack,
                              doubleClickCommand=self.dClickCallBack,h=30,w=30)
            pm.columnLayout()
            pm.text(label=self.label,  font="smallPlainLabelFont")
            self.addMenus()

    def addMenus(self):
        pass
