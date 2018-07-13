import pymel.core as pm
from lcPipe.core import database

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
            pm.rowLayout(self.name, e=True, backgroundColor=self.color)
            self.parentWidget.selectedItem = None
            self.selected = False
        else:
            if self.parentWidget.selectedItem:
                pm.rowLayout(self.parentWidget.selectedItem.name, e=True,
                                  backgroundColor=self.parentWidget.selectedItem.color)
                self.parentWidget.selectedItem.selected = False
            pm.rowLayout(self.name, e=True, backgroundColor=(.27, .27, .27))
            self.parentWidget.selectedItem = self
            self.selected = True
            if self.infoWidget:
                self.infoWidget.putInfo(self)

    def dragCallback(self, dragControl, x, y, modifiers):
        return [self.task, self.code]

    def removeCallback(self, *args):
        print 'remove Item'
        itemType = database.getTaskType(self.task)
        database.removeItem(itemType, self.code)
        pm.evalDeferred('cmds.deleteUI("' + self.widgetName + '")')
        self.parentWidget.itemList.remove(self)

    def addToLayout(self, option):
        if option == 1:
            self.widgetName = pm.rowLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color, nc=2, w=200, h=100, dragCallback=self.dragCallback)

            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack, doubleClickCommand=self.dClickCallBack)
            pm.columnLayout()
            pm.text(label=self.label)
            pm.separator(h=10)
            pm.text(label=self.itemName,  font="boldLabelFont")
            pm.separator(h=12, st='in')
            pm.text(label='code:%s' % self.code)
            pm.text(label='user: non')
            pm.text(label=self.status, font = "smallObliqueLabelFont")
            self.addMenus()

        elif option == 2:
            self.widgetName = pm.rowLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color, nc=2,
                                           w=140, h=50, dragCallback=self.dragCallback)

            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack,
                              doubleClickCommand=self.dClickCallBack,h=50,w=50)
            pm.columnLayout()
            pm.text(label=self.label)
            pm.separator(h=5)
            pm.text(label=self.itemName, font="boldLabelFont")
            self.addMenus()

    def addMenus(self):
        pass
