import pymel.core as pm
from lcPipe.core import database
reload(database)
from lcPipe.ui import widgets
reload(widgets)


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


    def browserCallback(self, *args):
        self.browser()

    def publishCallback(self, *args):
        type = pm.fileInfo['type']
        task = pm.fileInfo['task']
        code = pm.fileInfo['code']
        self.publish(type=pm.fileInfo['type'], task=pm.fileInfo['task'], code=pm.fileInfo['code'])

    def browser(self):
        database.mongoConnect()
        widgets.itemBrowser()

    def publish(self, type, task, code):
        pubWidget = widgets.PublishWidget(task=task, code=code, assetType=type)
        pubWidget.createWin()

    def currentPrj(self, *args):
        print database.currentProject

