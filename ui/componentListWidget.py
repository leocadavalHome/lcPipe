import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import fileFunctions
from lcPipe.ui.componentWidget import ComponentWidget
from lcPipe.ui.folderTreeWidget import FolderTreeWidget
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.itemListBase import ItemListBase
import logging
logger = logging.getLogger(__name__)

class ComponentListWidget(ItemListBase):
    def __init__(self):
        self.item = None
        self.taskToList = ['rig', 'uvs']
        super(ComponentListWidget, self).__init__()

    def addMenus(self):
        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='add item', c=self.addItemCallBack)

    def dropCallback(self, dragControl, dropControl, messages, x, y, dragType):
        if messages[0] in self.taskToList:
            database.addComponent(self.item, 'ref', messages[0], messages[1], 'reference')
            self.refreshList(itemMData=self.item)
        else:
            pm.confirmDialog(title='error', ma='center', message='please choose rigs or uvs!', button=['OK'],
                             defaultButton='OK', dismissString='OK')

    def createList(self, parentWidget):
        self.parentWidget = parentWidget
        a = pm.scrollLayout(p=self.parentWidget, childResizable=True, h=200)
        self.widgetName = pm.flowLayout(p=a, backgroundColor=(.17, .17, .17), columnSpacing=5, h=1000, wrap=True,
                                        dropCallback=self.dropCallback)
        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='add item', c=self.addItemCallBack)

    def refreshList(self, path=None, task=None, code=None, itemMData=None):
        color = (0, 0, 0)
        createdColor = (0, .5, .20)
        notCreatedColor = (.2, .2, .2)

        if not itemMData:
            print 'ERROR: No search item!!'

        self.item = itemMData

        childs = pm.flowLayout(self.widgetName, q=True, ca=True)
        if childs:
            for i in childs:
                pm.deleteUI(i)

        self.itemList = []
        self.selectedItem = None

        for ns, component in itemMData['components'].iteritems():
            type = component['type']
            collection = database.getCollection(type, self.projectName)
            result = collection.find_one({'task': component['task'], 'code': component['code']})

            if not result:
                print 'component %s %s missing!' % (component['task'], component['code'])
                continue

            name = ns + ':' + database.getTaskShort(result['task']) + result['code'] + '_' + result['name']

            status = result['status']
            if status == 'notCreated':
                color = notCreatedColor
            elif status == 'created':
                color = createdColor

            thumbPath = fileFunctions.getThumb(result)
            x = ComponentWidget(name=name, itemName=result['name'], imgPath=thumbPath, label=result['task'],
                                status=result['status'], parentWidget=self, color=color)

            self.itemList.append(x)
            x.task = result['task']
            x.code = result['code']
            x.addToLayout(self.viewOption)

    def addItemCallBack(self, *args):
        pm.layoutDialog(ui=lambda: self.createAssetPrompt())
        self.refreshList(itemMData=self.item)

    def createAssetPrompt(self):
        form = pm.setParent(q=True)
        f = pm.formLayout(form, e=True, width=150)

        col2 = pm.columnLayout(p=f, adjustableColumn=True)
        nsField = pm.textFieldGrp('nsFieldPrompt', l='Name Space', tx='ref' )
        refModeField = pm.optionMenuGrp(l='Assemble Mode' )
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
        itemListWidget.refreshList(path=[], task=self.taskToList)

        infoWidget = InfoWidget()
        infoWidget.createInfo(pane)

        folderTreeWidget.itemListWidget = itemListWidget
        folderTreeWidget.itemListWidget.type = 'asset'
        folderTreeWidget.itemListWidget.task = self.taskToList
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
