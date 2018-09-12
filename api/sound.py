import pymel.core as pm
import os.path
import logging
logger = logging.getLogger(__name__)
logger.setLevel(10)


class Sound:
    def __init__(self, parent=None, soundPath=None):
        self.item = parent

        if not soundPath and parent:
            self.soundPath = self.getFromSoundDir()
        else:
            self.soundPath = soundPath

    def importOnScene(self):
        if self.soundPath:
            if pm.objExists(self.item.name+'Sound'):
                pm.delete(self.item.name+'Sound')

            pm.sound(name=self.item.name+'Sound', file=self.soundPath)
        else:
            logger.debug('No sound defined')

    def getFromSoundDir(self):
        soundDir, soundFile = self.item.getPath(dirLocation='soundLocation', ext='')
        soundList = pm.getFileList(soundDir)
        last = None
        maxValue = 0
        if soundList:
            for sound in soundList:
                version = int(os.path.splitext(sound)[0].split('_')[-1][1:])
                if maxValue < version:
                    last = sound
                    maxValue = version

            return os.path.join(soundDir, last)