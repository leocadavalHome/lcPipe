import pymel.core as pm
import logging
import json
import os.path
import lcPipe.core.database as database
logger = logging.getLogger(__name__)
logger.setLevel(10)

def stripNamespace(name):
    return name.split(':')[-1]


def getObjMaterial(objName):
    obj = pm.PyNode(objName)
    objSG = pm.listConnections(obj.getShape(), type='shadingEngine')
    matList = pm.listConnections(objSG, destination=False)
    mat = pm.ls(matList, materials=True)[0]
    return mat


def saveShaders(presetDict=None, path=None):
    for ns in presetDict:
        shaderList = presetDict[ns]['shaderList']
        logger.info('saving shaders...')
        # define o nome da pasta de shaders, como o nome do asset, convertidos os ns para prefixos com '_'
        shadersPath = os.path.join(path, 'shaders', ns)

        # cria o diretorio se nao houver
        if not os.path.exists(shadersPath):
            os.makedirs(shadersPath)

        # grava cada shader da lista
        for shader in shaderList:
            SG = pm.listConnections(shader, type='shadingEngine')[0]
            pm.select(SG, r=True, ne=True)
            pm.exportSelected(os.path.join(shadersPath, shader + '.ma'), typ="mayaAscii", force=True)


def loadShader(presetName=None, shaderName=None, ns=None, path=None):
        shaderFullPath = os.path.join(path, 'shaders', ns, shaderName + '.ma')
        nodeList = pm.importFile(shaderFullPath, ns=presetName, mnc=True, typ="mayaAscii", rnn=True)


def savePreset(presetDict=None, path=None):
    saveShaders(presetDict=presetDict, path=path)

    name = os.path.basename(path)
    filePath = os.path.join(path, name+'.json')
    with open(filePath, 'w') as outfile:
        json.dump(presetDict, outfile)


def loadPreset(path=None):
    name = os.path.basename(path)
    filePath = os.path.join(path, name+'.json')
    with open(filePath) as f:
        lookDict = json.load(f)
    return lookDict

logger.info('saving preset...')

def gatherLookDict():
    sel = pm.ls(sl=True, type='transform')
    if not sel:
        selGeos = pm.ls(geometry=True)
        sel = pm.listRelatives(selGeos, parent=True)

    lookDict = {}

    sceneMData = database.getItemMData(fromScene=True)
    projectName = pm.fileInfo['projectName']
    lookDict['sourceAsset'] = {'name': sceneMData['name'], 'task': sceneMData['task'],
                               'code': sceneMData['code'], 'projectName': projectName,
                               'assetType': sceneMData['type']}

    shaderList = []
    for obj in sel:
        ns = obj.namespace()
        if not ns:
            ns = 'root'
        else:
            ns = ns[:-1]
        mat = getObjMaterial(obj)
        if ns in lookDict:
            lookDict[ns]['assign'].update({stripNamespace(obj.name()): mat.name()})
            if mat.name() not in lookDict[ns]['shaderList']:
                lookDict[ns]['shaderList'].append(mat.name())
        else:
            lookDict[ns] = {'shaderList': [mat.name()], 'assign': {stripNamespace(obj.name()): mat.name()}}

    logger.debug(shaderList)
    logger.debug(lookDict)
    return lookDict


def assignPreset(lookDict=None, path=None, useNS=False):
    oldShadersList =set()
    presetName = os.path.basename (path)
    for ns in lookDict:

        if ns == 'root':
            nameSpace = ''
        else:
            nameSpace = ns

        assignList = lookDict[ns]['assign']
        logger.debug(assignList)
        for obj, shaderName in assignList.iteritems():

            if useNS:
                objList = pm.ls(nameSpace+':'+obj)
            else:
                objList = pm.ls(obj, r=True)

            if not pm.objExists(presetName+':'+shaderName):
                shaderFullPath = os.path.join(path, 'shaders', ns, shaderName + '.ma')
                logger.debug(shaderFullPath)
                nodeList = pm.importFile(shaderFullPath, ns=presetName, mnc=True, typ="mayaAscii", rnn=True)
                # todo implementar a remocao de ns q vier com o shader

            SG = pm.listConnections(presetName+':'+shaderName, type='shadingEngine')[0]

            oldShaders = [getObjMaterial(x) for x in objList]
            logger.debug(objList)
            logger.debug(SG)
            pm.sets(SG, e=True, forceElement=objList)
            # guarda a lista de shaders antigos para apagar.
            oldShadersList += oldShaders

    oldShadersList.discard('lambert1')
    for shader in oldShadersList:
        SG = pm.listConnections (shader, type='shadingEngine')[0]
        geoList = pm.listConnections (SG, type='shape')
        if not (geoList):
            try:
                pm.delete (shader, SG)
            except:
                print 'nao deu pra apagar shader'

    pm.namespace(moveNamespace=[presetName, ':'], force=True)
    pm.namespace(removeNamespace=presetName)


lookDict = gatherLookDict()
saveShaders(presetDict=lookDict, path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib\teste2')
savePreset(presetDict=lookDict, path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib\teste2')
logger.info('preset saved')

lookDict = loadPreset(path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib\teste2')
logger.debug(lookDict)
assignPreset(lookDict=lookDict, path=None)