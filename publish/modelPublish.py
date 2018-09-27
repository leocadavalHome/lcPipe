import unicodedata

import maya.mel as mel
import pymel.core as pm
import pymel.core.datatypes as dt
import logging
logger = logging.getLogger(__name__)

## Model
def unlockNormals():
    geos = pm.ls(type='mesh')
    locked = False

    for geo in geos:
        if geo.isIntermediate():
            continue

        for geoIndex in range(geo.numNormals() - 1):
            x = geo.isNormalLocked(geoIndex)

            if x:
                locked = True
                break

    return locked


def selectUnlockNormals(*args):
    pm.select(cl=True)
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        for geoIndex in range(geo.numNormals() - 1):
            x = geo.isNormalLocked(geoIndex)

            if x:
                obj = geo.listRelatives(p=True, type='transform')[0]
                pm.select(obj, add=True)

    return 'select'


def fixNormals(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:
        if geo.isIntermediate():
            continue

        pm.polyNormalPerVertex(geo + '.vtx[*]', unFreezeNormal=True)

    return 'ok'


#########################################

def noNonManifold():
    geos = pm.ls(type='mesh')
    hasNMfold = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')
        p = pm.polyInfo(obj, nme=True, nmv=True)

        if p:
            hasNMfold = True
            break

    return hasNMfold


def cleanNonManifold(*args):
    mel.eval(
        'polyCleanupArgList 3 { "1","1","0","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","1","0" }')
    pm.selectMode(object=True)
    pm.select(cl=True)

    return 'ok'


def selectNonManifold(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')
        p = pm.polyInfo(obj, nme=True, nmv=True)

        if p:
            pm.select(p)

    return 'select'


######################################

def noLaminaFaces():
    geos = pm.ls(type='mesh')
    hasLamina = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')
        p = pm.polyInfo(obj, lf=True)

        if p:
            hasLamina = True
            break

    return hasLamina


def cleanLaminaFaces(*args):
    mel.eval(
        'polyCleanupArgList 3 { "1","1","0","0","0","0","0","0","0","1e-005","0","1e-005","0","1e-005","0","-1","1" }')
    pm.selectMode(object=True)
    pm.select(cl=True)

    return 'ok'


def selectLaminaFaces(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')
        p = pm.polyInfo(obj, lf=True)

        if p:
            pm.select(p)

    return 'select'


##################################

def noConstructionHistory():
    geos = pm.ls(type='surfaceShape')
    hasHist = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        hist = geo.history()

        hist = [x for x in hist if not x == geo]
        hist = [x for x in hist if not (pm.objectType(x, isa='groupId') or pm.objectType(x, isa='shadingEngine')
                                        or pm.objectType(x, isa='shadingDependNode'))]

        if hist:
            hasHist = True
            break

    return hasHist


def deleteHistory(*args):
    try:
        geos = pm.ls(type='surfaceShape')
        pm.delete(geos, ch=True)
    except:
        return

    return 'ok'


##################################

def duplicatedNames():
    geos = pm.ls(type='mesh')
    nameErr = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if '|' in obj.name():
            nameErr = True
            break

    return nameErr


def fixDuplicatedNames(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if '|' in obj.name():
            baseName = obj.name().split('|')[-1]
            sameNameObjs = pm.ls(baseName)
            num = len(sameNameObjs)

            for i in range(num):
                try:
                    if baseName.endswith ('_geo'):
                        pm.rename(sameNameObjs[i], baseName + '_%03d_geo' % (i + 1))
                    else:
                        pm.rename(sameNameObjs[i], baseName + '_%03d' % (i + 1))
                except:
                    pm.confirmDialog(title='error', ma='center', message='Problem renaming. Try manually',
                                     button=['OK'], defaultButton='OK', dismissString='OK')
                    return 'error'

    return 'ok'


def selectDuplicatedNames(*args):
    pm.select(cl=True)
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if '|' in obj.name():
            pm.select(obj, add=True)

    return 'select'


#######################################

def validNames():
    nameErr = False
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]
        legalName = unicodedata.normalize('NFKD', obj.name()).encode('ascii', 'ignore')

        if obj.name() != legalName:
            nameErr = True
            break

    return nameErr


def fixInvalidNames(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]
        legalName = unicodedata.normalize('NFKD', obj.name()).encode('ascii', 'ignore')

        if obj.name() != legalName:
            pm.rename(obj, legalName)

    return 'ok'


def selectInvalidNames(*args):
    pm.select(cl=True)
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]
        legalName = unicodedata.normalize('NFKD', obj.name()).encode('ascii', 'ignore')

        if obj.name() != legalName:
            pm.select(obj, add=True)

    return 'select'


###########################################

def validShapeNames():
    geos = pm.ls(type='mesh')
    nameErr = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if geo.name() != obj.name() + 'Shape':
            nameErr = True
            break

    return nameErr


def fixShapeNames(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]
        if geo.name() != obj.name() + 'Shape':
            try:
                pm.rename(geo, obj.name() + 'Shape')
            except:
                pm.confirmDialog(title='error', ma='center', message='Problem renaming. Try manually', button=['OK'],
                                 defaultButton='OK', dismissString='OK')
                return 'error'
    return 'ok'


def selectInvalidShapeNames(*args):
    pm.select(cl=True)
    geos = pm.ls(type='mesh')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if geo.name() != obj.name() + 'Shape':
            pm.select(obj, add=True)

    return 'select'


################################################

def noIntermediateShapes():
    geos = pm.ls(type='mesh')
    nameErr = False

    for geo in geos:
        if geo.isIntermediate():
            cntWMAux = pm.connectionInfo(geo + '.worldMesh[0]', isSource=True)

            if not cntWMAux:
                nameErr = True
                break

    return nameErr


def deleteIntermediateShapes(*args):
    geos = pm.ls(type='mesh')

    for geo in geos:
        if geo.isIntermediate():
            cntWMAux = pm.connectionInfo(geo + '.worldMesh[0]', isSource=True)
            if not cntWMAux:
                pm.delete(geo)

    return 'ok'


def selectIntermediateShapes(*args):
    pm.select(cl=True)
    geos = pm.ls(type='mesh')

    for geo in geos:
        if geo.isIntermediate():
            cntWMAux = pm.connectionInfo(geo + '.worldMesh[0]', isSource=True)

            if not cntWMAux:
                obj = geo.listRelatives(p=True, type='transform')[0]
                pm.select(obj, add=True)

    return 'select'


##################################################

def noShaders():
    geos = pm.ls(type='surfaceShape')
    shaderErr = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        SGGeos = pm.listConnections(geo, type='shadingEngine')

        for SGGeo in SGGeos:
            if SGGeo.name() != 'initialShadingGroup':
                print SGGeo.name()
                shaderErr = True

    return shaderErr


def fixShaders():
    geos = pm.ls(type='surfaceShape')
    inicialSG = pm.PyNode('initialShadingGroup')

    for geo in geos:
        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]
        SGGeos = pm.listConnections(geo, type='shadingEngine')
        print SGGeos
        for SGGeo in SGGeos:
            if SGGeo.name() != 'initialShadingGroup':
                 x = pm.sets(inicialSG,e=True, forceElement=geo)
                 print x
    return 'ok'


def selectShaderedObjs(*args):
    pm.select(cl=True)
    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        SGGeos = pm.listConnections(geo, type='shadingEngine')

        for SGGeo in SGGeos:
            if SGGeo.name() != 'initialShadingGroup':
                obj = geo.listRelatives(p=True, type='transform')[0]
                pm.select(obj, add=True)

    return 'select'


##################################################

def geosInsideGeoGroup():
    geoGrpErr = False
    geoGrps = pm.ls('geo_group', r=True)

    if geoGrps:
        geoGrp = geoGrps[0]
    else:
        logger.debug('geo_group doesnt exist on this scene')
        geoGrpErr = True
        return geoGrpErr

    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.isChildOf(geoGrp):
            geoGrpErr = True
            logger.debug('some geos outside geo_group')
            return geoGrpErr

    return geoGrpErr


def fixGeoGroup(*args):
    geoGrps = pm.ls('geo_group', r=True)

    if geoGrps:
        geoGrp = geoGrps[0]
    else:
        logger.debug ('geo_group doesnt exist on this scene')
        geoGrp = pm.group(em=True, n='geo_group')

    geos = pm.ls(type='surfaceShape')
    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.isChildOf(geoGrp):
            obj.root().setParent(geoGrp)

    return 'ok'


###################################################

def noNameSpaces():
    pm.namespace(set=':')
    nameSpacesInScene = pm.namespaceInfo(listOnlyNamespaces=True, recurse=True, absoluteName=True)
    nameSpacesInScene.remove(':UI')
    nameSpacesInScene.remove(':shared')

    if nameSpacesInScene:
        return True

    return False


def deleteNameSpaces(*args):
    pm.namespace(set=':')
    nameSpacesInScene = pm.namespaceInfo(listOnlyNamespaces=True, recurse=True, absoluteName=True)
    nameSpacesInScene.remove(':UI')
    nameSpacesInScene.remove(':shared')

    try:
        for i in range(len(nameSpacesInScene) - 1, -1, -1):
            pm.namespace(moveNamespace=[nameSpacesInScene[i], ':'], force=True)
            pm.namespace(removeNamespace=nameSpacesInScene[i])

    except:
        pm.confirmDialog(title='error', ma='center', message='Problem deleting namespaces. Try manually', button=['OK'],
                         defaultButton='OK', dismissString='OK')
        return 'erro'

    return 'ok'


# no display Layers
def noDisplayLayers(*arg):
    layersInScene = pm.ls(type='displayLayer')

    if len(layersInScene) > 1:
        return True


def delDisplayLayers(*arg):
    layersInScene = pm.ls(type='displayLayer')

    if layersInScene[1:]:
        try:
            pm.delete(layersInScene[1:])
        except:
            print 'Erro ao apagar Layers'
            raise

    return 'ok'


# geo has _geo sulfix
def geoHasSulfix(*args):
    geos = pm.ls(type='surfaceShape')
    nameErr = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().endswith('_geo'):
            nameErr = True
            break

    return nameErr


def selGeoNoSulfix(*args):
    pm.select(cl=True)
    geos = pm.ls(type='surfaceShape')
    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().endswith('_geo'):
            pm.select(obj, add=True)

    return 'select'


def fixGeoSulfix(*args):
    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().endswith('_geo'):
            pm.rename(obj, obj.name() + '_geo')

    return 'ok'


# grp has _grp sulfix
def grpHasSulfix(*args):
    transforms = pm.ls(type='transform')
    nameErr = False

    for trans in transforms:

        objShape = trans.getShape()

        if not objShape:
            if trans.name() == 'geo_group':
                continue

            if not trans.name().endswith('_grp'):
                nameErr = True
                break

    return nameErr


def selGrpNoSulfix(*args):
    pm.select(cl=True)
    transforms = pm.ls(type='transform')

    for trans in transforms:

        objShape = trans.listRelatives(s=True)

        if not objShape:
            if trans.name() == 'geo_group':
                continue

            if not trans.name().endswith('_grp'):
                pm.select(trans, add=True)

    return 'select'


def fixGrpSulfix(*args):
    transforms = pm.ls(type='transform')

    for trans in transforms:

        objShape = trans.listRelatives(s=True)

        if not objShape:
            if trans.name() == 'geo_group':
                continue

            if not trans.name().endswith('_grp'):
                pm.rename(trans, trans.name() + '_grp')

    return 'ok'


# not lowercase
def islowercase(*args):
    geos = pm.ls(type='surfaceShape')
    nameErr = False

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().islower():
            nameErr = True
            break

    if nameErr:
        return True

    transforms = pm.ls(type='transform')

    for trans in transforms:

        objShape = trans.listRelatives(s=True)

        if not objShape:

            if not trans.name().islower():
                nameErr = True
                break

    return nameErr


def fixNotLowercase(*args):
    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().islower():
            pm.rename(obj, obj.name().lower())

    transforms = pm.ls(type='transform')
    for trans in transforms:

        objShape = trans.listRelatives(s=True)

        if not objShape:
            pm.rename(trans, trans.name().lower())

    return 'ok'


def selNotLowercase(*args):
    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.name().islower():
            pm.select(obj, add=True)

    transforms = pm.ls(type='transform')

    for trans in transforms:

        objShape = trans.listRelatives(s=True)

        if not objShape:
            if not trans.name().endswith('_grp'):
                pm.select(trans, add=True)

    return 'select'


# triangle
def nonQuad(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x0008, size=1)
    pm.polySelectConstraint(disable=True)
    tris = pm.filterExpand(ex=True, sm=34) or []
    # Find N-Gons
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x0008, size=3)
    pm.polySelectConstraint(disable=True)
    ngon = pm.filterExpand(ex=True, sm=34) or []
    pm.select(cl=True)
    if tris or ngon:
        return True


def selNonQuad(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x0008, size=1)
    pm.polySelectConstraint(disable=True)
    tris = pm.filterExpand(ex=True, sm=34) or []
    # Find N-Gons
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x0008, size=3)
    pm.polySelectConstraint(disable=True)
    ngon = pm.filterExpand(ex=True, sm=34) or []
    pm.select(cl=True)
    pm.select(tris, ngon)

    return 'select'


def noHoles(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x0008, h=1)
    pm.polySelectConstraint(disable=True)
    holes = pm.filterExpand(ex=True, sm=34) or []

    pm.select(cl=True)
    if holes:
        return True


def selHoles(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x8000, h=1)
    pm.polySelectConstraint(disable=True)
    holes = pm.filterExpand(ex=True, sm=32) or []
    pm.select(holes)

    return 'select'


def noHardEdges(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x8000, sm=1)
    pm.polySelectConstraint(disable=True)
    hard = pm.filterExpand(ex=True, sm=32) or []
    pm.select(cl=True)
    if hard:
        return True


def selHardEdges(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    pm.select(meshList)
    pm.polySelectConstraint(mode=3, type=0x8000, sm=1)
    pm.polySelectConstraint(disable=True)
    hard = pm.filterExpand(ex=True, sm=32) or []
    pm.select(hard)

    return 'select'


def fixHardEdges(*args):
    meshList = pm.ls(type='surfaceShape')
    if not meshList:
        return []
    # Find Triangles
    for obj in meshList:
        pm.polySoftEdge(obj, a=180, ch=0)

    return 'ok'


def froozenTransforms(*args):
    geos = pm.ls(type='surfaceShape')

    for geo in geos:
        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        matrix = obj.getTransformation()

        zeroed = matrix.isEquivalent(dt.Matrix.identity, tol=1e-10)
        if not zeroed:
            return True


def selNotFroozenTransforms(*args):
    geos = pm.ls(type='surfaceShape')
    notFreezed = []
    for geo in geos:
        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        matrix = obj.getTransformation()

        zeroed = matrix.isEquivalent(dt.Matrix.identity, tol=1e-10)
        if not zeroed:
            notFreezed.append(obj)

    pm.select(notFreezed)
    return 'select'


def freezeTransforms(*args):
    geos = pm.ls(type='surfaceShape')

    for geo in geos:
        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        matrix = obj.getTransformation()

        zeroed = matrix.isEquivalent(dt.Matrix.identity, tol=1e-10)
        if not zeroed:
            pm.makeIdentity(obj, t=True, r=True, s=True)

    return 'ok'


def geoGroupPivotZeroed(*args):
    geoGrps = pm.ls('geo_group', r=True)

    if geoGrps:
        geoGrp = geoGrps[0]
    else:
        logger.debug ('geo_group doesnt exist on this scene')
        return True

    rp = geoGrp.getRotatePivot()
    sp = geoGrp.getScalePivot()

    zeroPoint = dt.Point()
    if rp != zeroPoint or sp != zeroPoint:
        return True


def resetGeoGroupPivot(*args):
    geoGrps = pm.ls('geo_group', r=True)

    if geoGrps:
        geoGrp = geoGrps[0]
    else:
        logger.debug ('geo_group doesnt exist on this scene')
        return True

    geoGrp.zeroTransformPivots()

    return 'ok'


def noVertexTransforms(*args):
    # Check meshList
    meshList = pm.ls(type='mesh')

    if not meshList:
        return []
    try:
        # Check Vertex Transforms
        for meshShape in meshList:
            if meshShape.isIntermediate():
                continue
            # Check NonZero Values
            # if [i for sublist in mc.getAttr(meshShape+'.pnts[*]') for i in sublist if abs(i) > 0.0000000001]:
            hasTrasnforms = meshShape.getAttr('pnts', mi=True)
            if hasTrasnforms:
                if len(hasTrasnforms) > 1:
                    return True
    except:
        logger.info('vertex test got an error')

    return False

def freezeVertices(*args):
    meshes = pm.ls(type='mesh')
    if not meshes:
        return []

    for mesh in meshes:
        if mesh.isIntermediate():
            continue
        try:
            # Freeze Vertices
            hasTrasnforms = mesh.getAttr('pnts', mi=True)
            if len(hasTrasnforms) > 1:
                pm.polyMoveVertex(mesh)
                pm.delete(mesh, ch=True)
                pm.select(cl=True)
        except:
            logger.info('freeze vertices fail')
            return 'fail'
    # Return Result
    return 'ok'


# done Check all geometry ends with _geo
# done Check all groups end with _grp
# done Check all geometries and groups starts with lowercase
# done Check triangles and faces more than four sides/ cant do fix
# done Check Border Edge (holes?? ok)
# done Check all geometries are Smooth edge
# done Check all transforms are freezed
# done Check Top group node pivot to World 0
# done Check all Vertex are freezed
# done Check Duplicate names  ok
# done Check Namespace ok
# done Check more than one Shape on geometry ok
# done Clear History ok
# done Check Normals ok
# done Check Non manifold Geometry ok
# done Check all shape names are correct ok
