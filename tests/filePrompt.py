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

class AssetPrompt:
    ##done fazer funcionar o asset Prompt generico
        def __init__(self):
            self.window=None
            self.createAssetPrompt()

        def createAssetPrompt(self):
            self.window = pm.window ()
            form = pm.formLayout(numberOfDivisions=100)
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
            pm.menuItem(divider=True)
            typesShot = database.getAllTasks('shot')
            for assetType in typesShot:
                pm.menuItem(label=assetType)

            pm.symbolButton(image=r'small.png',
                             c=lambda x, y=2: self.changeViewCallback (y))
            pm.symbolButton(image=r'big.png',
                             c=lambda x, y=1: self.changeViewCallback (y))

            pane = pm.paneLayout(p=form, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)], shp=0)

            logger.debug('setup ok')

            self.folderTreeWidget = FolderTreeWidget('asset')
            self.folderTreeWidget.createFolderTree(pane)
            self.folderTreeWidget.getFolderTree()

            self.itemListWidget = ItemListWidget()
            self.itemListWidget.createList(pane)
            self.itemListWidget.refreshList(path=[], task='asset')

            self.infoWidget = InfoWidget ()
            self.infoWidget.createInfo(pane)

            self.folderTreeWidget.itemListWidget = self.itemListWidget
            self.folderTreeWidget.itemListWidget.type = 'asset'
            self.folderTreeWidget.itemListWidget.task = 'asset'
            self.itemListWidget.infoWidget = self.infoWidget

            b1 = pm.button(p=f, l='Cancel', c=self.cancelCallback)
            b2 = pm.button(p=f, l='OK', c=lambda x: self.okCallback(self.itemListWidget.selectedItem))

            pm.formLayout(form, edit=True,
                          attachForm=[(pane, 'left', 5), (pane, 'right', 5),
                                       (col2, 'top', 5), (col2, 'left', 5), (col2, 'right', 5),
                                       (b1, 'right', 5), (b1, 'bottom', 5), (b2, 'left', 5), (b2, 'bottom', 5)
                                       ],
                          attachControl=[(pane, 'top', 5, col2), (pane, 'bottom', 5, b1)],
                          attachPosition=[(b1, 'right', 5, 90), (b2, 'left', 5, 10)],
                          attachNone=())

            pm.showWindow (self.window)

        def cancelCallback(self, *args):
            pm.deleteUI(self.window)

        def okCallback (self, selected, *args):
            if selected:
                logger.debug(selected.name)
                logger.debug('task %s, code %s' % (selected.task, selected.code))
                resp = pm.confirmDialog (title='Confirm',
                                         message='Are you sure to save the current file as task: %s, code: %s ?' % (selected.task, selected.code),
                                         button=['Yes', "No", 'Cancel'], defaultButton='Yes',
                                         cancelButton='No', dismissString='No')

                if resp=='Yes':
                    version.saveAs(task=selected.task, code=selected.code)
                    logger.info ('saved!!')

                pm.deleteUI(self.window)
            else:
                logger.debug('nothing selected')
                pm.confirmDialog(title='Warning', ma='center',
                                 message='Please select a task!',
                                 button=['OK'], defaultButton='OK', dismissString='OK')

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

x = AssetPrompt()
