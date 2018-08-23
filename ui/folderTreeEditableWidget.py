import pymel.core as pm
from lcPipe.ui.folderTreeBase import FolderTreeBase
import logging
logger = logging.getLogger(__name__)

class FolderTreeEditableWidget(FolderTreeBase):
    def __init__(self, itemType='asset'):
        super(FolderTreeEditableWidget, self).__init__(itemType)

    def createFolderTree(self, parent):
        self.parentWidget = parent
        self.widgetName = pm.treeView(p=self.parentWidget, numberOfButtons=0, abr=False)
        pm.treeView(self.widgetName, e=True, selectionChangedCommand=self.selChangedCallBack, allowDragAndDrop=True, editLabelCommand=self.editNameCallback, itemRenamedCommand = self.renameCallback)
        self.createMenus()
        self.getFolderTree()

    def createMenus(self):
        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='add folder', c=self.addFolderCallBack)
        pm.menuItem(label='add multiple folders', c=self.addMultipleFoldersCallback)
        pm.menuItem(label='remove folder', c=self.removeFolderCallBack)
        if self.projectName:
            self.getFolderTree()

    def renameCallback(self, *args):
        self.putFolderTree()
        self.getFolderTree(fromDb=False)

    def editNameCallback(self, *args):
        if args[0].split('_')[-1] == args[1]:
            print 'mesmo nome'
            return None

        par = pm.treeView(self.widgetName, q=True, itemParent=args[0])
        newName = self.nextFolderName(args[1], par)
        pm.treeView(self.widgetName, e=True, displayLabel=(args[0], newName.split('_')[-1]))
        logger.debug ('editName: oldName %s, newName %s ' % (args[0], newName))
        return newName

    def nextFolderName(self, name, parent):
        if parent:
            if parent + '_' + name in self.folderTreeDict:
                index = 1
                while parent + '_' + name + str(index) in self.folderTreeDict:
                    index += 1
                return parent + '_' + name + str(index)
            else:
                return parent + '_' + name
        else:
            if name in self.folderTreeDict:
                index = 1
                while name + str(index) in self.folderTreeDict:
                    index += 1
                return name + str(index)
            else:
                return name

    def addFolderCallBack(self, *args):
        print 'add folder'
        sel = pm.treeView(self.widgetName, q=True, si=True)
        if sel:
            newName = self.nextFolderName('newFolder', sel[0])
            pm.treeView(self.widgetName, e=True, addItem=(newName, sel[0]))
        else:
            newName = self.nextFolderName('newFolder', '')
            pm.treeView(self.widgetName, e=True, addItem=(newName, ''))

        pm.treeView(self.widgetName, e=True, displayLabel=(newName, newName.split('_')[-1]))
        self.putFolderTree()

    def addMultipleFoldersCallback(self, *args):
        pm.layoutDialog(ui=self.addMultiPromp)

    def abortMultipleFolders (self, *args):
        pm.layoutDialog(dismiss='cancel')

    def addMultiPromp(self):
        form = pm.setParent(q=True)
        f = pm.formLayout(form, e=True, width=150)
        row = pm.columnLayout()
        nameField = pm.textFieldGrp('addMulti_nameField', label='Name', cw=[(1, 80), (2, 20)], text='',
                                    cat=[(1, 'left', 10), (2, 'left', 5)], editable=True)
        rangeField = pm.intFieldGrp('addMulti_rangeField', label='start-end-step', cw=(1, 80),
                                    cat=[(1, 'left', 10), (2, 'left', 5)], numberOfFields=3, value1=1, value2=10,
                                    value3=1)
        rangeField = pm.intFieldGrp('addMulti_zeroField', label='zeroPad', cw=(1, 80),
                                    cat=[(1, 'left', 10), (2, 'left', 5)],
                                    numberOfFields=1, value1=3)

        b1 = pm.button(p=f, l='Cancel', c= self.abortMultipleFolders)
        b2 = pm.button(p=f, l='OK', c= self.addMultipleFolders)

        spacer = 5
        top = 5
        edge = 5
        pm.formLayout(form, edit=True,
                      attachForm=[(row, 'right', edge), (row, 'top', top), (row, 'left', edge),
                                  (row, 'right', edge),
                                  (b1, 'right', edge), (b1, 'bottom', edge), (b2, 'left', edge),
                                  (b2, 'bottom', edge)],
                      attachNone=[], attachControl=[],
                      attachPosition=[(b1, 'right', spacer, 90), (b2, 'left', spacer, 10)])

    def addMultipleFolders(self, *args):
        sel = pm.treeView(self.widgetName, q=True, si=True)

        name = pm.textFieldGrp('addMulti_nameField', q=True, tx=True)
        start = pm.intFieldGrp('addMulti_rangeField', q=True,  value1=True)
        end = pm.intFieldGrp('addMulti_rangeField', q=True,  value2=True)
        step = pm.intFieldGrp('addMulti_rangeField', q=True, value3=True)
        zeroPad = pm.intFieldGrp('addMulti_zeroField',q=True, value1=True)

        if sel:
            for folder in sel:
                par = folder
                for i in range(start, end + 1, step):
                    itemName = self.nextFolderName(name, par) + '{number:0{width}d}'.format(width=zeroPad, number=i)
                    pm.treeView(self.widgetName, e=True, addItem=(itemName, par))
                    pm.treeView(self.widgetName, e=True, displayLabel=(itemName, itemName.split('_')[-1]))
        else:
            par = ''
            for i in range(start, end + 1, step):
                itemName = self.nextFolderName(name, par) + '{number:0{width}d}'.format(width=zeroPad, number=i)
                pm.treeView(self.widgetName, e=True, addItem=(itemName, par))
                pm.treeView(self.widgetName, e=True, displayLabel=(itemName, itemName.split('_')[-1]))

        self.putFolderTree()
        pm.layoutDialog(dismiss='ok')

    def getChildren(self, sel):
        result = []
        children = [key for key, value in self.folderTreeDict.iteritems() if value['parent'] == sel]
        result.extend(children)
        if children:
            for child in children:
                result.extend(self.getChildren(child))
        return result

    def removeFolderCallBack(self, *args):
        sel = pm.treeView(self.widgetName, q=True, si=True)
        if sel:
            folderList = [x for x in sel if self.folderTreeDict[x]['parent'] not in sel]
            for folder in folderList:
                del self.folderTreeDict[folder]
                children = self.getChildren(folder)
                for child in children:
                    del self.folderTreeDict[child]
        else:
            pm.confirmDialog(title='error', ma='center', message='Select a folder to remove', button=['OK'],
                             defaultButton='OK', dismissString='OK')
        self.getFolderTree(fromDb=False)

