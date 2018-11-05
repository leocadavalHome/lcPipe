import pymel.core as pm
import json
import os.path
import lcPipe.core.database as database
from lcPipe.api.item import Item
import shutil
import re
import os
import logging
from lcPipe.ui.progressWidget import ProgressWindowWidget

logger = logging.getLogger(__name__)
logger.setLevel(10)

def readFbRole(FbRole, level, maxDepth=0, searchInGroupAsset=True, basePath=None):
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
            jsonContent = readGroupAsset(groupAssetPath, level=level+1, maxDepth=maxDepth, basePath=basePath)
        else:
            jsonContent = {}

        return {'name': assetCode, 'instanceNumber': assetInstanceNumber, 'subType': 'group', 'task': groupAssetTask,
                'sourcePath': groupAssetPath,
                'xform': {'innerControl': controlXform1, 'midControl': controlXform2, 'outerControl': controlXform3},
                'components': jsonContent}


def readGroup (group, level, maxDepth=0, searchInGroupAsset=True, basePath=None):
    assetlabel = group['componentData']['label']
    assetXform = group['componentData']['xform']
    try:
        if group['components'] and (maxDepth == 0 or level < maxDepth):
            componentContent = search(group['components'], level=level + 1, maxDepth=maxDepth,
                                      searchInGroupAsset=searchInGroupAsset, basePath=basePath)
        else:
            componentContent = []
    except KeyError:
        logger.error('There is no component key on Dict')
        componentContent = []

    return {'name': assetlabel, 'subType': 'sceneGroup',
            'xform': {'groupControl': {'rotatePivot': [0, 0, 0], 'scalePivot': [0, 0, 0], 'xform': assetXform}},
            'components': componentContent}


def readGroupAsset(path, level, maxDepth=0, basePath=None):
    jsonPath = path
    logger.debug ('jsonPath: %s ' % jsonPath)

    if not os.path.isfile(jsonPath):
        logger.error('Path not found!!')
        return {'error path not found'}

    with open(jsonPath) as f:
        data2 = json.load(f)

    jsonContent = search(data2['components'], level=level, maxDepth=maxDepth, basePath=basePath)

    return jsonContent


def readDescription(descFileName, path, level, maxDepth=0, searchInGroupAsset=True):

    jsonPath = os.path.join(path, descFileName)  # done remove hard Code!!
    logger.debug('jsonPath: %s ' % jsonPath)
    if not os.path.isfile(jsonPath):
        logger.error('Path not found!!')
        return {'error path not found'}

    with open(jsonPath) as f:
        data2 = json.load(f)

    jsonContent = search(data2['components'], level=level, maxDepth=maxDepth,
                         searchInGroupAsset=searchInGroupAsset, basePath=path)

    return jsonContent


def search(components, level=0, maxDepth=0, searchInGroupAsset=True, basePath=None):
    returnList = []
    for elem in components:

        if elem['componentClass'] == 'FbRole':
            content = readFbRole(elem, level, maxDepth, searchInGroupAsset=searchInGroupAsset, basePath=basePath)
        elif elem['componentClass'] == 'Group':
            content = readGroup(elem, level, maxDepth, searchInGroupAsset=searchInGroupAsset, basePath=basePath)
        else:
            return []

        returnList.append(content)

    return returnList


def insertFileInfo(path, projectName=None, task=None, code=None, type=None):
    if not os.path.exists(path):
        logger.info('file not exists')
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


def ingestPieces(pathSrc=None, pathTgt=None, selList=None):
    proxyModelPath = r'modeling\proxy_model\source'
    setPiecesFullPath = pathSrc
    fileList = pm.getFileList(folder=setPiecesFullPath)

    if selList:
        ingestList = [x for x in fileList if x in selList]
        if len(ingestList) != len (selList):
            resp = pm.confirmDialog (title='Missing', message='Missing some set pieces. Continue?',
                                     button=['Yes', "No", 'Cancel'], defaultButton='Yes',
                                     cancelButton='Cancel', dismissString='Cancel')
            if not resp == 'Yes':
                return 'error'
    else:
        ingestList = fileList

    progressWin = ProgressWindowWidget(title='set pieces', maxValue=len(fileList))
    for piece in ingestList:
        logger.info('importing %s to pipeLine' % piece)
        progressWin.progressUpdate(1)

        itemExist = database.searchName(piece)
        if itemExist:
            logger.info ('already exists! skipping %s' % piece)
            continue

        fileName = piece
        versionPath = os.path.join(setPiecesFullPath, fileName, proxyModelPath)
        versionsAvailable = pm.getFileList(folder = versionPath)
        maxVer = 0
        version = None

        if not versionsAvailable:
            continue

        for ver in versionsAvailable:
            verNum = int(ver[1:])
            maxVer = max(maxVer, verNum)
            version = 'v%03d' % maxVer

        if not version:
            logger.error('No version for %s' % piece)
            continue

        pieceFullPath = os.path.join(versionPath, version)

        try:
            pieceFile = pm.getFileList(folder=pieceFullPath)[0]
        except ValueError:
            logger.error('No file found for %s' % piece)
            continue

        pieceFullPath = os.path.join(pieceFullPath, pieceFile)

        ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': pieceFullPath,
                         'assetType': 'set_piece', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

        database.incrementNextCode('asset', fromBegining=True)
        itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='static',
                                        customData={'ingestData': ingestionDict})

        item = Item(task='proxy', code=itemMData['proxy']['code'])
        item.status = 'created'
        item.putDataToDB()

        workPath = item.getServerWorkPath(make=True)
        shutil.copyfile(pieceFullPath, workPath)

        prj = database.getCurrentProject()
        insertFileInfo(workPath, projectName=prj, task=item.task, code=item.code, type=item.type)

        # done copy to publish folder
        item.publishVer += 1
        publishPath = item.getPublishPath(make=True)
        shutil.copyfile(workPath, publishPath)
        item.putDataToDB()

        logger.info('%s imported as %s and published' % (piece, item.task + item.code + item.name))
    progressWin.closeWindow()

def ingestGroups(pathSrc, pathTgt):
    groupPath = r'group'
    proxyModelPath = r'modeling\proxy_model\desc'

    groupsFullPath = os.path.join(pathSrc, groupPath)
    logger.debug('groupFullPath: %s' % groupsFullPath)
    fileList = pm.getFileList(folder=groupsFullPath)

    if not fileList:
        logger.error('No file Found!')
        return

    progressWin = ProgressWindowWidget(title='groups', maxValue=len (fileList))

    for group in fileList:
        logger.info('importing %s to pipeLine' % group)
        progressWin.progressUpdate (1)

        fileName = group
        versionPath = os.path.join(groupsFullPath, fileName, proxyModelPath)
        versionsAvailable = pm.getFileList(folder=versionPath)
        version = 0
        maxVer = 0

        if not versionsAvailable:
            continue

        for ver in versionsAvailable:
            verNum = int(ver[1:])
            maxVer = max(maxVer, verNum)
            version = 'v%03d' % maxVer

        groupFullPath = os.path.join(versionPath, version)
        groupFile = pm.getFileList(folder=groupFullPath)[0]

        ingestionDict = {'name': fileName, 'version': maxVer, 'sourcePath': groupFullPath,
                         'assetType': 'group', 'task': 'proxy', 'setAssemble': os.path.split(pathSrc)[-1]}

        database.incrementNextCode('asset', fromBegining=True)
        itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='group',
                                        customData={'ingestData': ingestionDict})
        itemProxy = Item(task='proxy', code=itemMData['proxy']['code'])
        itemModel = Item(task='model', code=itemMData['model']['code'])

        descDict = readDescription(groupFile, groupFullPath, 1, maxDepth=0, searchInGroupAsset=True)
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
                                                         proxyMode='model', xform=component['xform'], onSceneParent='')
    progressWin.closeWindow()


def listSetPieces(descDict):
    setPieceList = []
    for a in descDict:
        if 'subType' in a:
            if a['subType'] == 'set_piece':
                setPieceList.append(a['name'])
        if a['components']:
            componentsSetPieceList = listSetPieces (a['components'])
            setPieceList += componentsSetPieceList
    return setPieceList


def ingestSet(descFileName=None, pathSrc=None, pathTgt=None,
              selectiveIngest=False, pathPieceSrc=None, pathPieceTgt=['setPiece']):

    descDict = readDescription(descFileName, pathSrc, level=1, maxDepth=0, searchInGroupAsset=True)

    if selectiveIngest:
        setPieceList = listSetPieces(descDict)
        database.addFolder(pathPieceTgt)
        result = ingestPieces(pathPieceSrc, pathPieceTgt, selList=setPieceList)
        if result == 'error':
            return

    descName, file_extension = os.path.splitext(descFileName)
    fileName = descName.split('_')[0]
    ver = descName.split('.')[-1]

    ingestionDict = {'name': fileName, 'version': ver, 'sourcePath': pathSrc,
                     'assetType': 'group', 'task': 'proxy', 'setAssemble': ''}
    database.addFolder(pathTgt)
    database.incrementNextCode('asset', fromBegining=True)
    itemMData = database.createItem(itemType='asset', name=fileName, path=pathTgt, workflow='group',
                                    customData={'ingestData': ingestionDict})

    addComponentsToSet(item=itemMData['proxy'], onSceneParent='', components=descDict, proxyMode='proxy' )
    addComponentsToSet(item=itemMData['model'], onSceneParent='', components=descDict, proxyMode='model')


def addComponentsToSet(item=None, onSceneParent='', components=[], groupComponents=True, proxyMode='proxy'):
    progressWin = ProgressWindowWidget (title=onSceneParent, maxValue=len(components))

    for obj in components:
        progressWin.progressUpdate (1)
        if obj['subType'] == 'sceneGroup':
            groupMData = database.addSource(item=item, ns=onSceneParent+'Ref',
                                            componentCode=obj['name'],
                                            componentTask='asset',
                                            assembleMode='createGroup', update=True,
                                            proxyMode='asset', xform=obj['xform'],
                                            onSceneParent=onSceneParent)

            if obj['components']:
                addComponentsToSet(item=item, onSceneParent=obj['name'],
                                   components=obj['components'], proxyMode=proxyMode)


        if obj['subType'] == 'set_piece':
            itemList = database.searchName(obj['name'])
            if 0 < len(itemList) > 1:
                proxyMData = database.addSource(item=item, ns=onSceneParent+'Ref'+str(obj['instanceNumber']),
                                                componentCode=itemList[0]['code'], componentTask='proxy',
                                                assembleMode='reference', update=True,
                                                proxyMode=proxyMode, xform=obj['xform'],
                                                onSceneParent=onSceneParent)


        if obj['subType'] == 'group':
            if not groupComponents:
                itemList = database.searchName(obj['name'])
                if 0 < len(itemList) > 1:
                    proxyMData = database.addSource(item=item, ns=onSceneParent+'Ref'+str(obj['instanceNumber']),
                                                    componentCode=itemList[0]['code'], componentTask='proxy',
                                                    assembleMode='reference', update=True,
                                                    proxyMode=proxyMode, xform=obj['xform'],
                                                    onSceneParent=onSceneParent)
            else:
                groupMData = database.addSource(item=item, ns=onSceneParent + 'Ref'+str(obj['instanceNumber']),
                                                componentCode=obj['name']+str(obj['instanceNumber']),
                                                componentTask='asset', assembleMode='createGroup', update=True,
                                                proxyMode='asset', xform=obj['xform'],
                                                onSceneParent=onSceneParent)
                if obj['components']:
                    addComponentsToSet(item=item, onSceneParent=obj['name']+str(obj['instanceNumber']),
                                       components=obj['components'], proxyMode=proxyMode)
    progressWin.closeWindow()


def browseCallBack(*args):
    resultDir = pm.fileDialog2 (cap='choose directory', okCaption='Select', fm=3, dialogStyle=2)
    if resultDir:
        pm.textField ('pathTxtField', e=True, tx=os.path.normpath (resultDir[0]))
        listSets()


def listSets():
    searchDir = pm.textField ('pathTxtField', q=True, tx=True)
    sets = next (os.walk (os.path.join(searchDir, 'set')))[1]
    pm.textScrollList ('setScrollList', e=True, ra=True)
    pm.textScrollList ('setScrollList', e=True, append=sets)


def selectSetCallback(*args):
    sel = pm.textScrollList('setScrollList', q=True, si=True)
    searchDir = pm.textField('pathTxtField', q=True, tx=True)
    pm.text ('descriptionPathTxt', e=True, l='')
    pm.text ('descriptionNameTxt', e=True, l='')

    if sel:
        groupDir = os.path.join (searchDir, 'group')
        if os.path.isdir (groupDir):
            pm.text ('groupTxt', e=True, l='   found!')
        else:
            pm.text ('groupTxt', e=True, l='   no diretory found')

        set_pieceDir = os.path.join (searchDir, 'set_piece')
        if os.path.isdir (set_pieceDir):
            pm.text ('pieceTxt', e=True, l='   found!')
        else:
            pm.text ('pieceTxt', e=True, l='   no diretory found')

        versionPath = os.path.join(searchDir, 'set', sel[0], r'modeling\proxy_model\desc')
        versionsAvailable = pm.getFileList(folder=versionPath)
        maxVer = 0
        version = None

        if versionsAvailable:
            for ver in versionsAvailable:
                verNum = int(ver[1:])
                maxVer = max(maxVer, verNum)
                version = 'v%03d' % maxVer

            descriptionFileDir = os.path.join (versionPath, version)
            descList = pm.getFileList (folder=descriptionFileDir, filespec='*.json')

            if len (descList) == 1:
                pm.text ('descriptionTxt', e=True, l='   found!')
                pm.text ('descriptionPathTxt', e=True, l=descriptionFileDir)
                pm.text ('descriptionNameTxt', e=True, l=descList[0])
            elif len (descList) > 1:
                pm.text ('descriptionTxt', e=True, l='   more than one found!')
            else:
                pm.text ('descriptionTxt', e=True, l='   no json file found!')
        else:
            pm.text ('descriptionTxt', e=True, l='   no file found!')


def importCallback(*args):
    sel = pm.textScrollList('setScrollList', q=True, si=True)
    searchDir = pm.textField('pathTxtField', q=True, tx=True)
    descName = pm.text('descriptionNameTxt', q=True, l=True)
    descPath = pm.text('descriptionPathTxt', q=True, l=True)
    pathTgt = ['set']
    pathPieceTgt = ['setPiece']
    piecePath = os.path.join (searchDir,'set_piece')

    if sel:
        ingestSet(descFileName=descName, pathSrc=descPath, pathTgt=pathTgt, selectiveIngest=True,
                  pathPieceSrc=piecePath, pathPieceTgt=pathPieceTgt)

    pm.deleteUI('FlyingBarkIngestTool', window=True)

def cancelCallback(*args):
    pm.deleteUI('FlyingBarkIngestTool', window=True)


def fbIngestTool():
    if pm.window('FlyingBarkIngestTool', exists=True):
        pm.deleteUI('FlyingBarkIngestTool', window=True)

    pm.window ('FlyingBarkIngestTool', w=300,h=400, sizeable = False)
    pm.columnLayout ()
    pm.rowLayout (nc=3)
    pm.text (l='PATH')
    pm.textField ('pathTxtField', w=390, tx=r'T:\jobs\wolftv\asset')
    pm.button (l='...', c=browseCallBack)
    pm.setParent ('..')
    pm.separator (h=20)
    pm.text (label='SETS')
    pm.separator (h=5)
    pm.textScrollList('setScrollList',w=444, h=150, sc=selectSetCallback)
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
    pm.separator (h=10)
    pm.text ('descriptionPathTxt',ww=True, l='')
    pm.separator (h=10)
    pm.text ('descriptionNameTxt', l='')
    pm.separator (h=20)
    pm.rowLayout (nc=2)
    pm.button ('Import', label='Import', w=222, h=50, c=importCallback)
    pm.button ('CancelBtn', label='Close', w=222, h=50, c=cancelCallback)
    listSets()
    pm.showWindow ()