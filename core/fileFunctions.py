import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.item import Item
import logging
from lcPipe.api.cameraComponent import CameraComponent
import json

logger = logging.getLogger(__name__)
logger.setLevel(10)

def checkModified():
    import maya.cmds as cmds
    if cmds.file(q=True, modified=True):
        resp = cmds.confirmDialog (title='Unsaved Changes', message='Save changes on current file?',
                                 button=['Save', "Don't Save", 'Cancel'], defaultButton='Save',
                                 cancelButton='Cancel', dismissString='Cancel')
    else:
        resp = "Don't Save"
    return resp


def openFile (type, task, code, force=False):
    if not force:
        resp = checkModified()

        if resp == 'Save':
            pm.saveFile()

        elif resp == 'Cancel':
            return

    item = Item(task=task, code=code, itemType=type)
    item.openServer()

def saveFileAs (task=None, code=None, type=None):
    openItem = Item(fromScene=True)
    if openItem.noData:
        comps=[]
    else:
        comps=openItem.components


    item = Item(task=task, code=code, itemType=type)
    item.components = comps

    if item:
        pm.fileInfo['type'] = item.type
        pm.fileInfo['task'] = item.task
        pm.fileInfo['code'] = item.code

        item.saveAsServer()

        item.status = 'created'
        item.putDataToDB()


def saveFileLocal():
    openItem = Item(fromScene=True)
    openItem.saveAsLocal()

    project = database.getProjectDict()
    mDataDir = os.path.join(project['localWorkLocation'],'mData')
    if not os.path.exists(mDataDir):
        os.makedirs(mDataDir)

    jsonProjFile = []
    projData = {'projectName': project['projectName'], 'assetFolders': project['assetFolders'],
                'shotFolders': project['shotFolders'], 'allAssetTasks': database.getAllTasks('asset'),
                'allShotTasks': database.getAllTasks('shot')}

    if not os.path.isfile(os.path.join(mDataDir, 'project.json')):
        jsonProjFile.append(projData)
        with open(os.path.join(mDataDir, 'project.json'), 'w') as f:
            json.dump(jsonProjFile, f)
    else:
        with open(os.path.join(mDataDir, 'project.json')) as f:
            jsonProjFile = json.load(f)

        searchProj = [x for x in jsonProjFile if x['projectName'] == project['projectName']]

        if not searchProj:
            jsonProjFile.append(projData)
            with open(os.path.join(mDataDir, 'project.json'), 'w') as f:
                json.dump(jsonProjFile, f)

    fileName = openItem.type+'_'+openItem.task+'_'+openItem.code+'.json'
    jsonPath = os.path.join(mDataDir, fileName)

    logger.debug('jsonPath: %s ' % jsonPath)

    mData = openItem.getDataDict()

    with open(jsonPath, 'w') as f:
        json.dump(mData, f)


def saveFileServer():
    openItem = Item(fromScene=True)
    openItem.saveAsServer()


def saveAsNextShot():
    item = Item (fromScene=True)
    code = '%04d' % (int (pm.fileInfo['code']) + 1)
    task = pm.fileInfo['task']

    nextItem = database.getItemMData (task=task, code=code)
    if not nextItem:
        resp = pm.confirmDialog (title='No Asset Data', message='No shot found on next code. Create?',
                                 button=['Yes', "No", 'Cancel'], defaultButton='Yes',
                                 cancelButton='Cancel', dismissString='Cancel')
        if resp == 'Yes':
            try:
                num = int (item.name[-3:]) + 1
                numSulfix = '%03d' % num
                fileName = item.name[:-3] + numSulfix
            except (ValueError, TypeError):
                numSulfix = '000'
                fileName = item.name + numSulfix

            sceneStart = pm.playbackOptions (ast=True, q=True)
            sceneEnd = pm.playbackOptions (aet=True, q=True)

            itemMData = database.createItem (itemType='shot', name=fileName, code=code, path=item.path,
                                             frameRange=[sceneStart, sceneEnd], workflow=item.workflow)

    saveFileAs(task=task, code=code)

    item = Item (fromScene=True)
    camera = CameraComponent (ns='cam', parent=item)
    camera.renameToScene ()


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

