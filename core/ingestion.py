import json
import pymel.core as pm
import json
from pprint import pprint
import os.path
import lcPipe.core.database as database
from lcPipe.api.item import Item
import shutil
import re
import os

with open('T:/test.json') as f:
    data = json.load(f)

pprint(data)

def readGroupAsset(path, level):
    jsonPath = path.replace('.\wolftv', 'T:\FTP Downloaded Files\howlingtonClassroom\wolftv')

    if not os.path.isfile(jsonPath):
        print 'nao achou path!!'
        return

    with open (jsonPath) as f:
        data2 = json.load (f)
    print 'json'
    search(data2['components'], level+1)
    print 'endjson'

def readFbRole(FbRole, level):
    assetType = FbRole['componentData']['assetType']
    assetCode = FbRole['componentData']['assetCode']

    print (('  '*level) + assetCode, assetType)

    if assetType == 'set_piece':
        modelAssetPath = FbRole['components'][0]['componentData']['sourcePath']
        print (('  ' * (level + 1)) + modelAssetPath)
        controlXform1 = FbRole['components'][1]['componentData']['inner_ctl_data']
        controlXform2 = FbRole['components'][1]['componentData']['mid_ctl_data']
        controlXform3 = FbRole['components'][1]['componentData']['outer_ctl_data']
        print (('  ' * (level + 1)), controlXform1)
        print (('  ' * (level + 1)), controlXform2)
        print (('  ' * (level + 1)), controlXform3)
    elif assetType == 'group':
        print (('  ' * (level + 1)) + 'groupAsset')
        groupAssetPath = FbRole['components'][0]['componentData']['sourcePath']
        print (('  ' * (level + 1)) + groupAssetPath)
        readGroupAsset(groupAssetPath, level+1)


def readGroup (group, level):
    assetlabel = group['componentData']['label']
    assetXform = group['componentData']['xform']
    print (('  '*level) + assetlabel, assetXform)


def search(components, level=0):
    for elem in components:
        print (('  '*level) + elem['componentClass'])
        if elem['componentClass'] == 'FbRole':
            readFbRole(elem, level)

        elif elem['componentClass'] == 'Group':
            readGroup(elem, level)

        if 'components' in elem:
            if elem['components']:
                search(elem['components'], level=level+1)
        else:
            print (('  '*level) + 'nao tem components key')
search(data['components'])


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

pathTgt = ['set', 'howlingtonClassroom', 'setPieces']
pathSrc = r'T:\FTP Downloaded Files\howlingtonClassroom'
ingestAtPath(pathSrc, pathTgt)