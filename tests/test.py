import pymel.core as pm
import logging
import json
import os.path
import lcPipe.core.database as database
logger = logging.getLogger(__name__)
logger.setLevel(10)

def stripNamespace(name):
    return name.split(':')[-1]


def getObjMaterial(obj):
    objSG = pm.listConnections(obj.getShape(), type='shadingEngine')
    matList = pm.listConnections(objSG, destination=False)
    mat = pm.ls(matList, materials=True)[0]
    return mat


def saveShaders(presetDict=None, path=None):
    for ns in presetDict:
        shaderList = presetDict[ns]['shaderList']
        logger.info ('saving shaders...')
        # define o nome da pasta de shaders, como o nome do asset, convertidos os ns para prefixos com '_'
        shadersPath = os.path.join (path, 'shaders', ns)

        # cria o diretorio se nao houver
        if not os.path.exists (shadersPath):
            os.makedirs (shadersPath)

        # grava cada shader da lista
        for shader in shaderList:
            SG = pm.listConnections(shader, type='shadingEngine')[0]
            pm.select (SG, r=True, ne=True)
            pm.exportSelected (os.path.join (shadersPath, shader + '.ma'), typ="mayaAscii", force=True)


def loadShader(presetName=None, shaderName=None, ns=None, path=None):
        shaderFullPath = os.path.join (path, 'shaders', ns, shaderName + '.ma')
        nodeList = pm.importFile (shaderFullPath, ns=presetName, mnc=True, typ="mayaAscii", rnn=True)


def savePreset(presetDict=None, path=None):
    with open (path, 'w') as outfile:
        json.dump (presetDict, outfile)


def loadPreset(path=None):
    with open(path) as f:
        lookDict = json.load(f)
    return lookDict

logger.info('saving preset...')

sel = pm.ls(sl=True, type='transform')
if not sel:
    selGeos = pm.ls(geometry=True)
    sel = pm.listRelatives(selGeos, parent=True)

lookDict = {}
shaderList = []
for obj in sel:
    ns = obj.namespace()[:-1]
    mat = getObjMaterial(obj)
    if ns in lookDict:
        lookDict[ns]['assign'].update({stripNamespace(obj.name()): mat.name()})
        if mat.name() not in lookDict[ns]['shaderList']:
            lookDict[ns]['shaderList'].append(mat.name())
    else:
        lookDict[ns] = {'shaderList': [mat.name()], 'assign': {stripNamespace(obj.name()): mat.name()}}

logger.debug(shaderList)
logger.debug(lookDict)

saveShaders(presetDict=lookDict, path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib')
savePreset(presetDict=lookDict, path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib\teste2')
logger.info('preset saved')

lookDict = loadPreset(path=r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib\teste2')
logger.debug(lookDict)
oldShadersList =set()
for ns in lookDict:
    assignList = lookDict[ns]['assign']
    for obj, shaderName in assignList.iteritems():
        path = r'D:\JOBS\PIPELINE\pipeExemple\publishes\shaderLib'
        presetName = 'teste2'
        shaderFullPath = os.path.join (path, 'shaders', ns, shaderName + '.ma')
        nodeList = pm.importFile(shaderFullPath, ns=presetName, mnc=True, typ="mayaAscii", rnn=True)
        for node in nodeList:
            nsList = node.namespaceList()
            node.rename(node, presetName+':'+stripNamespace(node.name()))

        SGList = pm.listConnections(presetName + ':' + shaderName, type='shadingEngine')
        if SGList:
            SG = SGList[0]
            oldShader = getObjMaterial(obj)
            pm.sets(obj, e=True, forceElement=SG)
            # guarda a lista de shaders antigos para apagar.
            if oldShader:
                oldShadersList.add(oldShader)