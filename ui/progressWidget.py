import pymel.core as pm

class ProgressWindowWidget(object):

    def __init__(self, title='ProgressBar', maxValue=None, width=300):
        self._window = None
        self.maxValue = maxValue
        self.width = width
        self._progressControl = None
        self.title = title
        self.createWindow()


    def createWindow(self):
        self._window = pm.window(t=self.title)
        pm.columnLayout()
        self._progressControl = pm.progressBar(maxValue=self.maxValue, width=self.width)
        pm.showWindow(self._window)

    def closeWindow(self):
        pm.deleteUI(self._window)

    def progressUpdate(self, step):
        pm.progressBar(self._progressControl, e=True, step=step)