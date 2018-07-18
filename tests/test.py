import pymel.core as pm
import lcPipe.core.database as database



for ref in refs.itervalues():
    print ref
    print database.referenceInfo(ref)

# todo database.referenceInfo precisa retornar info do cache (alembic Node)
# todo sceneCheck tem q ver se precisa update de cache tmb

def getGeoGroupMembers(geoGroup):
    geosShape = geoGroup.getChildren(allDescendents=True, type='geometryShape')
    geos = [x.getParent() for x in geosShape]
    return geos

def getAllConnectedAlembic (ref):
    alembicList = pm.ls(type='AlembicNode')
    if not alembicList:
        print 'there is no cache assigned'
        return
    connectedAlembic = []
    for alembic in alembicList:
            alembicConnections = alembic.connections(s=False, type='transform')
            geos = getGeoGroupMembers(geoGrp)
            print alembicConnections
            print geos
            connectedGeos = []
            for x in alembicConnections:
                if x in geos:
                    #return alembic
                    # verificar se so uma conexao e suficiente para definir q o alembic esta nessa ref.
                    connectedGeos.append(x)
            if connectedGeos:
                connectedAlembic.append(alembic)
    return connectedAlembic


def getConnectedAlembic (ref):
    alembicList = pm.ls(type='AlembicNode')
    if not alembicList:
        print 'there is no cache assigned'
        return
    connectedAlembic = []
    for alembic in alembicList:
            alembicConnections = alembic.connections(s=False, type='transform')
            geos = getGeoGroupMembers(geoGrp)
            print alembicConnections
            print geos
            connectedGeos = []
            for x in alembicConnections:
                if x in geos:
                    return alembic
    return

refs = pm.getReferences()
print refs
for ref in refs.itervalues():
    print ref
    refN = ref.refNode
    geoGrp = pm.PyNode(ref.namespace + ':geo_group')
    print getGeoGroupMembers(geoGrp)


x = getConnectedAlembic(ref)
y = x.getAttr('abc_File')
print y

reload (database)
refs = pm.getReferences()
print refs
for ref in refs.itervalues():
    print database.referenceInfo(ref)