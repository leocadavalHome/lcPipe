import pymel.core as pm
from lcPipe.core import database


class FolderTreeWidget ():
    def __init__ (self):
        self.widgetName = None
        self.parentWidget = None
        self.type = 'asset'

        self.itemListWidget = None

        proj = database.getProjectDict ()
        self.projectName = proj['projectName']

    def createFolderTree (self, parent):
        self.parentWidget = parent
        self.widgetName = pm.treeView ( p=self.parentWidget, numberOfButtons=0, abr=False )
        pm.treeView ( self.widgetName, e=True, selectionChangedCommand=self.selChangedCallBack )
        pm.popupMenu ( parent=self.widgetName )
        pm.menuItem ( l='add folder', c=self.addFolderCallBack )
        pm.menuItem ( l='remove folder', c=self.removeFolderCallBack )
        if self.projectName:
            self.getFolderTree ()

    def addFolderCallBack (self, *args):
        print 'add folder'
        sel = pm.treeView ( self.widgetName, q=True, si=True )
        if sel:
            pm.treeView ( self.widgetName, e=True, addItem=('new Folder', sel[0]) )
        else:
            pm.treeView ( self.widgetName, e=True, addItem=('new Folder', '') )

    def removeFolderCallBack (self, *args):
        print 'remove folder'
        sel = pm.treeView ( self.widgetName, q=True, si=True )
        if sel:
            pm.treeView ( self.widgetName, e=True, removeItem=sel[0] )
        else:
            print 'select a folder to remove!!'

    def selChangedCallBack (self, *args):
        sel = pm.treeView ( self.widgetName, q=True, si=True )
        if sel:
            if self.itemListWidget:
                self.itemListWidget.path = self.getSelectedPath ()
                self.itemListWidget.type = self.type
                self.itemListWidget.refreshList ( path=self.itemListWidget.path, task=self.itemListWidget.task,
                                                  code=None )

    def getSelectedPath (self):
        path=''
        sel = pm.treeView ( self.widgetName, q=True, si=True )
        if sel:
            child = sel[0]
            parent = 'start'
            path = [child]
            while parent:
                parent = pm.treeView ( self.widgetName, q=True, ip=child )
                child = parent
                if child:
                    path.append ( child )
        return list ( reversed ( path ) )

    def putFolderTree (self):
        allItems = pm.treeView ( self.widgetName, q=True, children=True )
        folderTreeDict = {}
        for item in allItems:
            par = pm.treeView ( self.widgetName, q=True, itemParent=item )
            folderTreeDict[item] = par
        return folderTreeDict

    def getFolderTree (self):
        proj = database.getProjectDict ( self.projectName )
        folderTreeDict = proj[self.type + 'Folders']

        allKeys = folderTreeDict.keys ()
        parentList = [x for x in folderTreeDict if folderTreeDict[x] == '']
        parentList.sort ()
        pm.treeView ( self.widgetName, e=True, ra=True )
        for item in parentList:
            pm.treeView ( self.widgetName, e=True, addItem=(item, '') )

        while allKeys:
            allKeys = [x for x in allKeys if not x in parentList]
            parentList = [x for x in folderTreeDict if folderTreeDict[x] in parentList]
            parentList.sort ()
            for item in parentList:
                pm.treeView ( self.widgetName, e=True, addItem=(item, folderTreeDict[item]) )