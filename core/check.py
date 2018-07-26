import pymel.core as pm
import os.path
from core import database


def checkVersions():
    itemMData = database.getItemMData(fromScene=True)
    components = itemMData['components']
    source = [x for x in itemMData['source'].itervalues()][0]
    sourceMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

    for component_ns, component in components.iteritems():
        if component_ns == 'cam':
            # todo tratar versoes da camera
            continue

        if component['assembleMode'] == 'reference':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])

            if not componentMData:
                continue

            components[component_ns] = checkReferenceVersions(component_ns, component, componentMData)

        elif component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task='xlo', itemType=component['type'])

            if not componentMData:
                continue

            components[component_ns] = checkReferenceVersions(component_ns, component, componentMData)
            components[component_ns] = checkCacheVersions(component_ns, components[component_ns], sourceMData)

        elif component['assembleMode'] == 'cache':

            components[component_ns] = checkCacheVersions(component_ns, component, sourceMData)

    database.putItemMData(itemMData)


def sceneRefCheck():
    print 'init checking...'
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')
    if currentProject != projName:
        print 'ERROR sceneRefCheck: This file is from a project different from the current project'
        return

    checkVersions()
    print 'checkVersions ok'

    # get scene name and item
    itemMData = database.getItemMData(fromScene=True)
    components = itemMData['components']

    if not isUpdatable(components):
        return

    refOnSceneList = pm.getReferences()

    toUpdate = [(x + '-> reference to delete') for x in refOnSceneList if x not in components]

    for component_ns, component in components.iteritems():
        refInfo = database.referenceInfo(refOnSceneList[component_ns])

        if component['assembleMode'] == 'reference':
            # procedure de reference
            if component_ns not in refOnSceneList:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> add to scene')

            refInfo = database.referenceInfo(refOnSceneList[component_ns])
            if component['ver'] != refInfo['ver']:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> update %s to %s' % (refInfo['ver'], component['ver']))

        elif component['assembleMode'] == 'xlo':
            # procedimentos de xlo
            if component_ns not in refOnSceneList:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> add xlo to scene')

            if component['ver'] != refInfo['ver']:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> update xlo %s to %s' % (refInfo['ver'], component['ver']))

            if component['cacheVer'] != refInfo['cacheVer']:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> update xlo cache %s to %s' % (refInfo['cacheVer'], component['cacheVer']))

        elif component['assembleMode'] == 'cache':
            # procedimentos de cache
            if component['cacheVer'] != refInfo['cacheVer']:
                # this namespace not yet in the scene, need to add
                toUpdate.append(component_ns + '-> update cache %s to %s' % (refInfo['cacheVer'], component['cacheVer']))

    if toUpdate:
        resp = pm.layoutDialog(ui=lambda: refCheckPrompt(toUpdate, 'change'))
        print resp
    else:
        confirmPopUp('Scene References OK!!')



def checkReferenceVersions(component_ns, component, componentMData):
    if componentMData['publishVer'] == 0:
        print 'checkVersions: reference %s not yet published!!' \
              % (component_ns + ':' + component['task'] + component['code'])
        return component

    if component['ver'] != componentMData['publishVer']:
        if component['updateMode'] == 'last':
            print 'checkVersions: reference %s version updated from %d to %d' % \
                  ((component_ns + ':' + component['task'] + component['code']), component['ver'],
                   componentMData['publishVer'])

            component['ver'] = componentMData['publishVer']

        else:
            print 'checkVersions: reference %s version fixed to %d' % \
                  ((component_ns + ':' + component['task'] + component['code']), component['ver'])
            component['ver'] = int(component['updateMode'])
    else:
        print 'checkVersions: reference %s version ok' % (component_ns + ':' + component['task'] + component['code'])

    return component


def checkCacheVersions(component_ns, component, sourceMData):
    if 'caches' in sourceMData:
        cache_ns = component_ns
        cache = sourceMData['caches'][cache_ns]

        if cache['cacheVer'] == 0:
            print 'checkVersions: Cache not yet published!!'
            return component

        if component['cacheVer'] != cache['cacheVer']:
            print 'checkVersions: Cache %s version updated from %d to %d' \
                  % ((component_ns + ':' + component['task'] + component['code']), component['cacheVer'],
                     cache['cacheVer'])
            component['cacheVer'] = cache['cacheVer']
        else:
            print 'checkVersions: cache %s version ok' % (component_ns + ':' + component['task'] + component['code'])
    else:
        print 'checkVersions: no caches in source!!'

    return component


def confirmPopUp(msg):
    return pm.confirmDialog(title='PopUp', ma='center', message=msg, button=['OK', 'Cancel'], defaultButton='OK',
                            dismissString='Cancel')


def refCheckPrompt(refs, type):
    form = pm.setParent(q=True)
    pm.formLayout(form, e=True, width=300)
    t = pm.text(l='this references are marked to %s' % type)
    t2 = pm.text(l='change selection')
    b3 = pm.button(l='Cancel', c='pm.layoutDialog( dismiss="Abort" )')
    # b2 = pm.button(l='Cancel', c='pm.layoutDialog( dismiss="Cancel" )' )
    b1 = pm.button(l='OK', c=lambda x: changeList())
    cb1 = pm.textScrollList('scrollList', allowMultiSelection=True, si=refs, append=refs)
    spacer = 5
    top = 5
    edge = 5
    pm.formLayout(form, edit=True,
                  attachForm=[(cb1, 'right', edge), (t, 'top', top), (t, 'left', edge), (t, 'right', edge),
                              (t2, 'left', edge), (t2, 'right', edge), (b1, 'left', edge), (b1, 'bottom', edge),
                              (b3, 'bottom', edge), (b3, 'right', edge), (cb1, 'left', edge)],

                  attachNone=[(t, 'bottom')], attachControl=[(cb1, 'top', spacer, t2), (t2, 'top', spacer, t)],
                  attachPosition=[(b1, 'right', spacer, 33), (b3, 'left', spacer, 66)])


def changeList(*args):
    sel = pm.textScrollList('scrollList', q=True, si=True)
    selString = ','.join(sel)
    pm.layoutDialog(dismiss=selString)


def addRef(component_ns, component):
    if component['assembleMode'] == 'reference':
        componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                               itemType=component['type'])
        ver = 'v%03d_' % component['ver']
        path = database.getPath(componentMData, dirLocation='publishLocation')
        componentPath = os.path.join(path[0], ver + path[1])
        pm.createReference(componentPath, namespace=component_ns)


def addCache(cache_ns, component, source):
    componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])
    path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)
    cache = componentMData['caches'][cache_ns]
    ver = 'v%03d_' % cache['cacheVer']

    cacheName = database.templateName(cache) + '_' + cache_ns
    cacheFileName = ver + cacheName + '.abc'
    cacheFullPath = os.path.join(cachePath, cacheFileName)

    if component['assembleMode'] == 'cache':
        pm.createReference(cacheFullPath, namespace=cache_ns)
    elif component['assembleMode'] == 'xlo':
        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')


def updateRefVersion(component_ns, component, ref):
    componentMData = database.getItemMData(code=component['code'], task=component['task'],itemType=component['type'])

    # componentMData = database.getItemMData(code=component['code'], task='xlo', itemType=component['type'])

    ver = 'v%03d_' % component['ver']
    path = database.getPath(componentMData, dirLocation='publishLocation')
    componentPath = os.path.join(path[0], ver + path[1])

    ref.replaceWith(componentPath)


def updateCacheVersion(cache_ns, component, source,  ref):
    componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])
    path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)
    cache = componentMData['caches'][cache_ns]
    ver = 'v%03d_' % cache['cacheVer']
    cacheName = database.templateName(cache) + '_' + cache_ns
    cacheFileName = ver + cacheName + '.abc'
    cacheFullPath = os.path.join(cachePath, cacheFileName)

    if component['assembleMode'] == 'cache':
        ref.replaceWith(cacheFullPath)

    elif component['assembleMode'] == 'xlo':
        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')


def delRef(refOnSceneList=None, refToDelete=None):
    for ns in refToDelete:
        ref = refOnSceneList[ns]
        print 'WARNING: Removing reference %s' % os.path.basename(ref.path)
        ref.remove()


def isUpdatable(components):
    hasRefsOrCaches = [x for x in components if
                       (components[x]['assembleMode'] == 'reference' or components[x]['assembleMode'] == 'cache' or
                        components[x]['assembleMode'] == 'xlo')]

    if not hasRefsOrCaches:
        print 'WARNING sceneCheck: no reference, xlo or cache found'
        return False

    return True


# replace ref
def replaceRef(wrongRef):
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')

    if currentProject != projName:
        print 'ERROR replaceRef: This file is from a project different from the current project'
        return

    itemMData = database.getItemMData(fromScene=True)
    components = itemMData['components']
    refOnSceneList = pm.getReferences()

    for component_ns in wrongRef:
        ref = refOnSceneList[component_ns]
        component = components[component_ns]

        if component['assembleMode'] == 'reference' or component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])
            if componentMData['publishVer'] == 0:
                print 'Component %s not yet published!!' % (component_ns + ':' + component['task'] + component['code'])
                # todo adicionar opcao para apagar a ref
                continue
            else:
                version = 'v%03d_' % componentMData['publishVer']

            path = database.getPath(componentMData, dirLocation='publishLocation')
            componentPath = os.path.join(path[0], version + path[1])
            ref.replaceWith(componentPath)

        elif component['assembleMode'] == 'cache':
            source = [x for x in itemMData['source'].itervalues()][0]
            componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

            path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
            cachePath = os.path.join(*path)
            # pm.namespace( set=':'+componentMData['task'])

            cache_ns = component_ns
            cache = componentMData['caches'][cache_ns]

            if cache['cacheVer'] == 0:
                print 'Component not yet published!!'
                continue

            else:
                ver = 'v%03d_' % cache['cacheVer']

            cacheName = database.templateName(cache) + '_' + cache_ns
            cacheFileName = ver + cacheName + '.abc'
            cacheFullPath = os.path.join(cachePath, cacheFileName)

            ref.replaceWith(cacheFullPath)
# todo implementar updateCacheVersion
# todo fazer o xlo
# todo implementar updateCacheVersion e possivelmente tirar da outra def.
