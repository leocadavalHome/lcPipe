import pymel.core as pm
from lcPipe.core import assemble
from lcPipe.core import database
from lcPipe.core import publish
from lcPipe.core import version
from lcPipe.ui.itemWidget import ItemWidget

reload ( database )
reload ( publish )
reload ( assemble )
reload ( version )


class ComponentWidget ( ItemWidget ):
    def __init__ (self, name, imgPath, label, parentWidget, color=(0, .2, .50)):
        super ( ComponentWidget, self ).__init__ ( name, imgPath, label, parentWidget, color )

    def removeComponentCallBack (self, *args):
        item = self.parentWidget.item
        ns = self.name.split ( ':' )[0]
        database.removeComponent ( item, ns )
        pm.evalDeferred ( 'pm.deleteUI("' + self.widgetName + '")' )
        self.parentWidget.itemList.remove ( self )

    def addToLayout (self):
        self.widgetName = pm.iconTextButton ( self.name, p=self.parentWidget.widgetName, backgroundColor=self.color,
                                              style='iconAndTextHorizontal', image=self.imgPath, label=self.label, h=80,
                                              w=160, doubleClickCommand=self.dClickCallBack, command=self.clickCallBack,
                                              dragCallback=self.dragCallback )
        pm.popupMenu ( parent=self.widgetName )
        pm.menuItem ( l='remove component', c=self.removeComponentCallBack )