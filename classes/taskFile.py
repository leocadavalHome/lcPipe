import copy
from lcPipe.classes.componentFile import ComponentFile
import pymel.core as pm
import logging

logger = logging.getLogger(__name__)

class TaskFile (object):

    def __init__(self):
        self.sourceTask = None
        self.path = None
        self.filename = None
        self.isOpen = None

    def _validade(self):
        pass

    def saveAs(self):
        pass

    def open(self):
        pass

    def publish(self):
        pass

    #components
    def listFileComponents(self):
        pass

    def getFileComponent(self):
        pass

    def addFileComponent(self):
        pass

    def deleteFileComponent(self):
        pass

    def updateFileComponent(self):
        pass

    def checkComponents(self):
        pass