import pymel.core as pm
from lcPipe.core import database
from lcPipe.core import version
from lcPipe.api.cameraComponent import CameraComponent
from lcPipe.api.item import Item

def saveAsNextShot():
    item = Item(fromScene=True)
    code = '%04d' % (int(pm.fileInfo['code'])+1)
    task = pm.fileInfo['task']

    nextItem = database.getItemMData(task=task, code=code)
    if not nextItem:
        resp = pm.confirmDialog (title='No Asset Data', message='No shot found on next code. Create?',
                                 button=['Yes', "No", 'Cancel'], defaultButton='Yes',
                                 cancelButton='Cancel', dismissString='Cancel')
        if resp == 'Yes':
            try:
                num = int(item.name[-3:])+1
                numSulfix = '%03d' % num
                fileName = item.name[:-3] + numSulfix
            except (ValueError, TypeError):
                numSulfix = '000'
                fileName = item.name + numSulfix

            sceneStart = pm.playbackOptions (ast=True, q=True)
            sceneEnd = pm.playbackOptions (aet=True, q=True)

            itemMData = database.createItem(itemType='shot', name=fileName, code=code, path=item.path,
                                            frameRange=[sceneStart, sceneEnd], workflow=item.workflow)

    version.saveAs(task=task, code=code)

    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)
    camera.renameToScene()]

ingestSet(descFileName=r'howlingtonClassroom_modeling_proxy_model_desc.v006.json',
          pathSrc=r'T:\FromFB\howlingtonClassroom', pathTgt=['set'], selectiveIngest=True,
          pathPieceSrc=r'T:\FromFB\howlingtonClassroom\wolftv\asset\set_piece', pathPieceTgt=['setPiece'])