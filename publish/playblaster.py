import pymel.core as pm
import os.path
import logging
logger = logging.getLogger(__name__)
logger.setLevel(10)

class PlayBlaster:

    def __init__(self, item=None, sound=None, moviePath=None, resolution=None):
        self.item = item
        self.moviePath = moviePath
        self.sound = sound
        self._camera = None
        self._modelPanel = None
        self.percent = 100
        self.resolution = resolution
        self.quality = 100
        self._camOptions = []
        self._hudOptions = []

    def doPlayBlast(self):
        pm.setFocus(self._modelPanel)
        self.getCamera()
        self.saveCameraOptions()
        self.setViewOptions()
        self.saveHUDStatus()
        self.setupHUD()

        if self.sound:
            pm.playblast(f=self.moviePath, sound=self.sound, fmt='qt', v=True, fo=True, p=self.percent, quality=self.quality,
                         editorPanelName=self._modelPanel, offScreen=True, w=self.resolution[0], h=self.resolution[1])
        else:
            pm.playblast(f=self.moviePath, fmt='qt', v=True, fo=True, p=self.percent, quality=self.quality,
                         editorPanelName=self._modelPanel, offScreen=True, w=self.resolution[0], h=self.resolution[1])

        self.restoreCameraOptions()
        self.restoreHUDStatus()
        pm.deleteUI(self._modelPanel+'Window')

    def getCamera(self):
        cameras = pm.ls(type='camera', l=True)
        startup_cameras = [camera for camera in cameras if pm.camera(camera.parent(0), startupCamera=True, q=True)]
        cameraShape = list(set(cameras) - set(startup_cameras))
        if not cameraShape:
            return None

        camera = map(lambda x: x.parent(0), cameraShape)[0]
        self._camera = camera

    def setViewOptions(self):
        self._modelPanel = pm.modelPanel(label='playBlaster', to=True, menuBarVisible=False, cam=self._camera)
        modelEditor = pm.modelPanel(self._modelPanel, q=True, me=True)
        pm.window (self._modelPanel + 'Window', e=True, w=self.resolution[0] / 2, h=self.resolution[1] / 2)
        pm.modelEditor(modelEditor, e=True, allObjects=True, polymeshes=True, nurbsSurfaces=True,
                       subdivSurfaces=True, grid=True, nurbsCurves=False, displayAppearance='smoothShaded',
                       displayTextures=False, hud=True, imagePlane=True, rendererName='Viewport 2')


    def saveCameraOptions(self):
        self._camOptions.append(self._camera.overscan.get())
        self._camOptions.append(self._camera.filmFit.get())
        self._camOptions.append(self._camera.displayFieldChart.get())
        self._camOptions.append(self._camera.displaySafeAction.get())
        self._camOptions.append(self._camera.displayFilmOrigin.get())
        self._camOptions.append(self._camera.displayFilmPivot.get())
        self._camOptions.append (self._camera.getShape().displayGateMask.get())
        self._camOptions.append (self._camera.getShape().displayResolution.get())
        self._camOptions.append (self._camera.getShape().displayFilmGate.get())

        self._camera.overscan.set(1)
        self._camera.filmFit.set(3)
        self._camera.displayFieldChart.set(0)
        self._camera.displaySafeAction.set(0)
        self._camera.displaySafeTitle.set(0)
        self._camera.displayFilmOrigin.set(0)
        self._camera.displayFilmPivot.set(0)

        self._camera.getShape().displayGateMask.set(0)
        self._camera.getShape().displayResolution.set(0)
        self._camera.getShape().displayFilmGate.set(0)

    def restoreCameraOptions(self):
        self._camera.overscan.set(self._camOptions[0])
        self._camera.filmFit.set(self._camOptions[1])
        self._camera.displayFieldChart.set(self._camOptions[2])
        self._camera.displaySafeAction.set(self._camOptions[3])
        self._camera.displayFilmOrigin.set(self._camOptions[4])
        self._camera.displayFilmPivot.set(self._camOptions[5])
        self._camera.getShape().displayGateMask.set(self._camOptions[6])
        self._camera.getShape().displayResolution.set(self._camOptions[7])
        self._camera.getShape().displayFilmGate.set(self._camOptions[8])

    def setupHUD(self):
        # todo restore huds after playblast
        logger.debug ('sceneName')

        if not (pm.headsUpDisplay ('HUDSceneName', q=True, exists=True)):
            self.freeHUDblock (0,0)
            pm.headsUpDisplay('HUDSceneName', vis=True, section=0, block=0, blockSize='small',
                               dataFontSize='large', command=self.getSceneName, event='RecentCommandChanged')
        else:
            self.freeHUDblock (0, 0)
            pm.headsUpDisplay ('HUDSceneName', e=True,section=0, block=0, vis=True)

        if not (pm.headsUpDisplay ('HUDUserName', q=True, exists=True)):
            self.freeHUDblock(4, 0)
            pm.headsUpDisplay ('HUDUserName', vis=True, section=4, block=0, blockSize='small', dataFontSize='large',
                               command=self.getUserName, event='RecentCommandChanged')
        else:
            self.freeHUDblock (4, 0)
            pm.headsUpDisplay('HUDUserName', e=True,section=4, block=0, vis=True)

        logger.debug ('cameraName')
        self.freeHUDblock (2, 0)
        pm.headsUpDisplay ('HUDCameraNames', e=True, vis=True, section=2, block=0, blockSize='small',
                           labelFontSize='large', dataFontSize='large')

        logger.debug ('focal')
        self.freeHUDblock (7, 0)
        pm.headsUpDisplay ('HUDFocalLength', e=True, label='', vis=True, section=7, block=0,
                           labelFontSize='large', lw=90, blockSize='small', dataFontSize='large')

        logger.debug ('currentFrame')
        self.freeHUDblock (9, 0)
        pm.headsUpDisplay ('HUDCurrentFrame', e=True, vis=True, dataAlignment='right',
                           label='', section=9, block=0,
                           labelFontSize='large', blockSize='small', dataFontSize='large')

        logger.debug ('timecode')
        self.freeHUDblock (5, 0)
        pm.headsUpDisplay ('HUDSceneTimecode', e=True, label='', lw=0, vis=True, labelFontSize='large', section=5,
                           block=0, blockSize='small', dataFontSize='large')

    def getSceneName(self):
        return os.path.basename(pm.sceneName())

    def getUserName(self):
        return 'user'

    def freeHUDblock(self, sec, blk):
        hudList = pm.headsUpDisplay(listHeadsUpDisplays=True)
        sel = [x for x in hudList if
               pm.headsUpDisplay (x, q=True, section=True) == sec and pm.headsUpDisplay (x, q=True, block=True) == blk]
        if sel:
            nextBlock = pm.headsUpDisplay (nfb=sec)
            pm.headsUpDisplay (sel[0], e=True, vis=False, section=sec, block=nextBlock)
            return sel[0]
        return

    def saveHUDStatus(self):
        hudList = pm.headsUpDisplay(listHeadsUpDisplays=True)
        self._hudOptions = [(x, pm.headsUpDisplay(x, q=True, section=True), pm.headsUpDisplay (x, q=True, block=True))
                       for x in hudList if pm.headsUpDisplay(x, q=True, vis=True)]

        for hud, sec, blk in self._hudOptions:
            pm.headsUpDisplay(hud, e=True, vis=False)

    def restoreHUDStatus (self):
        pm.headsUpDisplay('HUDSceneTimecode', e=True, vis=False)
        pm.headsUpDisplay('HUDCurrentFrame', e=True, vis=False)
        pm.headsUpDisplay('HUDFocalLength', e=True, vis=False)
        pm.headsUpDisplay('HUDCameraNames', e=True, vis=False)
        pm.headsUpDisplay('HUDUserName', e=True, vis=False)
        pm.headsUpDisplay('HUDSceneName', e=True, vis=False)

        for hud, sec, blk in self._hudOptions:
            self.freeHUDblock(sec=sec, blk=blk)
            pm.headsUpDisplay(hud, e=True, section=sec, block=blk, vis=True)