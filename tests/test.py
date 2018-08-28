import pymel.core as pm
import logging
import os.path
import lcPipe.core.database as database
reload (database)
logger = logging.getLogger(__name__)
logger.setLevel(10)

import lcPipe.publish.playblaster as pb
reload(pb)
x = pb.PlayBlaster()


x.resolution=(1280, 720)
x.doPlayBlast()



projectDict = database.getDefaultDict()
database.updateCurrentProjectKey('workflow', projectDict['workflow'])

database.updateCurrentProjectKey('soundLocation', projectDict['soundLocation'])
database.updateCurrentProjectKey('fps', projectDict['fps'])