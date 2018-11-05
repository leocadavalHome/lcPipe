import pymel.core as pm
from lcPipe.core import database
import logging
logger = logging.getLogger(__name__)

class FolderTreeBase(object):
    def __init__(self, itemType='asset'):
        self.widgetName = None
        self.parentWidget = None
        self.type = itemType
        self.itemListWidget = None
        self.projectName = None
        self.folderTreeDict = None

    def createFolderTree(self, parent):
        self.parentWidget = parent
        self.widgetName = pm.treeView(p=self.parentWidget, numberOfButtons=0, abr=False)
        pm.treeView(self.widgetName, e=True, selectionChangedCommand=self.selChangedCallBack,
                    allowDragAndDrop=False, editLabelCommand=self.editNameCallback)
        self.getFolderTree()

    def createMenus(self):
        pass

    def selChangedCallBack(self, *args):
        pass

    def editNameCallback(self, *args):
        return None

    def putFolderTree(self):
        allItems = pm.treeView(self.widgetName, q=True, children=True)
        if not allItems:
            return {}
        folderTreeDict = {}
        for item in allItems:
            par = pm.treeView(self.widgetName, q=True, itemParent=item)
            if par:
                newName = par.split('_')[-1]+'_'+item.split('_')[-1]
                if newName != item:
                    folderTreeDict[newName] = {'parent': par}
                else:
                    folderTreeDict[item] = {'parent': par}
            else:
                folderTreeDict[item] = {'parent': ''}
        self.folderTreeDict = folderTreeDict
        return folderTreeDict

    def getFolderTree(self, fromDb=True):
        if fromDb:
            proj = database.getProjectDict()
            self.projectName = proj['projectName']
            self.folderTreeDict = proj[self.type + 'Folders']

        allKeys = self.folderTreeDict.keys()
        parentList = [x for x in self.folderTreeDict if self.folderTreeDict[x]['parent'] == '']
        parentList.sort()
        pm.treeView(self.widgetName, e=True, ra=True)
        for item in parentList:
            pm.treeView(self.widgetName, e=True, addItem=(item, ''), ei=(item, False))
            pm.treeView(self.widgetName, e=True, displayLabel=(item, item.split('_')[-1]))

        count = 0
        while allKeys:
            allKeys = [x for x in allKeys if not x in parentList]
            parentList = [x for x in self.folderTreeDict if self.folderTreeDict[x]['parent'] in parentList]
            parentList.sort()
            for item in parentList:
                pm.treeView(self.widgetName, e=True, addItem=(item, self.folderTreeDict[item]['parent']), ei=(item, False))
                pm.treeView(self.widgetName, e=True, displayLabel=(item, item.split('_')[-1]))
            count += 1
            if count > 1000:
                break
