import pymel.core as pm
import os.path
from core import database
from lcPipe.ui.folderTreeEditableWidget import FolderTreeEditableWidget


class ProjectSettingsWidget():
    def __init__(self, projectName=None):

        self.parentWidget = None
        self.projectName = projectName
        self.projDict = None
        self.new = False

        self.workLocTxt = None
        self.publishLocTxt = None
        self.imgWorkLocTxt = None
        self.imgPublishLocTxt = None
        self.cacheLocTxt = None

    def okCallback(self, *args):
        self.putProjectSettings()
        projName = self.projDict['projectName']

        if self.new:
            if not projName:
                print 'Please choose a name for the project!!'
                return

            existName = database.getProjectDict(projName)

            if existName:
                print 'This Name exists. Please choose another name'
                return

            print 'create project'
            print self.projDict
            database.addProject(**self.projDict)
            pm.deleteUI(self.parentWidget.projPopUp)
            self.parentWidget.makePopup()
            self.parentWidget.changeProjectCallBack(projName)

        else:
            print 'edit project'
            database.putProjectDict(self.projDict, projName)

        pm.deleteUI(self.win)

    def cancelCallback(self, *args):
        pm.deleteUI(self.win)

    def browseCallback(self, opt, *args):
        print 'browse'
        resultDir = pm.fileDialog2(cap='choose directory', okCaption='Select', fm=3, dialogStyle=2)
        if resultDir:
            selectDir = os.path.normpath(resultDir[0])
        else:
            return

        if opt == 1:
            pm.textFieldGrp(self.workLocTxt, e=True, text=selectDir)
        elif opt == 2:
            pm.textFieldGrp(self.publishLocTxt, e=True, text=selectDir)
        elif opt == 3:
            pm.textFieldGrp(self.imgWorkLocTxt, e=True, text=selectDir)
        elif opt == 4:
            pm.textFieldGrp(self.imgPublishLocTxt, e=True, text=selectDir)
        elif opt == 5:
            pm.textFieldGrp( self.cacheLocTxt, e=True, text=selectDir)

    def createProjectSettingsWidget(self):
        if not self.projectName:
            self.projDict = database.getDefaultDict()
        else:
            self.projDict = database.getProjectDict(self.projectName)

        self.win = pm.window(w=800, h=600)
        col = pm.columnLayout(adjustableColumn=True, columnAlign='left', )
        self.projNameTxt = pm.textFieldGrp(label='ProjectName', text=self.projDict['projectName'], cat=(1, 'left', 20),
                                           adj=2, editable=False)
        self.prefixTxt = pm.textFieldGrp(label='Prefix', text=self.projDict['prefix'], cat=(1, 'left', 20), adj=2,
                                         editable=False)
        self.statusOpt = pm.optionMenuGrp(l='Status', cat=(1, 'left', 20))
        pm.menuItem(label='inative')
        pm.menuItem(label='active')
        pm.menuItem(label='current')
        pm.optionMenuGrp(self.statusOpt, e=True, v=self.projDict['status'])
        self.workLocTxt = pm.textFieldButtonGrp(label='Work Location', text=self.projDict['workLocation'],
                                                buttonLabel='...', adj=2, cat=(1, 'left', 20), bc=lambda:self.browseCallback(1))
        self.publishLocTxt = pm.textFieldButtonGrp(label='Publish Location', text=self.projDict['publishLocation'],
                                                   buttonLabel='...', adj=2, cat=(1, 'left', 20), bc=lambda:self.browseCallback(2))
        self.imgWorkLocTxt = pm.textFieldButtonGrp(label='Images Work Location',
                                                   text=self.projDict['imagesWorkLocation'], buttonLabel='...', adj=2,
                                                   cat=(1, 'left', 20), bc=lambda:self.browseCallback(3))
        self.imgPublishLocTxt = pm.textFieldButtonGrp(label='Images Publish Location',
                                                      text=self.projDict['imagesPublishLocation'], buttonLabel='...',
                                                      adj=2, cat=(1, 'left', 20),  bc=lambda:self.browseCallback(4))
        self.cacheLocTxt = pm.textFieldButtonGrp(label='Cache Location', text=self.projDict['cacheLocation'],
                                                 buttonLabel='...', adj=2, cat=(1, 'left', 20), bc=lambda:self.browseCallback(5))
        self.assetCollTxt = pm.textFieldGrp(label='Asset Collection', text=self.projDict['assetCollection'], adj=2,
                                            cat=(1, 'left', 20), editable=False)
        self.shotCollTxt = pm.textFieldGrp(label='Shot Collection', text=self.projDict['shotCollection'], adj=2,
                                           cat=(1, 'left', 20), editable=False)
        self.nameTemplTxt = pm.textFieldGrp(label='Asset Name Template',
                                            text=','.join(self.projDict['assetNameTemplate']), adj=2,
                                            cat=(1, 'left', 20))
        self.cacheTemplTxt = pm.textFieldGrp(label='Cache Name Template',
                                             text=','.join(self.projDict['cacheNameTemplate']), adj=2,
                                             cat=(1, 'left', 20))
        self.rendererOpt = pm.optionMenuGrp(label='Renderer', cat=(1, 'left', 20))
        pm.menuItem(label='vray')
        pm.menuItem(label='arnold')
        pm.optionMenuGrp(self.rendererOpt, e=True, v=self.projDict['renderer'])
        self.resolutionOpt = pm.optionMenuGrp(l='Resolution', cat=(1, 'left', 20))
        pm.menuItem(label='1920x1080')
        pm.menuItem(label='2048x1780')
        pm.optionMenuGrp(self.resolutionOpt, e=True,
                         v='%sx%s' % (self.projDict['resolution'][0], self.projDict['resolution'][1]))
        pm.text(p=col, l='FOLDERS')

        pane = pm.paneLayout(p=col, cn='vertical2', h=150)
        self.assetTreeView = FolderTreeEditableWidget('asset')
        self.assetTreeView.createFolderTree(pane)
        self.assetTreeView.getFolderTree()
        self.assetTreeView.createMenus()

        self.shotTreeView = FolderTreeEditableWidget('shot')
        self.shotTreeView.createFolderTree(pane)
        self.shotTreeView.getFolderTree()
        self.shotTreeView.createMenus()

        pm.text(p=col, l='WORKFLOWS')
        pane = pm.paneLayout(p=col, cn='vertical2', h=100)

        self.workflowScrll = pm.textScrollList(parent=pane)
        for workflow in self.projDict['workflow']:
            pm.textScrollList(self.workflowScrll, e=True, append='     ' + workflow)

        pm.rowLayout(p=col, nc=3, adj=1)
        pm.text(l='')
        pm.button(l='OK', w=50, h=50, c=self.okCallback)
        pm.button(l='Cancel', w=50, h=50, c=self.cancelCallback)

        pm.showWindow()

    def putProjectSettings(self):
        self.projDict['projectName'] = pm.textFieldGrp(self.projNameTxt, q=True, text=True)
        self.projDict['prefix'] = pm.textFieldGrp(self.prefixTxt, q=True, text=True)
        self.projDict['status'] = pm.optionMenuGrp(self.statusOpt, q=True, v=True)
        self.projDict['workLocation'] = pm.textFieldButtonGrp(self.workLocTxt, q=True, text=True)
        self.projDict['publishLocation'] = pm.textFieldButtonGrp(self.publishLocTxt, q=True, text=True)
        self.projDict['imagesWorkLocation'] = pm.textFieldButtonGrp(self.imgWorkLocTxt, q=True, text=True)
        self.projDict['imagesPublishLocation'] = pm.textFieldButtonGrp(self.imgPublishLocTxt, q=True, text=True)
        self.projDict['cacheLocation'] = pm.textFieldButtonGrp(self.cacheLocTxt, q=True, text=True)
        self.projDict['assetCollection'] = self.projDict['projectName'] + '_asset'
        self.projDict['shotCollection'] = self.projDict['projectName'] + '_shot'
        nameTemplateString = pm.textFieldGrp(self.nameTemplTxt, q=True, text=True)
        self.projDict['assetNameTemplate'] = nameTemplateString.split(',')
        cacheTemplateString = pm.textFieldGrp(self.cacheTemplTxt, q=True, text=True)
        self.projDict['cacheNameTemplate'] = cacheTemplateString.split(',')
        self.projDict['renderer'] = pm.optionMenuGrp(self.rendererOpt, q=True, v=True)

        res = pm.optionMenuGrp(self.resolutionOpt, q=True, v=True)
        self.projDict['resolution'] = [int(res.split('x')[0]), int(res.split('x')[1])]

        self.projDict['assetFolders'] = self.assetTreeView.putFolderTree()
        self.projDict['shotFolders'] = self.shotTreeView.putFolderTree()
