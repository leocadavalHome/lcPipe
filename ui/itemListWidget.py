import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import version
from lcPipe.ui.itemWidget import ItemWidget
from lcPipe.ui.itemListBase import ItemListBase
import time
import logging
import os.path
logger = logging.getLogger(__name__)

class ItemListWidget(ItemListBase):
    def __init__(self):
        super(ItemListWidget, self).__init__()

    def addMenus(self):
        pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='add item', c=self.addItemCallBack)

    def refreshList(self, path=None, task=None, code=None, itemMData=None):
        color = (0, 0, 0)

        start_time = time.time()
        itemListProj = database.getProjectDict()

        if itemMData:
            self.path = itemMData['path']
            self.task = itemMData['task']
            self.type = itemMData['type']
        else:
            self.path = path
            self.task = task
            self.type = database.getTaskType(task)

        collection = database.getCollection(self.type)

        if code:
            result = collection.find({'path': self.path, 'code': code})
        else:
            if self.task == 'asset':
                result = collection.find({'path': self.path, 'task': 'model'})
            elif self.task == 'shot':
                result = collection.find({'path': self.path, 'task': 'layout'})
            else:
                result = collection.find({'path': self.path, 'task': task})

        elapsed_time = time.time () - start_time
        logger.debug('%s to get items from db' % elapsed_time)

        start_time = time.time ()
        flowChilds = pm.flowLayout(self.widgetName, q=True, ca=True)
        if flowChilds:
            for i in flowChilds:
                pm.deleteUI(i)

        self.itemList = []
        self.selectedItem = None

        for itemMData in result:
            if not code and (task == 'asset' or task == 'shot'):
                templateToUse = [x for x in itemListProj['assetNameTemplate'] if x != '$task']
                name = database.templateName(itemMData, template=templateToUse)
                taskLabel = task.upper()
                createdColor = (0, .2, .50)
                notCreatedColor = (0, .2, .50)
            else:
                name = database.templateName(itemMData)
                taskLabel = itemMData['task'].upper()
                notCreatedColor = (.2, .2, .2)
                createdColor = (1, .8, .20)

            status = itemMData['status']
            if status == 'notCreated':
                color = notCreatedColor
            elif status == 'created':
                color = createdColor

            thumbPath = version.getThumb(itemMData)
            x = ItemWidget(name=name, itemName=itemMData['name'], imgPath=thumbPath, label=taskLabel, status=itemMData['status'],
                           parentWidget=self, color=color)
            x.infoWidget = self.infoWidget

            if code:
                x.task = itemMData['task']
                x.workVer = itemMData['workVer']
                x.publishVer = itemMData['publishVer']
            else:
                x.task = self.task
                x.workVer = 0
                x.publishVer = 0

            x.code = itemMData['code']
            self.itemList.append(x)
            x.addToLayout(self.viewOption)

        elapsed_time = time.time() - start_time
        logger.debug('%s to put items on ui' % elapsed_time)

    def addItemCallBack(self, *args):
        if not self.path:
            return pm.confirmDialog(title='error', ma='center',
                                    message='please choose a folder where to create the asset', button=['OK'],
                                    defaultButton='OK', dismissString='OK')

        pm.layoutDialog(ui=lambda: self.createAssetPrompt())
        self.refreshList(path=self.path, task=self.task)

    def createAssetPrompt(self):
        code = ''

        proj = database.getProjectDict()
        if self.type == 'asset':
            code = "%04d" % proj['nextAsset']
        elif self.type == 'shot':
            code = "%04d" % proj['nextShot']

        form = pm.setParent(q=True)
        f = pm.formLayout(form, e=True, width=150)
        row = pm.rowLayout(nc=2, adj=2)
        pm.picture(image='sphere.png', w=50, h=50)
        col = pm.columnLayout(adjustableColumn=True)
        nameField = pm.textFieldGrp('CrAsset_nameField', label='Name', cw=(1, 70), text='', adj=2,
                                    cat=[(1, 'left', 5), (2, 'left', 5)], editable=True)
        codeField = pm.textFieldGrp('CrAsset_codeField', label='Code', cw=(1, 70), text=code, adj=2,
                                    cat=[(1, 'left', 5), (2, 'left', 5)], editable=True)
        workflow = pm.optionMenuGrp('CrAsset_workflowOpt', label='Workflow', cw=(1, 70),
                                    cat=[(1, 'left', 5), (2, 'left', 5)])
        proj = database.getProjectDict()

        for key in proj['workflow']:
            context = set([proj['workflow'][key][x]['type'] for x in proj['workflow'][key]])
            if self.type in context:
                pm.menuItem(label=key)

        b1 = pm.button(p=f, l='Cancel', c=self.abortCreateCallback)
        b2 = pm.button(p=f, l='OK', c=self.createAssetCallBack)

        if self.type == 'shot':
            range = pm.intFieldGrp('rangeField', p=form, numberOfFields=2, label='start', extraLabel='end', value1=1, value2=48 )
            #self.soundPath = pm.textFieldButtonGrp('sound', p=form, label='sound', buttonLabel='...',
            #                                  adj=2, cat=[(1, 'left', 20)], bc=lambda: self.browseCallback(1))
            spacer = 5
            top = 5
            edge = 5
            # todo adjust create asset(shot) sound layout!
            pm.formLayout (form, edit=True,
                           attachForm=[(row, 'right', edge), (row, 'top', top), (row, 'left', edge),
                                       (row, 'right', edge),
                                       (b1, 'right', edge), (b1, 'bottom', edge), (b2, 'left', edge),
                                       (b2, 'bottom', edge)],
                           attachNone=[], attachControl=[(range, 'top', spacer, row), (range, 'bottom', spacer, row)],
                                                         # (range, 'bottom', spacer, self.soundPath),
                                                         # (self.soundPath, 'bottom', spacer, b1)],
                           attachPosition=[(b1, 'right', spacer, 90), (b2, 'left', spacer, 10)])

        else:
            spacer = 5
            top = 5
            edge = 5
            pm.formLayout(form, edit=True,
                          attachForm=[(row, 'right', edge), (row, 'top', top), (row, 'left', edge), (row, 'right', edge),
                                      (b1, 'right', edge), (b1, 'bottom', edge), (b2, 'left', edge), (b2, 'bottom', edge)],
                          attachNone=[], attachControl=[],
                          attachPosition=[(b1, 'right', spacer, 90), (b2, 'left', spacer, 10)])


    def abortCreateCallback(self, *args):
        pm.layoutDialog(dismiss="Abort")

    def createAssetCallBack(self, *args):
        name = pm.textFieldGrp('CrAsset_nameField', q=True, tx=True)
        if not name:
            return pm.confirmDialog(title='error', ma='center', message='please choose a name for the asset',
                                    button=['OK'], defaultButton='OK', dismissString='OK')
        workflow = pm.optionMenuGrp('CrAsset_workflowOpt', q=True, v=True)
        code = pm.textFieldGrp('CrAsset_codeField', q=True, tx=True)

        if self.type == 'shot':
            start = pm.intFieldGrp('rangeField', q=True, value1=True)
            end = pm.intFieldGrp('rangeField', q=True, value2=True)
            itemDict = database.createItem(self.type, name, self.path, workflow, code=code, frameRange=[start, end])
        else:
            itemDict = database.createItem(self.type, name, self.path, workflow, code=code)

        if itemDict == 'codeExists':
            return pm.confirmDialog(title='error', ma='center', message='this code already exists', button=['OK'],
                                    defaultButton='OK', dismissString='OK')

        pm.layoutDialog(dismiss='ok')

    def browseCallback(self, opt, *args):
        resultDir = pm.fileDialog2(cap='choose sound', okCaption='Select', fm=1, dialogStyle=2)
        if resultDir:
            selectDir = os.path.normpath(resultDir[0])
        else:
            return

        if opt == 1:
            pm.textFieldGrp(self.soundPath, e=True, text=selectDir)
