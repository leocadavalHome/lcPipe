import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import check
from lcPipe.ui import widgets
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget

class Session:
    def __init__(self):
        self.user = 'teste'

    def createMenu(self):
        print 'initiating session'
        if pm.menu('PipeMenu', exists=True):
            pm.deleteUI('PipeMenu')

        pm.menu('PipeMenu', label='PipeMenu', p='MayaWindow', to=True)
        pm.menuItem(label="Browser", command=self.browserCallback)
        pm.menuItem(label="Publish Scene", command=self.publishCallback)
        pm.menuItem(label="Update Scene", command=self.sceneCheckCallback)
        pm.menuItem (label="scriptJob Update Scene", command=self.scriptJobSceneCheckCallback)
        pm.menuItem (label="scriptJob kill", command=self.killall)

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
        print database.currentProject

    def checkProjects(self):
        all = database.getAllProjects()
        allProjects = [x for x in all]
        print allProjects

        if not allProjects:
            print 'no project found!!'

            result = pm.promptDialog (
                title='No project',
                message='No project Found! Enter Name for a new one:',
                button=['OK', 'Cancel'],
                defaultButton='OK',
                cancelButton='Cancel',
                dismissString='Cancel')

            if result == 'OK':
                text = pm.promptDialog (query=True, text=True)
                print text
                database.addProject (projectName=text, prefix=text[:2])

    def scriptJobSceneCheckCallback(self,*args):
        from lcPipe.core import check
        pm.scriptJob (event=['SceneOpened', check.sceneRefCheck])


    def killall(self, *args):
        pm.scriptJob (ka=True)