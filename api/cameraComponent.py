from lcPipe.api.component import Component
from lcPipe.core import database
import pymel.core as pm
import os.path
import logging
from lcPipe.api.item import Item

logger = logging.getLogger(__name__)
logger.setLevel(10)
"""
Wraper for a camera scene component
"""
class CameraComponent(Component):
    def __init__(self, ns, parent=None):
        """
        :param ns: str
        :param componentMData: dict
        :param parent: api.Item
        """
        cameraItem = Item(task='rig', code='0000', itemType='asset')

        if cameraItem.noData:
            pm.confirmDialog(title='No base camera', ma='center',
                             message='Please make an asset code:0000 as base camera',
                             button=['OK'], defaultButton='OK', dismissString='OK')
            return

        cameraMData = {'code': '0000', 'ver': cameraItem.publishVer, 'updateMode': 'last',
                      'task': 'rig', 'assembleMode': 'camera', 'proxyMode': 'rig',
                       'onSceneParent': None, 'type': 'asset', 'xform': {}}

        super(CameraComponent, self).__init__(ns=ns, componentMData=cameraMData, parent=parent)
        self.cameraTransform = None
        self.cameraShape = None
        self.wrapData()

        logger.debug('camera %s, shape %s' % (self.cameraTransform, self.cameraShape))

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
        self.cameraShape = cameraShape[0]

    @property
    def cameraAspect(self):
        return (self.cameraShape.horizontalFilmAperture.get() / self.cameraShape.verticalFilmAperture.get())

    @cameraAspect.setter
    def cameraAspect(self, value):
        logger.debug('setting camera aspect %s' % value)
        logger.debug(self.cameraShape.horizontalFilmAperture.get())
        logger.debug(self.cameraShape.verticalFilmAperture.get())
        self.cameraShape.horizontalFilmAperture.set(self.cameraShape.verticalFilmAperture.get() * value)

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
            self.cameraTransform = cameraName

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

    def getCameraPublishPath(self, make=False):
        """
        Return the path where to publish the alembic cache for this camera
        If make it true, create the folder if needed

        :param make: boolean
        :return: str
        """

        project = database.getProjectDict()

        location = project['publishLocation']
        filename = database.templateName(self.parent.getDataDict(), template=project['cameraNameTemplate'])

        folderPath = os.path.join(*self.parent.path)
        phase = project['workflow'][self.parent.workflow][self.parent.task]['phase']

        ext = '.ma'

        dirPath = os.path.join(location, phase, 'camera', folderPath)
        filename = filename + '_camera' + ext

        if make:
            if not os.path.exists(dirPath):
                os.makedirs(dirPath)

        logger.debug(dirPath)
        cameraDirList = pm.getFileList(folder=dirPath, filespec='*.ma')

        logger.debug(cameraDirList)
        maxVer = 0

        if cameraDirList:
            for cam in cameraDirList:
                ver = int(cam[1:4])
                maxVer = max(ver, maxVer)

        version = 'v%03d_' % (maxVer+1)
        logger.debug(version)
        camFilename = version+filename
        logger.debug(camFilename)
        return os.path.join(dirPath, camFilename)
