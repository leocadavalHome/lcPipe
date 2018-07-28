import lcPipe.api.item as it
import  lcPipe.api.xloComponent as xlo
from lcPipe.api.cacheComponent import CacheComponent
import lcPipe.api.sceneSource as ss
import lcPipe.core.check as ck
import lcPipe.api.component as cp
import lcPipe.core.database as dbase
import pymel.core as pm

reload(ss)
reload(ck)
reload (it)
reload (cp)
reload (xlo)

item = it.Item(task='layout', code='0002')
print item.getDataDict()

def getPhase(itemMData):
    project = dbase.getProjectDict()
    return project['workflow'][itemMData['workflow']][itemMData['task']]['phase']


def getShotCreatedTasks (itemMData):
    collection = dbase.getCollection('shot')
    cursor = collection.find({'status': {'$nin': ['notCreated']}, 'code': itemMData['code']})
    result = []
    for task in cursor:
        del task['_id']
        if getPhase(task)=='prod':
            result.append(task)
    return result




taskList =  getShotCreatedTasks (item.getDataDict())
for a in taskList:
    print a

ns = 'ref'
createdTasks = dbase.getShotCreatedTasks (item.getDataDict())
for itemMData in createdTasks:
    print itemMData
    if itemMData['task'] == 'layout':
        print 'layout', itemMData
    #dbase.addComponent (itemMData, ns, component.task, component.code, 'reference')


def checkModified():
    import maya.cmds as cmds
    if cmds.file(q=True, modified=True):
        resp = pm.confirmDialog(title='Unsaved Changes', message='Save changes on current file?', button=['Save',"Don't Save", 'Cancel'], defaultButton='Save',
                          cancelButton='Cancel', dismissString='Cancel')
    return resp
checkModified()