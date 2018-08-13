import json
import pymel.core as pm
import json
from pprint import pprint
import os.path
import lcPipe.core.database as database
from lcPipe.api.item import Item
from lcPipe.api.component import Component
import shutil
import re
import os
import logging

logger = logging.getLogger(__name__)

def readFbRole(FbRole, level, maxDepth=0, searchInGroupAsset=True):
    assetType = FbRole['componentData']['assetType']
    assetCode = FbRole['componentData']['assetCode']
    assetInstanceNumber = FbRole['componentData']['instanceNumber']

    if assetType == 'set_piece':
        modelAssetTask = FbRole['components'][0]['componentData']['task']
        controlXform1 = FbRole['components'][1]['componentData']['inner_ctl_data']
        controlXform2 = FbRole['components'][1]['componentData']['mid_ctl_data']
        controlXform3 = FbRole['components'][1]['componentData']['outer_ctl_data']

        return {'name': assetCode, 'instanceNumber': assetInstanceNumber, 'subType': 'set_piece', 'task': modelAssetTask,
                'xform': {'innerControl': controlXform1, 'midControl': controlXform2, 'outerControl': controlXform3},
                'components': []}

    elif assetType == 'group':
        groupAssetTask = FbRole['components'][0]['componentData']['task']
        groupAssetPath = FbRole['components'][0]['componentData']['sourcePath']
        controlXform1 = FbRole['components'][1]['componentData']['inner_ctl_data']
        controlXform2 = FbRole['components'][1]['componentData']['mid_ctl_data']
        controlXform3 = FbRole['components'][1]['componentData']['outer_ctl_data']

        if searchInGroupAsset and (maxDepth == 0 or level < maxDepth):
            jsonContent = readGroupAsset(groupAssetPath, level=level+1, maxDepth=maxDepth)
        else:
            jsonContent = {}

        return {'name': assetCode, 'instanceNumber': assetInstanceNumber, 'subType': 'group', 'task': groupAssetTask,
                'sourcePath': groupAssetPath,
                'xform': {'innerControl': controlXform1, 'midControl': controlXform2, 'outerControl': controlXform3},
                'components': jsonContent}


def readGroup (group, level, maxDepth=0, searchInGroupAsset=True):
    assetlabel = group['componentData']['label']
    assetXform = group['componentData']['xform']
    if 'components' in group:
        if group['components'] and (maxDepth == 0 or level < maxDepth):
            componentContent = search(group['components'], level=level + 1, maxDepth=maxDepth, searchInGroupAsset=searchInGroupAsset)
        else:
            componentContent = []
    else:
        logger.error('There is no component key on Dict')
        componentContent = []

    return {'name': assetlabel, 'xform': {'groupControl': assetXform}, 'components': componentContent}

def readGroupAsset(path, level, maxDepth=0):
    jsonPath = path.replace('.\wolftv', 'T:\FTP Downloaded Files\howlingtonClassroom\wolftv')  # todo remove hard Code!!
    if not os.path.isfile(jsonPath):
        logger.error('Path not found!!')
        return {'error path not found'}

    with open(jsonPath) as f:
        data2 = json.load(f)

    jsonContent = search(data2['components'], level=level, maxDepth=maxDepth)

    return jsonContent


def readDescription(path, level, maxDepth=0, searchInGroupAsset=True):
    jsonPath = path.replace('.\wolftv', 'T:\FTP Downloaded Files\howlingtonClassroom\wolftv')  # todo remove hard Code!!
    if not os.path.isfile(jsonPath):
        logger.error('Path not found!!')
        return {'error path not found'}

    with open(jsonPath) as f:
        data2 = json.load(f)

    jsonContent = search(data2['components'], level=level, maxDepth=maxDepth, searchInGroupAsset=searchInGroupAsset)

    return jsonContent


def search(components, level=0, maxDepth=0, searchInGroupAsset=True):
    returnList = []
    for elem in components:

        if elem['componentClass'] == 'FbRole':
            content = readFbRole(elem, level, maxDepth, searchInGroupAsset=searchInGroupAsset)
        elif elem['componentClass'] == 'Group':
            content = readGroup(elem, level, maxDepth, searchInGroupAsset=searchInGroupAsset)
        else:
            return []

        returnList.append(content)

    return returnList


def printDescription (x):
    for a in x:
        print a['name']
        for b in a['components']:
            print '-->',b['name']
            for c in b['components']:
                print '    -->', c['name']
                for d in c['components']:
                    print '        -->', d['name']


def insertFileInfo(path, projectName=None, task=None, code=None, type=None):
    if not os.path.exists(path):
        print 'file not exists'
        return

    newLines = []
    with open(path, 'rt') as scene_file:
        old_lines = scene_file.readlines ()
        for line in old_lines:
            newLine = None
            match = re.search('fileInfo "application" "maya";', line)
            if match:
                newLines.append('fileInfo "projectName" "'+projectName+'";\n')
                newLines.append('fileInfo "task" "'+task+'";\n')
                newLines.append('fileInfo "code" "'+code+'";\n')
                newLines.append('fileInfo "type" "'+type+'";\n')
                newLines.append(line)
            else:
                newLines.append(line)

    with open(path, 'wt') as scene_file:
        scene_file.writelines(newLines)


def ingestAtPath(pathSrc, pathTgt):
    setPiecesPath = r'wolftv\asset\set_piece'
    proxyModelPath = r'modeling\proxy_model\source'

    setPiecesFullPath = os.path.join(pathSrc, setPiecesPath)
    fileList = pm.getFileList(folder=setPiecesFullPath)

    for piece in fileList:
        print 'importing %s to pipeLine' % piece
        fileName = piece
        versionPath = os.path.join(setPiecesFullPath, fileName, proxyModelPath)
        versionsAvailable = pm.getFileList(folder = versionPath)
        maxVer = 0
        for ver in versionsAvailable:
            verNum = int(ver[1:])
            maxVer = max(maxVer, verNum)
            version = 'v%03d' % maxVer

        pieceFullPath = os.path.join(versionPath, version)
        pieceFile = pm.getFileList(folder=pieceFullPath)[0]
        pieceFullPath = os.path.join(pieceFullPath, pieceFile)

        ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': pieceFullPath,
                         'assetType': 'set_piece', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

        database.incrementNextCode ('asset', fromBegining=True)
        itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='static',
                                        customData={'ingestData': ingestionDict})

        item = Item(task='proxy',code=itemMData['proxy']['code'])
        item.status = 'created'
        item.putDataToDB()

        workPath = item.getWorkPath(make=True)
        shutil.copyfile(pieceFullPath, workPath)
        prj = database.getCurrentProject()
        insertFileInfo(workPath, projectName=prj, task=item.task, code=item.code, type=item.type)
        print '%s imported as %s' % (piece, item.task+item.code+item.name)
'''
### read description
with open('T:/test.json') as f:
    data = json.load(f)

pprint(data)


logger.setLevel(logging.DEBUG)


##ingest pieces
pathTgt = ['set', 'howlingtonClassroom', 'setPieces']
pathSrc = r'T:\FTP Downloaded Files\howlingtonClassroom'
ingestAtPath(pathSrc, pathTgt)
'''



### group
pathTgt = ['set', 'howlingtonClassroom', 'groups']
pathSrc = r'T:\FTP Downloaded Files\howlingtonClassroom'

groupPath = r'wolftv\asset\group'
proxyModelPath = r'modeling\proxy_model\desc'

groupsFullPath = os.path.join (pathSrc, groupPath)
logger.debug('groupFullPath: %s' % groupsFullPath)
fileList = pm.getFileList (folder=groupsFullPath)

for group in fileList:
    logger.info('importing %s to pipeLine' % group)
    fileName = group
    versionPath = os.path.join(groupsFullPath, fileName, proxyModelPath)
    logger.debug('versionPath: %s' % versionPath)
    versionsAvailable = pm.getFileList(folder=versionPath)
    logger.debug('versionAvailable: %s' % versionsAvailable)
    maxVer = 0
    for ver in versionsAvailable:
        verNum = int (ver[1:])
        maxVer = max (maxVer, verNum)
        version = 'v%03d' % maxVer
        logger.info(version)

    groupFullPath = os.path.join(versionPath, version)
    groupFile = pm.getFileList(folder=groupFullPath)[0]
    groupFullPath = os.path.join(groupFullPath, groupFile)
    logger.debug('groupFullPath: %s' % groupFullPath)
    ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': groupFullPath,
                 'assetType': 'group', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

    descDict = readDescription(groupFullPath, 1, maxDepth=0, searchInGroupAsset=False)

    database.incrementNextCode('asset', fromBegining=True)
    itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='group',
                                    customData={'ingestData': ingestionDict})

    itemProxy = Item(task='proxy', code=itemMData['proxy']['code'])
    itemModel = Item(task='model', code=itemMData['model']['code'])

    for component in descDict:
        logger.debug('add %s to %s' % (component['name'], fileName))
        logger.debug(component['xform'])
        itemList = database.searchName(component['name'])
        if 0 < len(itemList) > 1:
            proxyComponentMData = database.addComponent(item=itemProxy.getDataDict(), ns='ref',
                                                        componentCode=itemList[0]['code'],componentTask='proxy',
                                                        assembleMode='reference', update=True,
                                                        proxyMode='proxy', xform=component['xform'])
            logger.debug('proxy comp:%s'% proxyComponentMData)
            modelComponentMData = database.addComponent(item=itemModel.getDataDict(), ns='ref',
                                                        componentCode=itemList[0]['code'], componentTask='model',
                                                        assembleMode='reference', update=True,
                                                        proxyMode='', xform=component['xform'])
            logger.debug ('model comp:%s' % modelComponentMData)

# todo fazer as transformacoes dos components

