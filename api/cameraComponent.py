from lcPipe.api.component import Component
from lcPipe.core import database
import pymel.core as pm
import os.path

class CameraComponent(Component):
    def __init__(self, ns, componentMData, parent=None):
        super(CameraComponent, self).__init__(ns=ns, componentMData=componentMData, parent=parent)
        self.cameraTransform = None
        self.cameraShape = None

    def wrapData(self):
        cameras = pm.ls(type='camera', l=True)
        startup_cameras = [camera for camera in cameras if pm.camera(camera.parent (0), startupCamera=True, q=True)]
        cameraShape = list(set(cameras) - set(startup_cameras))
        if not cameraShape:
            return None

        camera = map(lambda x: x.parent(0), cameraShape)[0]
        self.cameraTransform = camera

    def addToScene(self):
        item = self.getItem()
        componentPath = item.getPublishPath()
        pm.namespace(add=':cam')
        pm.importFile(componentPath, ns='cam')
        self.wrapData()
        self.renameToScene()

    def renameToScene(self):
        print self.parent.getDataDict()
        cameraName = 'cam:'+self.parent.projPrefix + self.parent.code +'_' + self.parent.name+'_camera'
        if self.cameraTransform.name() != cameraName:
            pm.rename(self.cameraTransform, cameraName)

    def getCachePublishPath(self, make=False):
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