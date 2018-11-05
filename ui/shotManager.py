import pymel.core as pm
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.componentListWidget import ComponentListWidget
from lcPipe.core import check
from lcPipe.core import fileFunctions
import logging
logger = logging.getLogger(__name__)

class ShotManager:
    def __init__(self, itemMData):
        self.itemMData = itemMData
        self.infoWidget = None
        self.compListWidget = None
        self.projectName = None

    def createShotManager(self):
        self.win = pm.window(title='SHOT MANAGER', w=300, h=200)
        form = pm.formLayout(numberOfDivisions=100)

        pane = pm.paneLayout(p=form, configuration='horizontal2')
        self.infoWidget = InfoWidget()
        self.infoWidget.createInfo(pane)
        self.infoWidget.putItemInfo(self.itemMData)
        self.compListWidget = ComponentListWidget()
        self.compListWidget.projectName = self.projectName
        self.compListWidget.createList(pane)

        b1 = pm.button(p=form, label='Update', h=40, w=80, c=self.updateCallback)
        b2 = pm.button(p=form, label='Close', h=40, w=80, c=self.closeCallback)

        pm.formLayout(form, edit=True,
                      attachForm=[(pane, 'left', 5), (pane, 'top', 5), (pane, 'right', 5),
                                  (b1, 'left', 30), (b1, 'bottom', 5),  (b2, 'right', 30), (b2, 'bottom', 5)],
                      attachControl=[(pane, 'bottom', 5, b1)],
                      attachPosition=[],
                      attachNone=()
                      )

        pm.showWindow(self.win)
        self.compListWidget.refreshList(itemMData=self.itemMData)

    def closeCallback(self, *args):
        pm.deleteUI(self.win)

    def updateCallback (self, *args):
        info = pm.fileInfo.keys()
        if 'code' in info and 'task' in info:
            code = pm.fileInfo['code']
            task = pm.fileInfo['task']

            if code and task:
                if code == self.itemMData['code'] and task == self.itemMData['task']:
                    check.sceneRefCheck(silent=True)
                    pm.deleteUI (self.win)
                    return

        resp = pm.confirmDialog (title='File not open', message='Do you want to open this file for updating?',
                                 button=['Open', "Don't Open", 'Cancel'], defaultButton='Save',
                                 cancelButton='Cancel', dismissString='Cancel')
        if resp == 'Open':
            fileFunctions.openFile(task=self.itemMData['task'], code=self.itemMData['code'], type=self.itemMData['type'])
            check.sceneRefCheck (silent=True)
            pm.deleteUI (self.win)

