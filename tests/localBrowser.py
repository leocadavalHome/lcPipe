import lcPipe.core.fileFunctions as fileFunc
import os.path

import pymel.core as pm
from lcPipe.core import database
from lcPipe.publish import publish
from lcPipe.core import fileFunctions
from lcPipe.ui.folderTreeWidget import FolderTreeWidget
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.itemListWidget import ItemListWidget
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget
from lcPipe.api.item import Item
from lcPipe.ui.itemListBase import ItemListBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(10)


class localItemBrowser:
    def __init__(self):
        self.projectSelectWidget = None
        self.folderTreeWidget = None
        self.itemListWidget = None
        self.infoWidget = None
        self.createBrowser()
        self.typeOpt = None

    def createBrowser(self):
        win = pm.window(w=200)

        form = pm.formLayout(numberOfDivisions=100)
        col2 = pm.columnLayout(p=form, adjustableColumn=True)
        allowedAreas = ['right', 'left']
        pm.dockControl(label='BROWSER', w=200, area='left', content=win, allowedArea=allowedAreas)

        self.projectSelectWidget = ProjectSelectWidget()
        self.projectSelectWidget.createProjectSelect(col2)

        pm.rowLayout(nc=3, adj=1)
        self.typeOpt = pm.optionMenuGrp(label='Item Type', changeCommand=self.changeTypeCallback,
                                        cat=[[1,'left',5],[2,'left',-80]])
        pm.menuItem(label='asset')
        pm.menuItem(label='shot')
        pm.menuItem(divider=True)
        typesAsset = database.getAllTasks('asset')
        for assetType in typesAsset:
            pm.menuItem(label=assetType)
        pm.menuItem(divider=True)
        typesShot = database.getAllTasks('shot')
        for assetType in typesShot:
            pm.menuItem(label=assetType)

        pm.symbolButton(image=r'small.png', c=lambda x, y=2: self.changeViewCallback(y))
        pm.symbolButton(image=r'big.png', c=lambda x, y=1: self.changeViewCallback(y))

        pane = pm.paneLayout(p=form, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)], shp = 0)

        self.folderTreeWidget = FolderTreeWidget('asset')
        self.folderTreeWidget.createFolderTree(pane)
        self.folderTreeWidget.getFolderTree()

        self.itemListWidget = ItemListWidget()
        self.itemListWidget.createList(pane)
        self.itemListWidget.refreshList(path=[], task='asset')

        self.infoWidget = InfoWidget()
        self.infoWidget.createInfo(pane)

        self.folderTreeWidget.itemListWidget = self.itemListWidget
        self.folderTreeWidget.itemListWidget.type = 'asset'
        self.folderTreeWidget.itemListWidget.task = 'asset'
        self.projectSelectWidget.folderTreeWidget = self.folderTreeWidget
        self.projectSelectWidget.itemListWidget = self.itemListWidget
        self.itemListWidget.infoWidget = self.infoWidget

        pm.formLayout(form, edit=True,
                      attachForm=[(pane, 'left', 5), (pane, 'bottom', 5), (pane, 'right', 5),
                                  (col2, 'top', 5), (col2, 'left', 5), (col2, 'right', 5)],
                      attachControl=[(pane, 'top', 5, col2)],
                      attachPosition=[],
                      attachNone=()
                      )

        pm.showWindow()

    def changeTypeCallback(self, newTaskToSearch, *args):
        assetType = database.getTaskType(newTaskToSearch)

        self.itemListWidget.type = assetType

        self.folderTreeWidget.type = assetType
        self.folderTreeWidget.getFolderTree()

        self.itemListWidget.task = newTaskToSearch
        self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)

    def changeViewCallback(self, opt):
        self.itemListWidget.viewOption = opt
        self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)