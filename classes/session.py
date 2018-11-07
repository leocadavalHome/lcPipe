import pymel.core as pm
import sys
import pymongo
import pymongo.errors
import logging
from lcPipe.classes.project import Project
from lcPipe.classes.connection import MongoDBConnection

logger = logging.getLogger(__name__)


class Session(object):
    def __init__(self, user=None, password=None, projectName=None, databaseIP='localhost', databasePort=27017):

        self.db = MongoDBConnection(databaseIP, databasePort).db
        self.user = self.authenticateUser(user, password)
        self.project = None
        self.currentProject = projectName
        self.setCurrentProject(self.currentProject)

    def _validate(self):
        valid = True
        if not self.user:
            valid = False

        allProjects = self.listProjects()
        if self.currentProject not in allProjects:
            valid = False

        if not valid:
            logger.error('Session not valid')
            sys.exit()

    #user
    def listUsers(self):
        result = self.db.users.find()
        return [x for x in result]

    def authenticateUser(self, user, password):
        if password:
            return user
        else:
            return None

    #Project
    def listProjects(self):
        result = self.db.projects.find()
        return [x['projectName'] for x in result]

    def createProject(self, projectName, prefix, **projectDict):
        try:
            project = Project(projectName=projectName, prefix=prefix, **projectDict)
            self.db.projects.insert_one(project.getProjectDict())

            for col in project.collections:
                self.db.create_collection(projectName + '_' + col)
        except:
            logger.error('Cant create project %s' % projectName)
            raise

    def readProject(self, projectName):
        projectDict = self.db.projects.find_one({'projectName': projectName})
        if projectDict:
            proj = Project(**projectDict)
            return proj
        else:
            logger.error('Cant read project data %s' % projectName)

    def updateProject(self, projectName, **projectDict):
         proj = self.db.projects.find_one_and_update({'projectName': projectName}, {'$set': projectDict})
         if not proj:
             logger.error('Project %s non existent' % projectName)

    def deleteProject(self, projectName):
        proj = self.readProject(projectName)
        self.db.projects.delete_one({'projectName': projectName})
        for col in proj.collections:
            self.db.drop_collection(projectName + '_' + col)

    def getCurrentProject(self):
        return self.currentProject

    def setCurrentProject(self, projectName):
        allProjects = self.listProjects()
        if projectName in allProjects:
            self.currentProject = projectName
            self.project = self.readProject(projectName)
        else:
            logger.error('Non existent project: %s' % projectName)


