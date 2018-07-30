import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import check
from lcPipe.ui import widgets
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget
print 'init'
all = database.getAllProjects()
allProjects = [x for x in all]
print allProjects

if not allProjects:
    print 'no project found!!'

    result = pm.promptDialog(
            title='No project',
            message='No project Found! Enter Name for a new one:',
            button=['OK', 'Cancel'],
            defaultButton='OK',
            cancelButton='Cancel',
            dismissString='Cancel')

    if result == 'OK':
        text = cmds.promptDialog(query=True, text=True)
        print text
        database.addProject(projectName=text, prefix=text[:1])

itemMData = database.getItemMData(projName=self.projectName, task=self.task, code=self.code,
                                   itemType=self.type, fromScene=self.fromScene)

from lcPipe.core import check
pm.scriptJob(event=['SceneOpened', check.sceneRefCheck])