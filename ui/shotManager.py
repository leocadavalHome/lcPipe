import pymel.core as pm
from lcPipe.ui.componentListWidget import ComponentListWidget
from lcPipe.ui.infoWidget import InfoWidget


class ShotManager:
    def __init__(self, item):
        self.item = item
        self.infoWidget = None
        self.compListWidget = None
        self.projectName = None

    def createShotManager(self):
        win = pm.window(title='SHOT MANAGER', w=800, h=600)
        pane = pm.paneLayout(configuration='horizontal2')
        self.infoWidget = InfoWidget()
        self.infoWidget.createInfo(pane)
        self.infoWidget.putItemInfo(self.item)
        self.compListWidget = ComponentListWidget()
        self.compListWidget.projectName = self.projectName
        self.compListWidget.createList(pane)

        pm.showWindow(win)
        self.compListWidget.refreshList(item=self.item)