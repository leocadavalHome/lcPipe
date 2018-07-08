import pymel.core as pm
import os.path
from lcPipe.core import database
reload (database)

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

