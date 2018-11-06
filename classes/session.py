import pymel.core as pm
import sys
import pymongo
import pymongo.errors
import logging
from lcPipe.classes.project import Project
from lcPipe.classes.task import Task

logger = logging.getLogger(__name__)


class Session(object):

    def __init__(self, user=None, password=None, projectName=None, databaseIP='localhost', databasePort=27017):

        client = self._connectToClient(databaseIP=databaseIP, databasePort=databasePort)
        self.db = client.lcPipeline
        self.user = self.authenticateUser(user, password)
        self.project = None
        self.currentProject = None
        self.setCurrentProject(projectName)

    def _connectToClient(self, databaseIP, databasePort):
        try:
            client = pymongo.MongoClient (databaseIP, databasePort, serverSelectionTimeoutMS=5000, socketTimeoutMS=5000)
            client.server_info()
            return client
        except pymongo.errors.ServerSelectionTimeoutError as err:
            resp = pm.confirmDialog(title='Error', message='No Database Connection Found!', button=['OK'], defaultButton='Ok',
                         dismissString='Ok')
            if resp == 'Ok':
                sys.exit()

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
            project = Project(projectName, prefix, **projectDict)
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
            logger.error('Cant read project data %s'% projectName)

    def updateProject(self, projectName, **projectDict):
        self.db.projects.find_one_and_update({'projectName': projectName}, {'$set': projectDict})

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

    #items
    def createTask(self, **taskDict):
        taskInstance = Task(projectName=self.currentProject, **taskDict)
        collection = self.db.get_collection(self.currentProject + '_' + taskInstance.itemType)
        exist = collection.find_one({'task': taskInstance.task, 'code': taskInstance.code})
        if not exist:
            collection.insert_one(taskInstance.__dict__)
        else:
            logger.error('task %s already exists' % taskInstance.code)

    def readTask(self, task=None, code=None):
        itemType = self.getTaskType(task)
        collection = self.db.get_collection(self.currentProject + '_' + itemType)
        taskDict = collection.find_one({'task': task, 'code': code})
        if taskDict:
            taskInstance = Task(**taskDict)
            return taskInstance
        else:
            logger.error('Cant find task')

    def updateTask(self, task=None, code=None, **taskDict):
        itemType = self.getTaskType(task)
        collection = self.db.get_collection(self.currentProject + '_' + itemType)
        collection.find_one_and_update({'task': task, 'code': code}, {'$set': taskDict})


    def deleteTask(self, task=None, code=None):
        itemType = self.getTaskType(task)
        collection = self.db.get_collection(self.currentProject + '_' + itemType)
        collection.delete_one({'task': task, 'code': code})


    def getTaskType(self,task):
        if task == 'asset' or task == 'shot':
            return task

        resultTasks = []
        for workflow in self.project.workflows.itervalues():
            for key, values in workflow.iteritems():
                if key == task:
                    resultTasks.append(values['type'])

        if resultTasks:
            return resultTasks[0]
        else:
            print 'ERROR getTaskType: no task type found!'
