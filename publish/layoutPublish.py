import pymel.core as pm
import os.path
import logging
import lcPipe.core.database as database
import lcPipe.core.check as check
from lcPipe.api.item import Item
from lcPipe.publish.playblaster import PlayBlaster
from lcPipe.api.cameraComponent import CameraComponent

logger = logging.getLogger(__name__)
logger.setLevel(10)

# validates
# done Check for project settings like resolution size and FPS.
# done Check for camera name.
# done Check for audio name.
# done Remove the references that are switched off.

# pre-publish:
# done Check for file name. No need...
# done Check for assets name.
# done Check for playblast size and FPS
# todo Export the cameras.
# todo Remove unwanted nodes. (can harm the file)

def checkAudioFile(*args):
    item = Item(fromScene=True)

    sound = pm.ls(type='sound')
    if not sound:
        return False

    if len(sound) > 1:
        logger.warn('More than on sound file!')
        return True

    if sound[0] != item.name+'Sound':
        return True


def correctFps (*args):
    projectDict = database.getProjectDict()
    sceneFps = pm.currentUnit(q=True, time=True)
    if projectDict['fps'] != sceneFps:
        return True


def fixFpsNoChangeKey(*args):
    projectDict = database.getProjectDict()
    item = Item(fromScene=True)
    pm.currentUnit(time=projectDict['fps'], ua=False)
    logger.debug(item.frameRange)
    pm.playbackOptions(ast=item.frameRange[0], aet=item.frameRange[1])
    return 'ok'


def fixFpsChangeKey(*args):
    projectDict = database.getProjectDict()
    item = Item(fromScene=True)
    pm.currentUnit(time=projectDict['fps'], ua=True)
    logger.debug(item.frameRange)
    pm.playbackOptions(ast=item.frameRange[0],min=item.frameRange[0], aet=item.frameRange[1], max= item.frameRange[1])
    return 'ok'

def correctTimeRange(*args):
    item = Item(fromScene=True)

    sceneStart = pm.playbackOptions (ast=True, q=True)
    sceneEnd = pm.playbackOptions (aet=True, q=True)

    if item.frameRange[0]!=sceneStart or item.frameRange[1]!=sceneEnd:
        return True


def fixTimeRange(*args):
    item = Item(fromScene=True)
    pm.playbackOptions(ast=item.frameRange[0], min=item.frameRange[0], aet=item.frameRange[1], max=item.frameRange[1])
    return 'ok'


def cameraAspectCheck(*args):
    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)

    projectDict = database.getProjectDict()
    width, height = projectDict['resolution']

    projectAspect = float(width)/float(height)

    if abs(projectAspect-camera.cameraAspect) > 0.01:
        return True

def fixCameraAspect(*args):
    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)

    projectDict = database.getProjectDict()

    width, height = projectDict['resolution']
    projectAspect = float (width) / float (height)

    camera.cameraAspect = projectAspect
    return 'ok'

def cameraNameCheck (*args):
    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)

    correctCameraName = 'cam:'+item.projPrefix + item.code + '_' + item.name + '_camera'

    if camera.cameraTransform != correctCameraName:
        return True


def renameCamera(*args):
    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)
    camera.renameToScene()
    return 'ok'

def NoReferenceOff(*args):

    allReferences = pm.getReferences()

    for ref in allReferences.itervalues():
        if not ref.isLoaded():
            return True

def removeUnloadedRefs (*args):
    allReferences = pm.getReferences()

    for ref in allReferences.itervalues():
        if not ref.isLoaded():
            try:
                ref.remove()
            except RuntimeError:
                ref.load()
                ref.remove()


def doSceneCheck(*args):
    check.sceneRefCheck()

def doPlayBlast(*args):
    # todo check project resolution, set camera, set window and playblast
    projectDict = database.getProjectDict()

    item = Item(fromScene=True)
    sound = pm.ls(item.name+'Sound', type='sound')
    moviePath = os.path.join(projectDict['playblastLocation'], item.filename+'Preview.mov')
    logger.debug(projectDict['resolution'])
    if sound:
        pblast = PlayBlaster(item=item, sound=sound[0], moviePath=moviePath, resolution=projectDict['resolution'])
    else:
        pblast = PlayBlaster(item=item, moviePath=moviePath, resolution=projectDict['resolution'])

    pblast.doPlayBlast()

# todo exportar camera (como??)

def doExportCam(*args):
    item = Item(fromScene=True)
    camera = CameraComponent(ns='cam', parent=item)
    exportPath = camera.getCameraPublishPath(make=True)

    sceneCam = pm.ls('cam:*', assemblies=True)
    pm.select(sceneCam)
    pm.exportSelected(exportPath)