from lcPipe.api.component import Component
from lcPipe.core import database
import pymel.core as pm
import os.path
import logging
logger = logging.getLogger(__name__)
"""
Wraper for a camera scene component
"""
class CameraComponent(Component):
    def __init__(self, ns, componentMData, parent=None):
        """
        :param ns: str
        :param componentMData: dict
        :param parent: api.Item
        """
        super(CameraComponent, self).__init__(ns=ns, componentMData=componentMData, parent=parent)
        self.cameraTransform = None
        self.cameraShape = None

    def wrapData(self):
        """
        Get the camera name from the scene
        :return:
        """
        cameras = pm.ls(type='camera', l=True)
        startup_cameras = [camera for camera in cameras if pm.camera(camera.parent (0), startupCamera=True, q=True)]
        cameraShape = list(set(cameras) - set(startup_cameras))
        if not cameraShape:
            return None

        camera = map(lambda x: x.parent(0), cameraShape)[0]
        self.cameraTransform = camera

    def addToScene(self):
        """
        Import the camera to the scene
        :return:
        """
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.namespace(add=':cam')
        pm.importFile(componentPath, ns='cam')
        self.wrapData()
        self.renameToScene()

    def renameToScene(self):
        """
        Rename the camera after the scene name
        :return:
        """
        cameraName = 'cam:'+self.parent.projPrefix + self.parent.code +'_' + self.parent.name+'_camera'
        if self.cameraTransform.name() != cameraName:
            pm.rename(self.cameraTransform, cameraName)

    def getCachePublishPath(self, make=False):
        """
        Return the path where to publish the alembic cache for this camera
        If make it true, create the folder if needed

        :param make: boolean
        :return: str
        """
        proj = database.getProjectDict()
        path = self.parent.getPath(dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)

        if make:
            if not os.path.exists(cachePath):
                os.makedirs(cachePath)

        ver = 'v%03d_' % self.parent.caches['cam']['cacheVer']
        cacheName = database.templateName(self.getDataDict(), proj['cacheNameTemplate']) + '_' + self.ns
        cacheFileName = ver + cacheName + '.abc'

        return os.path.join(cachePath, cacheFileName)