import pymel.core as pm
from lcPipe.core import database
from lcPipe.ui.itemBase import ItemBase


class ComponentWidget(ItemBase):
    def __init__(self, name, itemName, imgPath, label, status, parentWidget, color=(0, .2, .50)):
        super(ComponentWidget, self).__init__(name, itemName, imgPath, label, status, parentWidget, color)

    def removeComponentCallBack(self, *args):
        itemMData = self.parentWidget.item
        ns = self.name.split(':')[0]
        database.removeComponent(itemMData, ns)
        pm.evalDeferred('pm.deleteUI("' + self.widgetName + '")')
        self.parentWidget.itemList.remove(self)

    def addMenus(self):
        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='remove component', c=self.removeComponentCallBack)
