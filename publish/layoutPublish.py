import pymel.core as pm
import os.path
import logging
import lcPipe.core.database as database
import lcPipe.core.check as check
from lcPipe.api.item import Item
from lcPipe.publish.playblaster import PlayBlaster

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
    pm.currentUnit(time=projectDict['fps'], ua=False)
    return 'ok'


def fixFpsChangeKey(*args):
    projectDict = database.getProjectDict()
    pm.currentUnit(time=projectDict['fps'], ua=True)
    return 'ok'

def cameraAspectCheck(*args):
    item = Item(fromScene=True)
    try:
        camera = pm.PyNode('cam:'+item.projPrefix + item.code + '_' + item.name + '_camera')
    except RuntimeError:
        logger.warn('no camera found')
        return True
    projectDict = database.getProjectDict()

    width, height = projectDict['resolution']

    projectAspect = float(width)/float(height)
    cameraAspect = camera.horizontalFilmAperture / camera.verticalFilmAperture

    if abs(projectAspect-cameraAspect) > 0.01:
        return True

def fixCameraAspect(*args):
    item = Item(fromScene=True)
    try:
        camera = pm.PyNode('cam:'+item.projPrefix + item.code + '_' + item.name + '_camera')
    except RuntimeError:
        logger.warn('no camera found')
        return True
    projectDict = database.getProjectDict()

    width, height = projectDict['resolution']
    projectAspect = float (width) / float (height)

    camera.horizontalFilmAperture = camera.verticalFilmAperture * projectAspect


def cameraNameCheck (*args):
    cameras = pm.ls(type='camera', l=True, r=True)
    startup_cameras = [camera for camera in cameras if pm.camera (camera.parent (0), startupCamera=True, q=True)]
    cameraShape = list(set(cameras) - set (startup_cameras))
    if not cameraShape:
        return True
    camera = map(lambda x: x.parent (0), cameraShape)[0]

    item = Item(fromScene=True)
    correctCameraName = 'cam:'+item.projPrefix + item.code + '_' + item.name + '_camera'
    if camera != correctCameraName:
        return True


def renameCamera(*args):
    cameras = pm.ls(type='camera', l=True, r=True)
    startup_cameras = [camera for camera in cameras if pm.camera (camera.parent (0), startupCamera=True, q=True)]
    cameraShape = list(set(cameras) - set(startup_cameras))
    if not cameraShape:
        return None
    camera = map(lambda x: x.parent(0), cameraShape)[0]

    item = Item(fromScene=True)
    correctCameraName = 'cam:' + item.projPrefix + item.code + '_' + item.name + '_camera'
    pm.rename(camera, correctCameraName)
    return 'ok'

def NoReferenceOff(*args):

    allReferences = pm.getReferences()

    for ref in allReferences:
        if not ref.isLoaded():
            return True

def removeUnloadedRefs (*args):
    allReferences = pm.getReferences()

    for ref in allReferences:
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

    moviePath = os.path.join(r'D:\JOBS\PIPELINE\pipeExemple\movies', item.fileName+'Preview.mov') # todo remove this hard code

    if sound:
        pblast = PlayBlaster(item=item, sound=sound[0], moviePath=moviePath, resolution=projectDict['resolution'])
    else:
        pblast = PlayBlaster(item=item, moviePath=moviePath)

    pblast.doPlayBlast()

