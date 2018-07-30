import pymel.core as pm
from lcPipe.core import database
from lcPipe.ui.projectSettingsWidget import ProjectSettingsWidget


class ProjectSelectWidget:
    def __init__(self):
        self.widgetName = None
        self.parentWidget = None
        self.projectName = None
        self.folderTreeWidget = None
        self.itemListWidget = None

    def makePopup(self):
        self.projPopUp = pm.popupMenu(parent=self.widgetName)
        pm.menuItem(label='new project', c=self.newProjectCallback)

        allProjects = database.getAllProjects()

        for proj in allProjects:
            if not self.projectName:
                self.projectName = proj['projectName']
                database.setCurrentProject(self.projectName)
                self.changeProjectCallBack(self.projectName)

            pm.menuItem(label=proj['projectName'], c=lambda x, y=proj['projectName']: self.changeProjectCallBack(y))

    def createProjectSelect(self, parent):
        self.parentWidget = parent
        self.widgetName = pm.textFieldButtonGrp('projectSel', p=self.parentWidget, label='ProjectName', text='projeto',
                                                cat=[[1, 'left',5],[2,'left',-50]] , adj=2, bl='...', bc=self.projectSettingsCallback)
        pm.separator(height=40, style='in')
        self.makePopup()

    def newProjectCallback(self, *args):
        proj = ProjectSettingsWidget()
        proj.createProjectSettingsWidget()
        proj.new = True
        proj.parentWidget = self
        pm.textFieldGrp(proj.projNameTxt, e=True, editable=True)
        pm.textFieldGrp(proj.prefixTxt, e=True, editable=True)

    def projectSettingsCallback(self, *args):
        proj = ProjectSettingsWidget(self.projectName)
        proj.createProjectSettingsWidget()

    def changeProjectCallBack(self, projName):
        pm.textFieldButtonGrp(self.widgetName, e=True, text=projName)

        if self.projectName != projName:
            self.projectName = projName
            database.setCurrentProject(self.projectName)

            if self.folderTreeWidget:
                self.folderTreeWidget.projectName = self.projectName
                self.folderTreeWidget.getFolderTree()

            if self.itemListWidget:
                self.itemListWidget.projectName = self.projectName
                self.itemListWidget.refreshList(path=[], task=self.itemListWidget.task)

    def getProject(self):
        shortName = pm.layout(self.widgetName, q=True, ca=True)[1]
        fullName = pm.layout(shortName, q=True, fpn=True)
        projName = pm.textField(fullName, q=True, text=True)
        proj = database.getProjectDict(projName)
        return proj
