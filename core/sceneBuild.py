import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.item import Item
from lcPipe.api.sceneSource import SceneSource
from lcPipe.api.cameraComponent import CameraComponent
import logging

logger = logging.getLogger(__name__)
logger.setLevel(10)


def build(itemType, task, code):
    logger.debug('initiate Scene Building %s %s %s' % (task, code, itemType))
    parcial = False
    empty = True

    item = Item(task=task, code=code, itemType=itemType)

    if not item.source:
        logger.debug('No source found. Using components')
        logger.debug('components %s' % item.components)
        itemList = item.components
    else:
        logger.debug('Using source')
        itemList = item.source

    pm.newFile(f=True, new=True)
    newComponentsDict = {}

    if item.type == 'shot':
        logger.debug('creating camera...')
        cameraItem = Item(task='rig', code='0000', itemType='asset')
        if cameraItem.noData:
            pm.confirmDialog(title='No base camera', ma='center',
                             message='Please make an asset code:0000 as base camera',
                             button=['OK'], defaultButton='OK', dismissString='OK')
            return

        cameraMData = {'code': '0000', 'ver': cameraItem.publishVer, 'updateMode': 'last',
                      'task': 'rig', 'assembleMode': 'camera','proxyMode':'rig', 'type': 'asset'}
        camera = CameraComponent('cam', cameraMData, parent=item)

        camera.wrapData()
        if not camera.cameraTransform:
            camera.addToScene()
        newComponentsDict['cam'] = camera.getDataDict()

    logger.debug('item list %s' % itemList)
    for ns, sourceMData in itemList.iteritems():
        source = SceneSource(ns, sourceMData, parent=item)
        logger.debug('source component %s' % source.getDataDict())
        sourceItem = source.getItem()

        if sourceItem.publishVer == 0:
            logger.warn('Component %s not yet published!!' % (ns + ':' + source.task + source.code))
            parcial = True
            newComponentsDict[ns] = sourceMData
            continue

        empty = False

        if source.assembleMode == 'import':
            source.importToScene()

        elif source.assembleMode == 'reference':
            newComponentsDict[ns] = source.addReferenceToScene()

        elif source.assembleMode == 'copy':
            newComponentsDict = source.copyToScene()

        elif source.assembleMode == 'cache':
            newComponentsDict = source.addCacheToScene()

        elif source.assembleMode == 'xlo':
            newComponentsDict = source.addXloToScene()

    item.components = newComponentsDict

    # update infos on scene and database
    if not empty or not item.components:
        pm.fileInfo['projectName'] = database.getCurrentProject()
        pm.fileInfo['task'] = item.task
        pm.fileInfo['code'] = item.code
        pm.fileInfo['type'] = item.type

        if item.type == 'shot':
            pm.playbackOptions(ast=item.frameRange[0], aet=item.frameRange[1])
            pm.currentUnit(time='film')

        item.workVer = 1
        item.status = 'created'

        item.putDataToDB()
        sceneDirPath = item.getPath()[0]
        sceneFullPath = item.getWorkPath()

        if not os.path.exists(sceneDirPath):
            os.makedirs(sceneDirPath)

        pm.saveAs(sceneFullPath)

        if parcial:  # todo make parcial rebuild
            item.status = 'partial'
            pm.confirmDialog(title='Warning', ma='center',
                             message='WARNING build: Some components have no publish to complete build this file!',
                             button=['OK'], defaultButton='OK', dismissString='OK')
            item.putDataToDB()
        else:
            pm.confirmDialog(title='Warning', ma='center',
                             message='%s assembled sucessfully!' % item.filename,
                             button=['OK'], defaultButton='OK', dismissString='OK')

    else:
        pm.confirmDialog(title='Warning', ma='center',
                         message='ERROR build: No component published to build this file',
                         button=['OK'], defaultButton='OK', dismissString='OK')

