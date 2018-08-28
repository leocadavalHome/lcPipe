import pymel.core as pm

class ProgressWindowWidget(object):

    def __init__(self, title='ProgressBar', maxValue=None, width=300):
        self._window = None
        self.maxValue = maxValue
        self._columnLayout = None
        self.width = width
        self._progressControl = None
        self._ProgressControlList = []
        self.title = title
        self.createWindow()


    def createWindow(self):
        self._window = pm.window(t=self.title)
        self._columnLayout = pm.columnLayout()
        self._progressControl = pm.progressBar(maxValue=self.maxValue, width=self.width)
        self._ProgressControlList.append(self._progressControl)
        pm.showWindow(self._window)

    def closeWindow(self):
        pm.deleteUI(self._window)

    def progressUpdate(self, step):
        pm.progressBar(self._progressControl, e=True, step=step)

    def addProgressBar (self, maxValue):
        newProgressBar = pm.progressBar(p=self._columnLayout, maxValue=maxValue, width=self.width)
        self._ProgressControlList.append(newProgressBar)

    def delProgressBar (self):
        pm.deleteUI(self._progressControl)
        self._ProgressControlList.pop()
        self._progressControl = self._ProgressControlList[-1]