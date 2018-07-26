import pymel.core as pm
from lcPipe.ui.folderTreeBase import FolderTreeBase


class FolderTreeWidget(FolderTreeBase):
    def __init__(self, itemType='asset'):
        super(FolderTreeWidget, self).__init__(itemType)

    def createFolderTree(self, parent):
        self.parentWidget = parent
        self.widgetName = pm.treeView(p=self.parentWidget, numberOfButtons=0, abr=False)
        pm.treeView(self.widgetName, e=True, selectionChangedCommand=self.selChangedCallBack, allowDragAndDrop=False, editLabelCommand=self.editNameCallback)
        self.getFolderTree()

    def selChangedCallBack(self, *args):
        sel = pm.treeView(self.widgetName, q=True, si=True)
        if sel:
            if self.itemListWidget:
                self.itemListWidget.path = self.getSelectedPath()
                self.itemListWidget.type = self.type
                self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task, code=None)

    def getSelectedPath(self):
        path = ''
        sel = pm.treeView(self.widgetName, q=True, si=True)
        if sel:
            child = sel[0]
            parent = 'start'
            path = [child.split('_')[-1]]
            while parent:
                parent = pm.treeView(self.widgetName, q=True, ip=child)
                child = parent
                if child:
                    path.append(child.split('_')[-1])
        return list(reversed(path))
