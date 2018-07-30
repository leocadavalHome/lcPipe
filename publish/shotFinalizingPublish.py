#todo Merge anim layers.
#todo Bake all constrains.
#todo All characters n props CTRL must be baked.
#todo Export the cameras.
#todo Scene caching.
#todo Batch caching process.
#todo Playblast and Publish.

import pymel.core as pm
import lcPipe.core.cache as cache


def cacheAnimation(*args):
    try:
        cache.cacheScene(task=pm.fileInfo['task'], code=pm.fileInfo['code'])
        return False
    except:
        raise

def cacheCameraAnimation(*args):
    try:
        pm.confirmDialog(title='camera Cache', ma='center', icon='information', message='Camera Cache', button=['OK'],
                         defaultButton='OK', dismissString='ok')
        cache.cacheCamera(task=pm.fileInfo['task'], code=pm.fileInfo['code'])
    except:
        raise