import os.path

import pymel.core as pm
from lcPipe.core import database
from lcPipe.publish import publish
from lcPipe.core import version
from lcPipe.ui.folderTreeWidget import FolderTreeWidget
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.itemListWidget import ItemListWidget
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget
from lcPipe.api.item import Item
from lcPipe.ui.itemListBase import ItemListBase
import logging
logger = logging.getLogger(__name__)
logger.setLevel(10)
"""

"""
class itemBrowser:
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
        self.typeOpt = pm.optionMenuGrp(label='Item Type', changeCommand=self.changeTypeCallback, cat=[[1,'left',5],[2,'left',-80]])
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


class PublishWidget(publish.PublishWidget):
    def __init__(self, task=None, code=None, assetType=None):
        super(PublishWidget, self).__init__(task)
        self.task = task
        self.code = code
        self.type = assetType

    def publishFile(self, *args):
        # get database info on item
        item = Item(task=self.task, code=self.code, itemType=self.type)

        item.publish()
        version.takeSnapShot(item.getDataDict())
        self.closeWin()

        logger.debug('publish ver %s, at %s' % (item.publishVer, item.getPublishPath()))
        resp = pm.confirmDialog(title='Warning', ma='center',
                                message='PUBLISH: %s %s \n Reopen working task?' % (item.name, item.task),
                                button=['Ok', 'No'], defaultButton='Ok', dismissString='No')

        if resp == 'Ok':
            version.open(type=item.type, task=item.task, code= item.code,force=True)
        else:
            pm.newFile(f=True, new=True)


class PublishAsWidget (publish.PublishWidget):
    def __init__(self, task=None, code=None, assetType=None, proxyMode=''):
        super(PublishAsWidget, self).__init__(task)
        self.task = task
        self.code = code
        self.type = assetType
        self.proxyMode = proxyMode

    def publishFile(self, *args):
        # get database info on item
        item = Item(task=self.task, code=self.code, itemType=self.type)
        item.proxyMode = self.proxyMode
        item.publishAs()
        version.takeSnapShot(item.getDataDict())
        self.closeWin()

        logger.debug('publish ver %s, at %s' % (item.publishVer, item.getPublishPath()))
        resp = pm.confirmDialog(title='Warning', ma='center',
                                message='PUBLISH: %s %s \n Reopen working task?' % (item.name, item.task),
                                button=['Ok', 'No'], defaultButton='Ok', dismissString='No')

        if resp == 'Ok':
            version.open(type=item.type, task=item.task, code=item.code, force=True)
        else:
            pm.newFile(f=True, new=True)


class AssetPrompt:
    ##done fazer funcionar o asset Prompt generico
        def __init__(self):
            self.createAssetPrompt()

        def createAssetPrompt(self):
            form = pm.setParent(q=True)
            f = pm.formLayout (form, e=True, width=150)
            col2 = pm.columnLayout (p=f, adjustableColumn=True)
            pm.rowLayout (nc=3, adj=1)
            self.typeOpt = pm.optionMenuGrp (label='Item Type', changeCommand=self.changeTypeCallback,
                                             cat=[[1, 'left', 5], [2, 'left', -80]])
            pm.menuItem (label='asset')
            pm.menuItem (label='shot')
            pm.menuItem (divider=True)
            typesAsset = database.getAllTasks('asset')
            for assetType in typesAsset:
                pm.menuItem (label=assetType)
            pm.menuItem (divider=True)
            typesShot = database.getAllTasks('shot')
            for assetType in typesShot:
                pm.menuItem(label=assetType)

            pm.symbolButton(image=r'small.png',
                             c=lambda x, y=2: self.changeViewCallback (y))
            pm.symbolButton(image=r'big.png',
                             c=lambda x, y=1: self.changeViewCallback (y))

            pane = pm.paneLayout(p=form, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)], shp=0)

            self.folderTreeWidget = FolderTreeWidget ('asset')
            self.folderTreeWidget.createFolderTree (pane)
            self.folderTreeWidget.getFolderTree ()

            self.itemListWidget = ItemListWidget ()
            self.itemListWidget.createList (pane)
            self.itemListWidget.refreshList (path=[], task='asset')

            self.infoWidget = InfoWidget ()
            self.infoWidget.createInfo (pane)

            self.folderTreeWidget.itemListWidget = self.itemListWidget
            self.folderTreeWidget.itemListWidget.type = 'asset'
            self.folderTreeWidget.itemListWidget.task = 'asset'
            self.itemListWidget.infoWidget = self.infoWidget

            b1 = pm.button(p=f, l='Cancel', c='pm.layoutDialog( dismiss="Abort" )')
            b2 = pm.button(p=f, l='OK', c=lambda x: self.okCallback(self.itemListWidget.selectedItem))

            pm.formLayout(form, edit=True,
                          attachForm=[(pane, 'left', 5), (pane, 'right', 5),
                                       (col2, 'top', 5), (col2, 'left', 5), (col2, 'right', 5),
                                       (b1, 'right', 5), (b1, 'bottom', 5), (b2, 'left', 5), (b2, 'bottom', 5)
                                       ],
                          attachControl=[(pane, 'top', 5, col2), (pane, 'bottom', 5, b1)],
                          attachPosition=[(b1, 'right', 5, 90), (b2, 'left', 5, 10)],
                          attachNone=())

        def okCallback (self, selected):
            logger.debug(selected.name)
            if selected:
                logger.debug('task %s, code %s' % (selected.task, selected.code))

            version.saveAs(task=selected.task, code=selected.code)
            pm.layoutDialog(dismiss='ok')

        def changeViewCallback(self, opt):
            self.itemListWidget.viewOption = opt
            self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)

        def changeTypeCallback(self, newTaskToSearch, *args):
            assetType = database.getTaskType(newTaskToSearch)

            self.itemListWidget.type = assetType

            self.folderTreeWidget.type = assetType
            self.folderTreeWidget.getFolderTree()

            self.itemListWidget.task = newTaskToSearch
            self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)