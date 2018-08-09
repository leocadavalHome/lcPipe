import json
import pymel.core as pm
import json
from pprint import pprint
import os.path
import lcPipe.core.database as database

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

def ingestAtPath(pathSrc, pathTgt):
    pass
pathTgt = ['set','howlingtonClassroom', 'setPieces']
pathSrc = r'T:\FTP Downloaded Files\howlingtonClassroom'
setPiecesPath  = r'wolftv\asset\set_piece'
proxyModelPath = r'modeling\proxy_model\source'

setPiecesFullPath = os.path.join (pathSrc, setPiecesPath)
print setPiecesFullPath
fileList = pm.getFileList(folder=setPiecesFullPath)
print fileList

for piece in fileList:
    fileName = piece
    versionPath = os.path.join(setPiecesFullPath, fileName, proxyModelPath)
    versionsAvailable = pm.getFileList(folder = versionPath)
    maxVer = 0
    for ver in versionsAvailable:
        verNum = int(ver[1:])
        maxVer = max(maxVer, verNum)
        version = 'v%03d' % maxVer

    pieceFullPath = os.path.join(versionPath, version)
    pieceFile = pm.getFileList(folder = pieceFullPath)[0]
    pieceFullPath = os.path.join (pieceFullPath, pieceFile)

    print pieceFullPath
    ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': pieceFullPath,
                     'assetType': 'set_piece', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

    print ingestionDict
    print database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='static')



