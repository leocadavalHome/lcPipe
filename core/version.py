import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.item import Item
import logging

logger = logging.getLogger(__name__)

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

        if resp == 'Save':
            pm.saveFile()

        elif resp == 'Cancel':
            return

    item = Item(task=task, code=code, itemType=type)
    item.open()

def saveAs (task=None, code=None, type=None):
    item = Item(task=task, code=code, itemType=type)

    if item:
        pm.fileInfo['type'] = item.type
        pm.fileInfo['task'] = item.task
        pm.fileInfo['code'] = item.code

        item.saveAs()

        item.status='created'
        item.putDataToDB()


def takeSnapShot(itemMData=None, thumbPath=None):
    if itemMData and not thumbPath:
        itemDir = database.getPath(itemMData, ext='thumb')

        thumbDir = os.path.join(itemDir[0], 'thumb')

        if not os.path.exists(thumbDir):
            os.makedirs(thumbDir)

        thumbPath = os.path.join(thumbDir, itemDir[1])

    pm.playblast(frame = 1, format="image", compression="jpg",orn=False,  cf=thumbPath , v=False, fo=True, wh=[100,100], p=100, os=True )


def getThumb( itemMData = None):
    itemDir = database.getPath(itemMData, ext='thumb')
    thumbDir = os.path.join(itemDir[0], 'thumb')
    thumbPath = os.path.join(thumbDir, itemDir[1])

    if os.path.isfile(thumbPath):
        return thumbPath
    else:
        if itemMData['type'] == 'asset':
            return 'block.png'
        elif itemMData['type'] == 'shot':
            return 'film.png'

