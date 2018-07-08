import pymel.core as pm

def noMultipleUVsets(*arg):
    # Check meshList
    meshList = pm.ls(type='mesh')
    if not meshList:
        return []

    # Check Multiple UV Sets
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        UVsets = pm.polyUVSet(mesh, q=True, allUVSets=True)
        if not UVsets:
            continue

        if len(UVsets) > 1:
            return True


def selMultipleUVsets(*arg):

    # Check meshList
    meshList = pm.ls(type='mesh')

    if not meshList:
        return []

    # Check Multiple UV Sets
    multipleUVsets = []
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        UVsets = pm.polyUVSet(mesh, q=True, allUVSets=True)
        if not UVsets:
            continue
        if len(UVsets) > 1:
            multipleUVsets.append(mesh)

    pm.select(multipleUVsets)


def delMultipleUVsets(*arg):
    # Check meshList
    meshList = pm.ls(type='mesh')
    if not meshList:
        return []

    # Check Multiple UV Sets
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        UVsets = pm.polyUVSet(mesh, q=True, allUVSets=True)
        if not UVsets:
            continue

        if len(UVsets) > 1:
            current = pm.polyUVSet(mesh, q=True, currentUVSet=True)[0]
            if current != UVsets[0]:
                pm.polyUVSet(mesh, copy=True, uvSet=current, nuv=UVsets[0])

            for UV in UVsets[1:]:
                pm.polyUVSet(mesh, delete=True, uvSet=UV)
                pm.delete(mesh, ch=True)


def noMissingUVsets(*arg):
    # Check meshList
    meshList = pm.ls(type='mesh')
    if not meshList:
        return []

    # Check Missing UV Sets
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        uv = mesh.getUVs()[0]

        if not uv:
            return True
    return False


def selMissingUVsets(*arg):
    # Check meshList
    meshList = pm.ls(type='mesh')
    if not meshList:
        return []

    # Check Missing UV Sets
    missingUVsets = []
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        uv = mesh.getUVs()[0]

        if not uv:
            missingUVsets.append(mesh)
    pm.select(cl=True)
    pm.select(missingUVsets)
    # Return Result
    return 'select'


def applyAutomaticUV(*arg):
    # Check meshList
    meshList = pm.ls(type='mesh')
    if not meshList:
        return []

    # Check Missing UV Sets
    for mesh in meshList:
        if mesh.isIntermediate():
            continue

        uv = mesh.getUVs()[0]
        if not uv:
            pm.polyAutoProjection(mesh.faces, ch=0)
    pm.select(cl=True)
    # Return Result
    return 'ok'

# done delete display layers,renderlayers
# done delete history
# done reverse normals
# done freeze transformations
# done delete namespace editor
# done no multiple UVs

# todo delete LockedNodes ( from outliner)
# todo before publish file save in the bounding box
