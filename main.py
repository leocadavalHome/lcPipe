import pymel.core as pm
import logging
import sys

from lcPipe.core import database
from lcPipe.core import check
from lcPipe.ui import widgets

from lcPipe.ui.folderTreeWidget import FolderTreeWidget
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.itemListBase import ItemListBase

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)



class Session:
    def __init__(self):
        self.user = 'teste'

    def createMenu(self):
        logger.info('initiating session')
        if pm.menu('PipeMenu', exists=True):
            pm.deleteUI('PipeMenu')

        pm.menu('PipeMenu', label='PipeMenu', p='MayaWindow', to=True)
        pm.menuItem(label="Browser", command=self.browserCallback)
        pm.menuItem(label="Publish Scene", command=self.publishCallback)
        pm.menuItem(label="Update Scene", command=self.sceneCheckCallback)
        pm.menuItem(label="scriptJob Update Scene", command=self.scriptJobSceneCheckCallback)
        pm.menuItem(label="scriptJob kill", command=self.killall)

    def sceneCheckCallback(self,*args):
        check.sceneRefCheck()

    def browserCallback(self, *args):
        self.browser()

    def publishCallback(self, *args):
        if 'task' not in pm.fileInfo.keys() or 'code' not in pm.fileInfo.keys():
            resp = pm.confirmDialog(title='No file', ma='center',
                                    message='This file has no file info',
                                    button=['Ok'], defaultButton='ok', dismissString='ok')
            return
        else:
            self.publish(type=pm.fileInfo['type'], task=pm.fileInfo['task'], code=pm.fileInfo['code'])

    def browser(self):
        database.mongoConnect()
        self.checkProjects()
        widgets.itemBrowser()

    def publish(self, type, task, code):
        pubWidget = widgets.PublishWidget(task=task, code=code, assetType=type)
        pubWidget.createWin()

    def currentPrj(self, *args):
        return database.currentProject

    def checkProjects(self):
        all = database.getAllProjects()
        allProjects = [x for x in all]

        if not allProjects:
            logger.error('no project found!!')

            result = pm.promptDialog (
                title='No project',
                message='No project Found! Enter Name for a new one:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

            if result == 'OK':
                text = pm.promptDialog (query=True, text=True)
                database.addProject (projectName=text, prefix=text[:2])

    def saveAs(self):
        #open a browser
        #save file as selected task
        pass

    def scriptJobSceneCheckCallback(self,*args):
        from lcPipe.core import check
        pm.scriptJob (event=['SceneOpened', check.sceneRefCheck])


    def killall(self, *args):
        pm.scriptJob (ka=True)

def createAssetPrompt(self):
    form = pm.setParent(q=True)
    f = pm.formLayout(form, e=True, width=150)

    col2 = pm.columnLayout(p=f, adjustableColumn=True)
    nsField = pm.textFieldGrp ( 'nsFieldPrompt', l='Name Space', tx='ref' )
    refModeField = pm.optionMenuGrp ( l='Assemble Mode' )
    pm.menuItem(l='reference')
    pm.menuItem(l='cache')
    pm.menuItem(l='import')
    pm.menuItem(l='copy')
    pane = pm.paneLayout(p=col2, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)])
    folderTreeWidget = FolderTreeWidget()
    folderTreeWidget.createFolderTree(pane)
    folderTreeWidget.projectName = self.projectName
    folderTreeWidget.type = 'asset'
    folderTreeWidget.getFolderTree()

    itemListWidget = ItemListBase()
    itemListWidget.projectName = self.projectName
    itemListWidget.createList(pane)
    itemListWidget.refreshList(path=[], task='rig')

    infoWidget = InfoWidget()
    infoWidget.createInfo(pane)

    folderTreeWidget.itemListWidget = itemListWidget
    folderTreeWidget.itemListWidget.type = 'asset'
    folderTreeWidget.itemListWidget.task = 'rig'
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
        ns = pm.textFieldGrp('nsFieldPrompt', q=True, tx=True)

        database.addComponent(self.item, ns, component.task, component.code, 'reference', update=True)

        createdTasks = database.getShotCreatedTasks(self.item)
        for itemMData in createdTasks:
            database.addComponent(itemMData, ns, component.task, component.code, 'reference', update=True)

        pm.layoutDialog(dismiss='ok')