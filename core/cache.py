import copy

import pymel.core as pm
import os.path
from lcPipe.core import database

reload(database)


def cachePrompt(refs):
    """

    :rtype: None
    :param refs: string list
    """
    form = pm.setParent(q=True)
    pm.formLayout(form, e=True, width=300)
    t = pm.text(l='geo groups to cache')
    t2 = pm.text(l='change selection')
    b3 = pm.button(l='Cancel', c='pm.layoutDialog( dismiss="Abort" )')
    # b2 = pm.button(l='Cancel', c='pm.layoutDialog( dismiss="Cancel" )' )
    b1 = pm.button(l='OK', c=lambda x: cachePromptChangeList())
    cb1 = pm.textScrollList('cacheScrollList', allowMultiSelection=True, si=refs, append=refs)
    spacer = 5
    top = 5
    edge = 5
    pm.formLayout(form, edit=True,
                  attachForm=[(cb1, 'right', edge), (t, 'top', top), (t, 'left', edge), (t, 'right', edge),
                              (t2, 'left', edge), (t2, 'right', edge), (b1, 'left', edge), (b1, 'bottom', edge),
                              (b3, 'bottom', edge), (b3, 'right', edge), (cb1, 'left', edge)],

                  attachNone=[(t, 'bottom')], attachControl=[(cb1, 'top', spacer, t2), (t2, 'top', spacer, t)],
                  attachPosition=[(b1, 'right', spacer, 33), (b3, 'left', spacer, 66)])


def cachePromptChangeList(*args):
    """

    :rtype: object
    """
    sel = pm.textScrollList('cacheScrollList', q=True, si=True)
    selString = ','.join(sel)
    pm.layoutDialog(dismiss=selString)


def cacheScene(task, code):
    ver = 0

    collection = database.getCollection('shot')
    shotMData = database.getItemMData(task=task, code=code, itemType='shot')

    if 'caches' not in shotMData:
        shotMData['caches'] = copy.deepcopy(shotMData['components'])

        for item in shotMData['caches'].itervalues():
            item['ver'] = 0
            item['type'] = 'cache'
            item['assembleMode'] = 'cache'
            item['cacheVer'] = 0
            item['name'] = ''

    itemComponents = shotMData['components']
    itemCaches = shotMData['caches']
    geoGroups = pm.ls('geo_group', r=True)

    choosen = pm.layoutDialog(ui=lambda: cachePrompt(geoGroups))

    if 'Abort' in choosen:
        return

    path = database.getPath(shotMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    if not os.path.exists(cachePath):
        os.makedirs(cachePath)

    choosenGeoGroups = [pm.PyNode(x) for x in choosen.split(',')]

    for geoGroup in choosenGeoGroups:
        # get all geometry on geo_group
        geosShape = geoGroup.getChildren(allDescendents=True, type='geometryShape')
        geos = [x.getParent() for x in geosShape]
        jobGeos = ''

        for geo in geos:
            if '|' in geo:

                print 'PROBLEMA de nomeacao na geo %s' % geo
            else:
                jobGeos = jobGeos + ' -root ' + geo

                # make path and name for alembic file

        ns = geoGroup.namespace()[:-1]
        cacheMData = itemCaches[ns]  # get the data for this component

        # get version and increment
        cacheMData['cacheVer'] += 1

        ver = cacheMData['cacheVer']

        # get cache publish path

        cacheName = database.templateName(cacheMData) + '_' + ns
        cacheFileName = str('v%03d_' % ver) + cacheName
        cacheFullPath = os.path.join(cachePath, cacheFileName)

        jobFile = " -file " + cacheFullPath + ".abc "

        # get scene frame range
        ini = str(int(pm.playbackOptions(q=True, min=True)))
        fim = str(int(pm.playbackOptions(q=True, max=True)))
        jobFrameRange = ' -frameRange ' + ini + ' ' + fim

        # set parameters for alembic cache     
        jobAttr = ' -attr translateX -attr translateY -attr translateZ -attr rotateX ' \
                  '-attr rotateY -attr rotateZ -attr scaleX -attr scaleY -attr scaleZ -attr visibility'
        jobOptions = " -worldSpace -uv -writeVisibility"

        # build cache arguments
        jobArg = jobFrameRange + jobOptions + jobAttr + jobGeos + jobFile

        # do caching
        pm.AbcExport(j=jobArg)

    collection.find_one_and_update({'task': task, 'code': code}, {'$set': shotMData})

    pm.confirmDialog(title='cache', ma='center', icon='information', message='Cache Ver: %s' % ver, button=['OK'],
                     defaultButton='OK', dismissString='ok')


def cacheCamera(task, code):
    ver = 0
    collection = database.getCollection('shot')
    shotMData = database.getItemMData(task=task, code=code, itemType='shot')

    if 'caches' not in shotMData:
        shotMData['caches'] = copy.deepcopy(shotMData['components'])

        for item in shotMData['caches'].itervalues():
            item['ver'] = 0
            item['type'] = 'cache'
            item['assembleMode'] = 'cache'
            item['cacheVer'] = 0
            item['name'] = ''

    itemComponents = shotMData['components']
    itemCaches = shotMData['caches']

    cameras = pm.ls(type='camera', l=True)
    startup_cameras = [camera for camera in cameras if pm.camera(camera.parent(0), startupCamera=True, q=True)]
    cameraShape = list(set(cameras) - set(startup_cameras))
    camera = map(lambda x: x.parent(0), cameraShape)[0]

    path = database.getPath(shotMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    if not os.path.exists(cachePath):
        os.makedirs(cachePath)

    # get all geometry on geo_group
    jobCam = ' -root ' + camera

    # make path and name for alembic file
    cacheMData = itemCaches['cam']  # get the data for this component

    # get version and increment
    cacheMData['cacheVer'] += 1

    ver = cacheMData['cacheVer']

    # get cache publish path

    cacheName = database.templateName(cacheMData) + '_cam'
    cacheFileName = str('v%03d_' % ver) + cacheName
    cacheFullPath = os.path.join(cachePath, cacheFileName)

    jobFile = " -file " + cacheFullPath + ".abc "

    # get scene frame range
    ini = str(int(pm.playbackOptions(q=True, min=True)))
    fim = str(int(pm.playbackOptions(q=True, max=True)))
    jobFrameRange = ' -frameRange ' + ini + ' ' + fim

    # set parameters for alembic cache
    jobAttr = ' -attr translateX -attr translateY -attr translateZ -attr rotateX ' \
              '-attr rotateY -attr rotateZ -attr scaleX -attr scaleY -attr scaleZ -attr visibility'
    jobOptions = " -worldSpace -writeVisibility"

    # build cache arguments
    jobArg = jobFrameRange + jobOptions + jobAttr + jobCam + jobFile

    # do caching
    pm.AbcExport(j=jobArg)

    collection.find_one_and_update({'task': task, 'code': code}, {'$set': shotMData})