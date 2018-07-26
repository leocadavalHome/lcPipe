import pymel.core as pm
import os.path
from core import database

def open (type, task, code):
    collection = database.getCollection ( type )
    item = collection.find_one ( {'task': task, 'code': code} )

    if not item:
        print 'ERROR: No metadata for this item'
        return

    ## get path
    path = database.getPath ( item )
    sceneFullPath = os.path.join ( *path )

    pm.openFile ( sceneFullPath, f=True )


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

