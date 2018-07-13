import pymel.core as pm
from lcPipe.core import assemble
from lcPipe.core import database
from lcPipe.core import publish
from lcPipe.core import version
from lcPipe.ui.itemWidget import ItemWidget


class ComponentWidget(ItemWidget):
    def __init__(self, name, imgPath, label, parentWidget, color=(0, .2, .50)):
        super(ComponentWidget, self).__init__(name, imgPath, label, parentWidget, color)

    def removeComponentCallBack(self, *args):
        item = self.parentWidget.item
        ns = self.name.split(':')[0]
        database.removeComponent(item, ns)
        pm.evalDeferred('pm.deleteUI("' + self.widgetName + '")')
        self.parentWidget.itemList.remove(self)

    def addToLayout(self, option):
        if option == 1:
            self.widgetName = pm.rowLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color, nc=2, w=200, h=100,
                                           dragCallback=self.dragCallback)

            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack, doubleClickCommand=self.dClickCallBack)
            pm.columnLayout()
            pm.text(label=self.label)
            pm.separator(h=10)
            pm.text(label=self.itemName,  font="boldLabelFont")
            pm.separator(h=12, st='in')
            pm.text(label='code:%s' % self.code)
            pm.text(label='user: non')
            pm.text(label=self.status, font = "smallObliqueLabelFont")

        elif option == 2:
            self.widgetName = pm.rowLayout(self.name, p=self.parentWidget.widgetName, backgroundColor=self.color, nc=2,
                                           w=140, h=50, dragCallback=self.dragCallback)

            pm.iconTextButton(image=self.imgPath, style='iconOnly', command=self.clickCallBack,
                              doubleClickCommand=self.dClickCallBack, h=50, w=50)
            pm.columnLayout()
            pm.text(label=self.label)
            pm.separator(h=5)
            pm.text(label=self.itemName, font="boldLabelFont")

        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='remove component', c=self.removeComponentCallBack)
