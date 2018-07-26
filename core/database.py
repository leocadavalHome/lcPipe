# DATABASES
import pymel.core as pm
import os.path
import os
import pymongo
import sys

# The global variable for database acess
db = None
currentProject = None


# basic connection
def mongoConnect():
    global db
    try:
        client = pymongo.MongoClient('localhost', 27017, serverSelectionTimeoutMS=5000, socketTimeoutMS=5000)
        db = client.lcPipeline

    except:
        resp = pm.confirmDialog(title='Error', message='No Database Connection Found!', button=['OK'], defaultButton='Ok',
                         dismissString='Ok')
        if resp == 'Ok':
            sys.exit()
    # return db


##Projects
def getDefaultDict():
    projDict = {'projectName': '', 'prefix': '', 'workLocation': u'D:/JOBS/PIPELINE/pipeExemple/scenes',
                'publishLocation': u'D:/JOBS/PIPELINE/pipeExemple/publishes',
                'imagesWorkLocation': u'D:/JOBS/PIPELINE/pipeExemple/sourceimages',
                'imagesPublishLocation': u'D:/JOBS/PIPELINE/pipeExemple/publishes/sourceimages',
                'cacheLocation': u'D:/JOBS/PIPELINE/pipeExemple/cache/alembic',
                'assetCollection': '_asset',
                'shotCollection': '_shot', 'status': 'active',
                'assetFolders': {'character': {'parent': ''},
                                 'props': {'parent': ''},
                                 'sets': {'parent': ''},
                                 'primary': {'parent': 'character'}},
                'shotFolders': {'ep001': {'parent': ''},
                                'ep002': {'parent': ''},
                                'ep003': {'parent': ''},
                                'seq0001': {'parent': 'ep001'}},
                'assetNameTemplate': ['$prefix', '$code', '_', '$name', '_', '$task'],
                'cacheNameTemplate': ['$prefix', '$code', '$task'],
                'nextAsset': 1,
                'nextShot': 1,
                'renderer': 'vray',
                'fps': 24,
                'resolution': [1920, 1080],
                'workflow': {
                                'rig': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                                  'source': []},
                                        'uvs': {'type': 'asset', 'phase': 'preProd', 'short': 'uvs',
                                                'source': [('model', 'import')]},
                                        'blendShape': {'type': 'asset', 'phase': 'preProd', 'short': 'bsp',
                                                       'source': [('model', 'import')]},
                                        'texture': {'type': 'asset', 'phase': 'preProd', 'short': 'tex',
                                                    'source': [('uvs', 'reference')]},
                                        'xlo': {'type': 'asset', 'phase': 'preProd', 'short': 'xlo',
                                                'source': [('texture', 'import')]},
                                        'rig': {'type': 'asset', 'phase': 'preProd', 'short': 'rig',
                                                'source': [('uvs', 'reference'),('blendShape', 'import')]}},

                                'static': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                                     'source': []},
                                           'uvs': {'type': 'asset', 'phase': 'preProd', 'short': 'uvs',
                                                   'source': [('model', 'import')]},
                                           'texture': {'type': 'asset', 'phase': 'preProd', 'short': 'tex',
                                                       'source': [('uvs', 'reference')]}},
                                'camera': {'model': {'type': 'asset', 'phase': 'preProd', 'short': 'mod',
                                                     'source': []},
                                           'rig': {'type': 'asset', 'phase': 'preProd', 'short': 'rig', 'source': []}},

                                'shotCache': {'layout': {'type': 'shot', 'phase': 'prod', 'short': 'lay','source': [],
                                                         'components': {'cam': {'code': '9999', 'ver': 1,
                                                                        'updateMode': 'last', 'task': 'rig',
                                                                        'assembleMode': 'reference',
                                                                        'type': 'asset'}}},
                                             'animation': {'type': 'shot', 'phase': 'prod', 'short': 'ani',
                                                           'source': [('layout', 'copy')]},
                                             'render': {'type': 'shot', 'phase': 'postProd', 'short': 'rnd',
                                                        'source': [('shotFinalizing', 'cache')]},
                                             'shotFinalizing': {'type': 'shot', 'phase': 'prod', 'short': 'sfh',
                                                                'source': [('animation', 'copy')]}},

                                'shotXlo': {'layout': {'type': 'shot', 'phase': 'prod', 'short': 'lay', 'source': [],
                                                       'components': { 'cam': {'code': '9999', 'ver': 1, 'updateMode': 'last',
                                                                       'task': 'rig', 'assembleMode': 'reference',
                                                                       'type': 'asset'}}},
                                            'animation': {'type': 'shot', 'phase': 'prod', 'short': 'ani',
                                                          'source': [('layout', 'copy')]},
                                            'render': {'type': 'shot', 'phase': 'postProd', 'short': 'rnd',
                                                       'source': [('shotFinalizing', 'xlo')]},
                                            'shotFinalizing': {'type': 'shot', 'phase': 'prod', 'short': 'sfh',
                                                               'source': [('animation', 'copy')]}},

                                'keyLightShot': {'layout': {'type': 'shot', 'phase': 'prod', 'short': 'lay',
                                                            'source': [],
                                                            'components': [{'code': '9999', 'ver': 1,
                                                                            'updateMode': 'last', 'task': 'rig',
                                                                            'assembleMode': 'reference',
                                                                            'type': 'asset'}]},
                                                 'animation': {'type': 'shot', 'phase': 'prod', 'short': 'ani',
                                                               'source': [('layout', 'copy')]},
                                                 'lighting': {'type': 'shot', 'phase': 'postProd', 'short': 'lit',
                                                              'source': [('shotFinalizing', 'reference')]},
                                                 'render': {'type': 'shot', 'phase': 'postProd', 'short': 'rnd',
                                                            'source': [('shotFinalizing', 'cache')]},
                                                 'shotFinalizing': {'type': 'shot', 'phase': 'prod', 'short': 'sfh',
                                                                    'source': [('animation', 'copy')]}}}
                }
    return projDict


def addProject(**projectSettings):
    global db
    projDict = getDefaultDict()
    projDict.update(projectSettings)
    db.create_collection(projectSettings['projectName'] + '_asset')
    db.create_collection(projectSettings['projectName'] + '_shot')
    db.projects.insert_one(projDict)


def getCurrentProject():
    global currentProject
    return currentProject


def setCurrentProject(project):
    global currentProject
    currentProject = project


def editProject(projectName, **projectSettings):
    global db
    projDict = getDefaultDict()
    projDict.update(projectSettings)
    db.projects.find_one_and_update({'projectName': projectName}, {'$set': projDict})


def getProjectDict(projectName=None):
    global db
    global currentProject
    if projectName:
        returnProject = db.projects.find_one({'projectName': projectName})
    elif currentProject:
        returnProject = db.projects.find_one({'projectName': currentProject})
    else:
        returnProject = db.projects.find_one()
    return returnProject


def putProjectDict(projDict, projectName=None):
    global db
    global currentProject
    if projectName:
        projName = projectName
    else:
        projName = currentProject

    db.projects.find_one_and_update({'projectName': projName}, {'$set': projDict})


def getAllProjects():
    global db
    return db.projects.find()


def getCollection(itemType, projectName=None):
    global db
    global currentProject
    if projectName:
        collection = db.get_collection(projectName + '_' + itemType)
    else:
        collection = db.get_collection(currentProject + '_' + itemType)

    return collection


##DATABASE
def getItemMData(projName=None, task=None, code=None, itemType=None, fromScene=False):
    if fromScene:
        print 'fromScene'
        projName = pm.fileInfo.get('projectName')
        task = pm.fileInfo.get('task')
        code = pm.fileInfo.get('code')
        itemType = pm.fileInfo.get('type')

        if not projName or not task or not code or not itemType:
            print 'ERROR getItemData: Cant get item Metadata. Scene has incomplete fileInfo:', projName, task, code, itemType
    else:
        if not task or not code:
            print 'ERROR getItemData: Cant get item Metadata. Missing item ids on function call:', projName, task, code, itemType

        if not itemType:
            itemType = getTaskType(task)
            print 'WARNING getItemData: getting type from task', task, itemType

    if projName:
        collection = getCollection(itemType, projName)
    else:
        collection = getCollection(itemType)

    item = collection.find_one({'task': task, 'code': code})

    if not item:
        print 'ERROR getItemData: Cant find item Metadata on database:', projName, task, code, itemType

    return item


def putItemMData(itemMData, projName=None, task=None, code=None, itemType=None, fromScene=True):
    if not itemMData:
        print 'ERROR putItemData: no item metadata in function call:'

    if fromScene:
        projName = pm.fileInfo.get('projectName')
        task = pm.fileInfo.get('task')
        code = pm.fileInfo.get('code')
        itemType = pm.fileInfo.get('type')

        if not projName or not task or not code or not itemType:
            print 'ERROR putItemData: Cant put item Metadata. Scene has incomplete fileInfo:', projName, task, code, itemType
            return
    else:
        if not task or not code:
            print 'ERROR putItemData: Cant get item Metadata. Missing item ids on function call:', projName, task, code, itemType

        if not itemType:
            itemType = getTaskType(task)
            print 'WARNING putItemData: getting type from task', task, itemType

    collection = getCollection(itemType, projectName=projName)
    itemOut = collection.find_one_and_update({'task': task, 'code': code}, {'$set': itemMData})


# NAMEPROCESS
def templateName(item, template=None):
    proj = getProjectDict()
    itemNameTemplate = None

    if template:
        itemNameTemplate = template
    else:
        type = item['type']

        if type == 'asset' or type == 'shot':
            itemNameTemplate = proj['assetNameTemplate']
        elif type == 'cache':
            itemNameTemplate = proj['cacheNameTemplate']

    taskShort = getTaskShort(item['task'])

    code = item['code']
    if 'name' in item:
        name = item['name']
    else:
        name = ''
    prefix = proj['prefix']

    fileNameList = itemNameTemplate
    fileNameList = [taskShort if x == '$task' else x for x in fileNameList]
    fileNameList = [code if x == '$code' else x for x in fileNameList]
    fileNameList = [name if x == '$name' else x for x in fileNameList]
    fileNameList = [prefix if x == '$prefix' else x for x in fileNameList]

    fileName = ''.join(fileNameList)

    return fileName


def untemplateName(source, template=None):
    proj = getProjectDict()

    if template:
        itemNameTemplate = template
    else:
        sourceExt = os.path.splitext(source)[1]

        if sourceExt == 'abc' or sourceExt == '.abc':
            itemNameTemplate = proj['cacheNameTemplate']
        else:
            itemNameTemplate = proj['assetNameTemplate']

    sourceName = os.path.splitext(source)[0]

    if '$name' in itemNameTemplate:
        nameId = itemNameTemplate.index('$name')
        templateStart = itemNameTemplate[:nameId]
        templateEnd = itemNameTemplate[nameId + 1:]
    else:
        templateStart = itemNameTemplate
        templateEnd = None

    separators = {}
    prefix = None
    task = None
    code = None

    for p in itemNameTemplate:
        if (p != '$prefix') and (p != '$code') and (p != '$task') and (p != '$name'):
            separators[p] = len(p)

    pos = 0

    for i, val in enumerate(templateStart):
        if val == '$prefix':
            prefix = sourceName[pos:pos + 2]
            pos = pos + 2
        elif val == '$code':
            code = sourceName[pos:pos + 4]
            pos = pos + 4
        elif val == '$task':
            task = sourceName[pos:pos + 3]
            pos = pos + 3
        else:
            pos = pos + separators[val]

    posStart = pos
    pos = len(sourceName)

    if templateEnd:
        for i, val in enumerate(reversed(templateEnd)):
            if val == '$prefix':
                prefix = sourceName[pos - 2:pos]
                pos = pos - 2
            elif val == '$code':
                code = sourceName[pos - 4:pos]
                pos = pos - 4
            elif val == '$task':
                task = sourceName[pos - 3:pos]
                pos = pos - 3
            else:
                pos = pos - separators[val]

    posEnd = pos
    name = sourceName[posStart:posEnd]

    return prefix, task, code, name


# CREATE ASSET!!
def incrementNextCode(itemType, fromBegining=False):
    global db
    global currentProject

    proj = getProjectDict()
    collection = getCollection(itemType)

    flag = True

    if fromBegining:
        nextCode = 1
    else:
        nextCode = int(proj['next' + itemType.capitalize()])

    count = 0

    while flag:
        nextCode += 1
        count += 1
        search = "%04d" % nextCode
        result = collection.find({'code': search})
        codeExists = [x for x in result]

        if not codeExists:
            flag = False
        if count == 150:
            flag = False

    db.projects.find_one_and_update({'projectName': currentProject},
                                    {'$set': {'next' + itemType.capitalize(): nextCode}})

def codeCheck(code, itemType):
    proj = getProjectDict()
    if code:
        code = "%04d" % int(code)
        nextItem = False
        collection = getCollection(itemType)
        result = collection.find({'code': code})
        codeExists = [x for x in result]

        if codeExists:
            return ['codeExists']

        else:
            nextCode = "%04d" % proj['next' + itemType.capitalize()]
            if code == nextCode:
                nextItem = True
    else:
        nextItem = True
        code = "%04d" % proj['next' + itemType.capitalize()]

    print code, nextItem
    return code, nextItem


def createItem(itemType, name, path, workflow, code=None):
    global db
    global currentProject

    codeTest = codeCheck(code, itemType)
    if codeTest[0] == 'codeExists':
        return 'codeExists'

    validatedCode = codeTest[0]

    proj = getProjectDict()
    collection = getCollection(itemType)
    itemWorkflow = proj['workflow'][workflow]
    itemsDict = {}

    for task in itemWorkflow.iterkeys():
        itemsDict[task] = {'name': name, 'code': validatedCode, 'task': task, 'type': itemType, 'workflow': workflow,
                           'projPrefix': proj['prefix'], 'workVer': 0, 'publishVer': 0, 'path': path, 'filename': '',
                           'status': 'notCreated', 'source': {}, 'components': {}}

        fileName = templateName(itemsDict[task])
        itemsDict[task]['filename'] = fileName

    for task, value in itemWorkflow.iteritems():
        for sourceTask in value['source']:
            itemsDict[task]['source'][sourceTask[0]] = {'code': validatedCode, 'ver': 1,
                                                           'updateMode': 'last', 'task': sourceTask[0],
                                                           'assembleMode': sourceTask[1],
                                                           'type': itemType}
        if 'components' in value.keys():
            itemsDict[task]['components'] = value['components']

    itemList = [x for x in itemsDict.itervalues()]
    collection.insert_many(itemList)
    incrementNextCode(itemType, fromBegining=not codeTest[1])

    return itemsDict


def removeItem(itemType, code):
    print 'remove item'
    collection = getCollection(itemType)
    collection.delete_many({'code': code})


# Items
def addComponent(item, ns, componentTask, componentCode, assembleMode, update=True):
    itemType = getTaskType(componentTask)
    compCollection = getCollection(itemType)

    componentMData = compCollection.find_one({'task': componentTask, 'code': componentCode})  # hardcode so assets
    componentDict = {'code': componentCode, 'ver': 1, 'updateMode': 'last', 'task': componentTask,
                     'assembleMode': assembleMode, 'type': componentMData['type']}

    nsList = item['components'].keys()
    index = 1
    nsBase = ns

    while ns in nsList:
        ns = nsBase + str(index)
        index += 1

    item['components'][ns] = componentDict

    if update:
        itemCollection = getCollection(item['type'])
        result = itemCollection.find_one_and_update({'task': item['task'], 'code': item['code']}, {'$set': item})

    return item


def removeComponent(item, ns):
    del item['components'][ns]
    collection = getCollection(item['type'])
    collection.find_one_and_update({'task': item['task'], 'code': item['code']}, {'$set': item})


# ASSEMBLE
def find(code, task, collection):  # old!!
    item = collection.find_one({'task': task, 'code': code})

    if item:
        return item
    else:
        print 'FIND: item not found'
        return


def getTaskType(task):
    proj = getProjectDict()

    if task == 'asset' or task == 'shot':
        return task

    resultTasks = []

    for workflow in proj['workflow'].itervalues():
        for key, values in workflow.iteritems():
            if key == task:
                resultTasks.append(values['type'])

    if resultTasks:
        return resultTasks[0]
    else:
        print 'ERROR getTaskType: no task type found!'


def getTaskLong(taskShort):
    project = getProjectDict()

    result = []
    for workflow in project['workflow'].itervalues():
        for key, value in workflow.iteritems():
            if value['short'] == taskShort:
                result.append(key)
    if result:
        return result[0]
    else:
        print 'ERROR getTaskLong: no long name for this task short!'


def getTaskShort(taskLong):
    project = getProjectDict()

    result = []
    for workflow in project['workflow'].itervalues():
        for key, values in workflow.iteritems():
            if key == taskLong:
                result.append(values['short'])
    if result:
        return result[0]
    else:
        print 'ERROR getTaskShort: no short name for this task!'


def getGeoGroupMembers(geoGroup):
    geosShape = geoGroup.getChildren(allDescendents=True, type='geometryShape')
    geos = [x.getParent() for x in geosShape]
    return geos


def getCamera():
    cameras = pm.ls(type='camera', l=True)
    startup_cameras = [camera for camera in cameras if pm.camera(camera.parent(0), startupCamera=True, q=True)]
    cameraShape = list(set(cameras) - set(startup_cameras))
    camera = map(lambda x: x.parent(0), cameraShape)[0]
    return camera


def getConnectedAlembic(ref):
    if pm.objExists(ref.namespace + ':geo_group'):
        geoGrp = pm.PyNode(ref.namespace + ':geo_group')
        geos = getGeoGroupMembers(geoGrp)
    else:
        geos = [getCamera()]

    alembicList = pm.ls(type='AlembicNode')
    if not alembicList:
        print 'there is no cache assigned'
        return

    for alembic in alembicList:
            alembicConnections = alembic.connections(s=False, type='transform')
            for x in alembicConnections:
                if x in geos:
                    return alembic
    return


def referenceInfo(refFile):
    fileName = os.path.basename(refFile.path).split('_', 1)
    ver = int(fileName[0][1:])

    info = untemplateName(fileName[1])
    task = getTaskLong(info[1])
    code = info[2]

    alembic = getConnectedAlembic(refFile)
    if alembic:
        alembicFileName = alembic.getAttr('abc_File')
        alembicBaseName = os.path.basename(alembicFileName).split('_', 1)
        cacheVer = int(alembicBaseName[0][1:])
    else:
        cacheVer = 0

    return {'ver': ver, 'task': task, 'code': code, 'cacheVer': cacheVer}


def getPath(item, dirLocation='workLocation', ext='ma'):
    project = getProjectDict()
    location = project[dirLocation]
    taskFolder = item['task']
    folderPath = os.path.join(*item['path'])
    phase = project['workflow'][item['workflow']][item['task']]['phase']
    filename = item['filename']

    if ext:
        ext = '.' + ext

    else:
        ext = ''

    dirPath = os.path.join(location, phase, taskFolder, folderPath)
    filename = filename + ext

    return dirPath, filename


def getSceneImagesPath(dirLocation='imagesWorkLocation'):
    project = getProjectDict()
    location = project[dirLocation]
    itemMData = getItemMData(task=pm.fileInfo['task'], code=pm.fileInfo['code'], itemType=pm.fileInfo['type'])
    folderPath = os.path.join(*itemMData['path'])
    filename = itemMData['filename']
    dirPath = os.path.join(location,folderPath,filename)

    return dirPath

