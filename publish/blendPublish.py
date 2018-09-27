
import pymel.core as pm
import logging
logger = logging.getLogger(__name__)


##################################################

def geosInsideBsbGroup():
    geoGrpErr = False
    geoGrps = pm.ls('bsp_group', r=True)

    if geoGrps:
        geoGrp = geoGrps[0]
    else:
        logger.debug('bsp_group doesnt exist on this scene')
        geoGrpErr = True
        return geoGrpErr

    geos = pm.ls(type='surfaceShape')

    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.isChildOf(geoGrp):
            geoGrpErr = True
            logger.debug('some geos outside bsp_group')
            return geoGrpErr

    return geoGrpErr


def fixBspGroup(*args):
    bspGrps = pm.ls('bsp_group', r=True)

    if bspGrps:
        bspGrp = bspGrps[0]
    else:
        logger.debug('bsp_group doesnt exist on this scene')
        bspGrp = pm.group(em=True, n='bsp_group')

    geos = pm.ls(type='surfaceShape')
    for geo in geos:

        if geo.isIntermediate():
            continue

        obj = geo.listRelatives(p=True, type='transform')[0]

        if not obj.isChildOf(bspGrp):
            obj.root().setParent(bspGrp)

    geoGrp = pm.ls('geo_group', r=True)
    pm.delete(geoGrp)

    return 'ok'