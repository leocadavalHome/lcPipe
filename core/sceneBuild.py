import pymel.core as pm
import os.path
from lcPipe.core import database
from lcPipe.api.item import Item
from lcPipe.api.sceneSource import SceneSource
from lcPipe.api.cameraComponent import CameraComponent
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)
logger.setLevel(10)


def build(itemType=None, task=None, code=None, silent=False):
    logger.debug('initiate Scene Building %s %s %s' % (task, code, itemType))
    parcial = False
    empty = True

    item = Item(task=task, code=code, itemType=itemType)

    if not item.source:
        logger.debug('No source found. Using components')
        logger.debug('components %s' % item.components)
        itemUnOrdered = item.components
    else:
        logger.debug('Using source')
        itemUnOrdered = item.source

    pm.newFile(f=True, new=True)
    newComponentsDict = {}

    itemDict = OrderedDict()
    parentList = ['']
    count = 0

    while len(itemUnOrdered) != len(itemDict):
        count += 1
        level = [[key, x['code']] for key, x in itemUnOrdered.iteritems() if x['onSceneParent'] in parentList]

        parentList = [x[1] for x in level]
        for x in level:
            itemDict[x[0]] = itemUnOrdered[x[0]]
        if count > 100:
            break

    logger.debug(itemDict)

    if item.type == 'shot':
        logger.debug('creating camera...')
        cameraItem = Item(task='rig', code='0000', itemType='asset')
        if cameraItem.noData:
            pm.confirmDialog(title='No base camera', ma='center',
                             message='Please make an asset code:0000 as base camera',
                             button=['OK'], defaultButton='OK', dismissString='OK')
            return

        cameraMData = {'code': '0000', 'ver': cameraItem.publishVer, 'updateMode': 'last',
                      'task': 'rig', 'assembleMode': 'camera', 'proxyMode': 'rig',
                       'onSceneParent': None, 'type': 'asset', 'xform': {}}
        camera = CameraComponent('cam', cameraMData, parent=item)

        camera.wrapData()
        if not camera.cameraTransform:
            camera.addToScene()
        newComponentsDict['cam'] = camera.getDataDict()
        empty = False

    for ns, sourceMData in itemDict.iteritems():
        source = SceneSource(ns, sourceMData, parent=item)
        if source.assembleMode == 'createGroup':
            source.createGroup()
        empty = False

    for ns, sourceMData in itemDict.iteritems():
        source = SceneSource(ns, sourceMData, parent=item)
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
            if not silent:
                pm.confirmDialog(title='Warning', ma='center',
                                 message='WARNING build: Some components have no publish to complete build this file!',
                                 button=['OK'], defaultButton='OK', dismissString='OK')
            else:
                logger.warn ('Some components have no publish to complete build this file!'
                             '')
            item.putDataToDB()
        else:
            if not silent:
                pm.confirmDialog(title='Warning', ma='center',
                                 message='%s assembled sucessfully!' % item.filename,
                                 button=['OK'], defaultButton='OK', dismissString='OK')
            else:
                logger.info('%s assembled sucessfully!' % item.filename)
    else:
        if not silent:
            pm.confirmDialog(title='Warning', ma='center',
                             message='ERROR build: No component published to build this file',
                             button=['OK'], defaultButton='OK', dismissString='OK')
        else:
            logger.error('No component published to build this file')
