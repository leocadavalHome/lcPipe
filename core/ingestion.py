import pymel.core as pm
import json
import os.path
import lcPipe.core.database as database
from lcPipe.api.item import Item
import shutil
import re
import os
import logging

logger = logging.getLogger(__name__)
logger.setLevel(10)

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
    try:
        if group['components'] and (maxDepth == 0 or level < maxDepth):
            componentContent = search(group['components'], level=level + 1, maxDepth=maxDepth, searchInGroupAsset=searchInGroupAsset)
        else:
            componentContent = []
    except KeyError:
        logger.error('There is no component key on Dict')
        componentContent = []

    return {'name': assetlabel, 'subType': 'sceneGroup',
            'xform': {'groupControl': {'rotatePivot': [0, 0, 0], 'scalePivot': [0, 0, 0], 'xform': assetXform}},
            'components': componentContent}

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
        if 'subType' in a:
            print a['name']
            print a['subType']
        for b in a['components']:
            print '-->',b['name']
            if 'subType' in b:
                print '-->', b['subType']
            for c in b['components']:
                print '    -->', c['name']
                if 'subType' in c:
                    print '    -->', c['subType']
                for d in c['components']:
                    print '        -->', d['name'], d['subType']
                    if 'subType' in d:
                        print '        -->', d['subType']


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


def ingestPieces(pathSrc, pathTgt):
    setPiecesPath = r'wolftv\asset\set_piece'
    proxyModelPath = r'modeling\proxy_model\source'

    setPiecesFullPath = os.path.join(pathSrc, setPiecesPath)
    fileList = pm.getFileList(folder=setPiecesFullPath)

    for piece in fileList:
        logger.info('importing %s to pipeLine' % piece)
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

        database.incrementNextCode('asset', fromBegining=True)
        itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='static',
                                        customData={'ingestData': ingestionDict})

        item = Item(task='proxy', code=itemMData['proxy']['code'])
        item.status = 'created'
        item.putDataToDB()

        workPath = item.getWorkPath(make=True)
        shutil.copyfile(pieceFullPath, workPath)

        prj = database.getCurrentProject()
        insertFileInfo(workPath, projectName=prj, task=item.task, code=item.code, type=item.type)

        # todo copy to publish folder
        item.publishVer += 1
        publishPath = item.getPublishPath(make=True)
        shutil.copyfile(workPath, publishPath)
        item.putDataToDB()

        logger.info('%s imported as %s and published' % (piece, item.task + item.code + item.name))


def ingestGroups(pathSrc, pathTgt):
    groupPath = r'wolftv\asset\group'
    proxyModelPath = r'modeling\proxy_model\desc'

    groupsFullPath = os.path.join(pathSrc, groupPath)
    logger.debug('groupFullPath: %s' % groupsFullPath)
    fileList = pm.getFileList (folder=groupsFullPath)

    for group in fileList:
        logger.info('importing %s to pipeLine' % group)
        fileName = group
        versionPath = os.path.join(groupsFullPath, fileName, proxyModelPath)
        versionsAvailable = pm.getFileList(folder=versionPath)
        maxVer = 0
        for ver in versionsAvailable:
            verNum = int(ver[1:])
            maxVer = max(maxVer, verNum)
            version = 'v%03d' % maxVer

        groupFullPath = os.path.join(versionPath, version)
        groupFile = pm.getFileList(folder=groupFullPath)[0]
        groupFullPath = os.path.join(groupFullPath, groupFile)

        ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': groupFullPath,
                         'assetType': 'group', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

        database.incrementNextCode('asset', fromBegining=True)
        itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='group',
                                        customData={'ingestData': ingestionDict})
        itemProxy = Item(task='proxy', code=itemMData['proxy']['code'])
        itemModel = Item(task='model', code=itemMData['model']['code'])

        descDict = readDescription(groupFullPath, 1, maxDepth=0, searchInGroupAsset=True)
        for component in descDict:
            logger.debug('add %s to %s' % (component['name'], fileName))
            itemList = database.searchName(component['name'])
            if 0 < len(itemList) > 1:
                proxyComponentMData = database.addSource(item=itemProxy.getDataDict(), ns='ref',
                                                         componentCode=itemList[0]['code'], componentTask='proxy',
                                                         assembleMode='reference', update=True,
                                                         proxyMode='proxy', xform=component['xform'], onSceneParent='')
                modelComponentMData = database.addSource(item=itemModel.getDataDict(), ns='ref',
                                                         componentCode=itemList[0]['code'], componentTask='proxy',
                                                         assembleMode='reference', update=True,
                                                         proxyMode='', xform=component['xform'], onSceneParent='')


def ingestSet(pathSrc , pathTgt):
    descDict = readDescription(pathSrc, level=1, maxDepth=0, searchInGroupAsset=True)

    descName, file_extension = os.path.splitext(os.path.basename(pathSrc))
    fileName = descName.split('_')[0]
    ver = descName.split('.')[-1]

    ingestionDict = {'name': fileName, 'version': ver, 'sourcePath': pathSrc,
                     'assetType': 'group', 'task': 'proxy', 'setAssemble': ''}

    database.incrementNextCode('asset', fromBegining=True)
    itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='group',
                                    customData={'ingestData': ingestionDict})
    item = Item(task='proxy', code=itemMData['proxy']['code'])
    addComponentsToSet(item=itemMData['proxy'], onSceneParent='', components=descDict)


def addComponentsToSet(item=None, onSceneParent='', components=[], groupComponents=True):
    for object in components:
        if object['subType'] == 'sceneGroup':
            groupMData = database.addSource(item=item, ns=onSceneParent+'Ref',
                                            componentCode=object['name'],
                                            componentTask='asset',
                                            assembleMode='createGroup', update=True,
                                            proxyMode='', xform=object['xform'],
                                            onSceneParent=onSceneParent)

            if object['components']:
                addComponentsToSet(item=item, onSceneParent=object['name'],
                                   components=object['components'])


        if object['subType'] == 'set_piece':
            itemList = database.searchName(object['name'])
            if 0 < len(itemList) > 1:
                proxyMData = database.addSource(item=item, ns=onSceneParent+'Ref'+str(object['instanceNumber']),
                                                componentCode=itemList[0]['code'], componentTask='proxy',
                                                assembleMode='reference', update=True,
                                                proxyMode='proxy', xform=object['xform'],
                                                onSceneParent=onSceneParent)


        if object['subType'] == 'group':
            if not groupComponents:
                itemList = database.searchName(object['name'])
                if 0 < len(itemList) > 1:
                    proxyMData = database.addSource(item=item, ns=onSceneParent+'Ref'+str(object['instanceNumber']),
                                                    componentCode=itemList[0]['code'], componentTask='proxy',
                                                    assembleMode='reference', update=True,
                                                    proxyMode='proxy', xform=object['xform'],
                                                    onSceneParent=onSceneParent)
            else:
                groupMData = database.addSource(item=item, ns=onSceneParent + 'Ref'+str(object['instanceNumber']),
                                                componentCode=object['name']+str(object['instanceNumber']),
                                                componentTask='asset', assembleMode='createGroup', update=True,
                                                proxyMode='', xform=object['xform'],
                                                onSceneParent=onSceneParent)
                if object['components']:
                    addComponentsToSet(item=item, onSceneParent=object['name']+str(object['instanceNumber']),
                                       components=object['components'])


def browseCallBack(*args):
    resultDir = pm.fileDialog2 (cap='choose directory', okCaption='Select', fm=3, dialogStyle=2)
    if resultDir:
        pm.textField ('pathTxtField', e=True, tx=os.path.normpath (resultDir[0]))
        listSets ()


def listSets():
    searchDir = pm.textField ('pathTxtField', q=True, tx=True)
    sets = next (os.walk (searchDir))[1]
    pm.textScrollList ('setScrollList', e=True, ra=True)
    pm.textScrollList ('setScrollList', e=True, append=sets)


def selectSetCallback(*args):
    sel = pm.textScrollList ('setScrollList', q=True, si=True)
    searchDir = pm.textField ('pathTxtField', q=True, tx=True)
    if sel:
        groupDir = os.path.join (searchDir, sel[0], 'wolftv', 'asset', 'group')
        print groupDir
        if os.path.isdir (groupDir):
            pm.text ('groupTxt', e=True, l='   found!')
        else:
            pm.text ('groupTxt', e=True, l='   no diretory found')

        set_pieceDir = os.path.join (searchDir, sel[0], 'wolftv', 'asset', 'set_piece')
        print set_pieceDir
        if os.path.isdir (set_pieceDir):
            pm.text ('pieceTxt', e=True, l='   found!')
        else:
            pm.text ('pieceTxt', e=True, l='   no diretory found')

        descriptionFileDir = os.path.join (searchDir, sel[0])
        descList = pm.getFileList (folder=descriptionFileDir, filespec='*.json')
        if len (descList) == 1:
            pm.text ('descriptionTxt', e=True, l='   found!')
        elif len (descList) > 1:
            pm.text ('descriptionTxt', e=True, l='   more than one found!')
        else:
            pm.text ('descriptionTxt', e=True, l='   no json file found!')


def importCallback(*args):
    sel = pm.textScrollList ('setScrollList', q=True, si=True)
    searchDir = pm.textField ('pathTxtField', q=True, tx=True)
    if sel:
        if pm.text('groupTxt', q=True, label=True) == '   found!':
            resp = pm.confirmDialog(title='Import Groups', ma='center',
                                    message='Import Group?',
                                    button=['Ok', 'No'], defaultButton='Ok', dismissString='No')
            if resp == 'Ok':
                pathTgt = ['set', sel[0], 'group']
                pathSrc = os.path.join(searchDir, sel[0])
                database.addFolder(['set', sel[0], 'group'])
                ingestGroups(pathSrc, pathTgt)

        if pm.text('pieceTxt', q=True, label=True) == '   found!':
            resp = pm.confirmDialog(title='Import set_pieces', ma='center',
                                    message='Import Set_Pieces?',
                                    button=['Ok', 'No'], defaultButton='Ok', dismissString='No')
            if resp == 'Ok':
                pathTgt = ['set', sel[0], 'setPiece']
                pathSrc = os.path.join(searchDir, sel[0])
                database.addFolder(['set', sel[0], 'setPiece'])
                ingestPieces(pathSrc, pathTgt)

        if pm.text('descriptionTxt', q=True, label=True) == '   found!':
            resp = pm.confirmDialog(title='Import File Description', ma='center',
                                    message='Import File Description?',
                                    button=['Ok', 'No'], defaultButton='Ok', dismissString='No')
            if resp == 'Ok':
                descriptionFileDir = os.path.join(searchDir, sel[0])
                descList = pm.getFileList (folder=descriptionFileDir, filespec='*.json')
                if len(descList) == 1:
                    fileDescName = descList[0]
                    pathTgt = ['set', sel[0]]
                    pathSrc = os.path.join(searchDir, sel[0], fileDescName)
                    database.addFolder(['set', sel[0]])
                    ingestSet(pathSrc, pathTgt)


def cancelCallback(*args):
    pm.deleteUI ('FlyingBarkIngestTool', window=True)


def fbIngestTool():
    if pm.window ('FlyingBarkIngestTool', exists=True):
        pm.deleteUI ('FlyingBarkIngestTool', window=True)

    pm.window ('FlyingBarkIngestTool')
    pm.columnLayout ()
    pm.rowLayout (nc=3)
    pm.text (l='PATH')
    pm.textField ('pathTxtField', w=205)
    pm.button (l='...', c=browseCallBack)
    pm.setParent ('..')
    pm.separator (h=20)
    pm.text (label='SETS')
    pm.separator (h=5)
    pm.textScrollList ('setScrollList', h=150, sc=selectSetCallback)
    pm.separator (h=10)
    pm.rowLayout (nc=2)
    pm.text (label='GROUP DIR')
    pm.text ('groupTxt', l='')
    pm.setParent ('..')
    pm.separator (h=10)
    pm.rowLayout (nc=2)
    pm.text (label='SET_PIECES DIR')
    pm.text ('pieceTxt', l='')
    pm.setParent ('..')
    pm.separator (h=10)
    pm.rowLayout (nc=2)
    pm.text (label='DESCRIPTION FILE')
    pm.text ('descriptionTxt', l='')
    pm.setParent ('..')
    pm.separator (h=20)
    pm.rowLayout (nc=2)
    pm.button ('Import', label='Import', w=125, h=50, c=importCallback)
    pm.button ('CancelBtn', label='Cancel', w=125, h=50)
    pm.showWindow ()
