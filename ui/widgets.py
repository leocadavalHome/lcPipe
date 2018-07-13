import os.path

import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import publish
from lcPipe.core import version
from lcPipe.ui.folderTreeWidget import FolderTreeWidget
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.itemListWidget import ItemListWidget
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget

class itemBrowser:
    def __init__(self):
        self.projectSelectWidget = ProjectSelectWidget()
        self.folderTreeWidget = FolderTreeWidget()
        self.itemListWidget = ItemListWidget()
        self.infoWidget = InfoWidget()
        self.createBrowser()
        self.typeOpt = None

    def createBrowser(self):
        win = pm.window(w=800, h=600)
        col2 = pm.columnLayout(adjustableColumn=True)
        allowedAreas = ['right', 'left']
        pm.dockControl(label='SHOT INFO', w=600, area='left', content=win, allowedArea=allowedAreas)

        self.projectSelectWidget.createProjectSelect(col2)
        pm.rowLayout(nc=3, adj=1)
        self.typeOpt = pm.optionMenuGrp(label='Item Type', changeCommand=self.changeTypeCallback, cat=[[1,'left',45],[2,'left',-20]])
        types = ['asset', 'shot', 'model', 'uvs', 'texture', 'blendShape', 'rig', 'layout', 'animation',
                 'shotFinalizing', 'lightining', 'render']
        for assetType in types:
            pm.menuItem(label=assetType)

        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/small.png', c=lambda x, y=2: self.changeViewCallback(y))
        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/big.png', c=lambda x, y=1: self.changeViewCallback(y))
        pane = pm.paneLayout(p=col2, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)])

        self.folderTreeWidget.createFolderTree(pane)
        self.folderTreeWidget.type = 'asset'
        self.folderTreeWidget.getFolderTree()

        self.itemListWidget.createList(pane)
        self.itemListWidget.refreshList(path=[], task='asset')

        self.infoWidget.createInfo(pane)

        self.folderTreeWidget.itemListWidget = self.itemListWidget
        self.folderTreeWidget.itemListWidget.type = 'asset'
        self.folderTreeWidget.itemListWidget.task = 'asset'
        self.projectSelectWidget.folderTreeWidget = self.folderTreeWidget
        self.projectSelectWidget.itemListWidget = self.itemListWidget
        self.itemListWidget.infoWidget = self.infoWidget

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

        collection = database.getCollection(self.type)
        item = database.getItemMData(task=self.task, code=self.code, itemType=self.type)
        # get path
        originalName = pm.sceneName()
        path = database.getPath(item, dirLocation='publishLocation')
        dirPath = path[0]
        filename = path[1]

        # increment publish version
        item['publishVer'] += 1
        collection.find_one_and_update({'task': self.task, 'code': self.code},
                                       {'$set': {'publishVer': item['publishVer']}})
        publishVer = 'v%03d_' % item['publishVer']

        # make full path
        fullPath = os.path.join(dirPath, publishVer + filename)

        if not os.path.exists(dirPath):
            print ('creating:' + dirPath)
            os.makedirs(dirPath)

        print 'publish ver %s, at %s' % (publishVer, fullPath)

        # save scene
        pm.saveAs(fullPath)
        pm.renameFile(originalName)

        version.takeSnapShot(item)

        self.closeWin()
