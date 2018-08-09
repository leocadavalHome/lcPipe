import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.item import Item


def checkModified():
    import maya.cmds as cmds
    if cmds.file(q=True, modified=True):
        resp = cmds.confirmDialog (title='Unsaved Changes', message='Save changes on current file?',
                                 button=['Save', "Don't Save", 'Cancel'], defaultButton='Save',
                                 cancelButton='Cancel', dismissString='Cancel')
    else:
        resp = "Don't Save"
    return resp


def open (type, task, code, force=False):
    if not force:
        resp = checkModified()
        print resp
        if resp == 'Save':
            print pm.saveFile()

        elif resp == 'Cancel':
            print 'canceling'
            return

    print 'opening'
    item = Item(task=task, code=code, itemType=type)
    item.open()

def saveAs (type, task, code, force=True):
    pm.fileInfo['type'] = 'type'
    pm.fileInfo['task'] = 'task'
    pm.fileInfo['code'] = 'code'

    item = Item(task=task, code=code, itemType=type)
    item.saveAs()

def takeSnapShot(itemMData=None, thumbPath=None):
    if itemMData and not thumbPath:
        itemDir = database.getPath(itemMData, ext='thumb')

        thumbDir = os.path.join(itemDir[0], 'thumb')

        if not os.path.exists(thumbDir):
            os.makedirs(thumbDir)

        thumbPath = os.path.join(thumbDir, itemDir[1])

    print thumbPath
    pm.playblast(frame = 1, format="image", compression="jpg",orn=False,  cf=thumbPath , v=False, fo=True, wh=[100,100], p=100, os=True )


def getThumb( itemMData = None):
    itemDir = database.getPath(itemMData, ext='thumb')
    thumbDir = os.path.join(itemDir[0], 'thumb')
    thumbPath = os.path.join(thumbDir, itemDir[1])

    if os.path.isfile(thumbPath):
        return thumbPath
    else:
        if itemMData['type'] == 'asset':
            return 'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/block.png'
        elif itemMData['type'] == 'shot':
            return 'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/film.png'

