import pymel.core as pm
from lcPipe.core import version
from lcPipe.core import assemble
from lcPipe.core import database
from lcPipe.ui.itemBase import ItemBase
from lcPipe.ui.shotManager import ShotManager

### INTERFACE
class ItemWidget(ItemBase):
    def __init__(self, name, itemName, imgPath, label, status, parentWidget, color=(0, .2, .50)):
        super(ItemWidget, self).__init__(name, itemName, imgPath, label, status, parentWidget, color)

    def dClickCallBack(self, *args):
        if self.task == 'asset' or self.task == 'shot':
            self.parentWidget.refreshList(path=self.parentWidget.path, task=self.task, code=self.code)
        else:
            self.openCallback()
        
    def openCallback(self, *args):
        print 'open'
        itemMData = self.getItem()

        if itemMData['status'] == 'notCreated':
            return pm.confirmDialog(title='error', ma='center', message='This scene is not assembled yet',
                                    button=['OK'], defaultButton='OK', dismissString='OK')

        version.open(type=itemMData['type'], task=itemMData['task'], code=itemMData['code'])

    def assembleCallback(self, *args):
        print 'assemble'
        itemMData = self.getItem()
        itemType = database.getTaskType(self.task)
        if itemMData['status'] == 'notCreated':
            assemble.assemble(itemType, self.task, self.code)
        else:
            resp = pm.confirmDialog(title='Confirm',
                                    message='This item is already assembled \n Do you want to reassemble?',
                                    button=['Yes', 'No'], defaultButton='Yes', cancelButton='No', dismissString='No')
            if resp == 'Yes':
                assemble.assemble(itemType, self.task, self.code)

    def shotManagerCallback(self, *args):
        itemMData = self.getItem()
        shotMng = ShotManager(itemMData)
        shotMng.projectName = self.parentWidget.projectName
        shotMng.createShotManager()

    def addMenus(self):
        pm.popupMenu(parent=self.widgetName)

        if self.task == 'asset':
            pm.menuItem(label='remove asset', c=self.removeCallback)
        elif self.task == 'shot':
            pm.menuItem(label='shot manager', c=self.shotManagerCallback)
            pm.menuItem(label='remove shot', c=self.removeCallback)
        else:
            pm.menuItem(label='assemble', c=self.assembleCallback)
            pm.menuItem(label='open', c=self.openCallback)
