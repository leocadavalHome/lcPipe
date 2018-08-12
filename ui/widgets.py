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

        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/small.png', c=lambda x, y=2: self.changeViewCallback(y))
        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/big.png', c=lambda x, y=1: self.changeViewCallback(y))

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
    ##todo fazer funcionar o asset Prompt generico
        def __init__(self):
            self.createAssetPrompt()

        def createAssetPrompt(self):
            form = pm.setParent(q=True)
            f = pm.formLayout(form, e=True, width=150)

            col2 = pm.columnLayout(p=f, adjustableColumn=True)
            pane = pm.paneLayout(p=col2, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)])
            folderTreeWidget = FolderTreeWidget()
            folderTreeWidget.createFolderTree(pane)
            folderTreeWidget.projectName = database.getCurrentProject()
            folderTreeWidget.type = 'asset'
            folderTreeWidget.getFolderTree()

            itemListWidget = ItemListBase()
            itemListWidget.projectName = database.getCurrentProject()
            itemListWidget.createList(pane)
            itemListWidget.refreshList(path=[], task='asset')

            infoWidget = InfoWidget()
            infoWidget.createInfo(pane)

            folderTreeWidget.itemListWidget = itemListWidget
            folderTreeWidget.itemListWidget.type = 'asset'
            folderTreeWidget.itemListWidget.task = 'asset'
            itemListWidget.infoWidget = infoWidget

            b1 = pm.button(p=f, l='Cancel', c='pm.layoutDialog( dismiss="Abort" )')
            b2 = pm.button(p=f, l='OK', c=lambda x: self.createAssetCallBack(itemListWidget.selectedItem))

            spacer = 5
            top = 5
            edge = 5
            pm.formLayout(form, edit=True,
                          attachForm=[(col2, 'right', edge), (col2, 'top', top), (col2, 'left', edge), (b1, 'right', edge),
                                      (b1, 'bottom', edge), (b2, 'left', edge), (b2, 'bottom', edge)], attachNone=[],
                          attachControl=[], attachPosition=[(b1, 'right', spacer, 90), (b2, 'left', spacer, 10)])

        def createAssetCallBack(self, component, *args):
            if component:
                print component

                pm.layoutDialog(dismiss='ok')