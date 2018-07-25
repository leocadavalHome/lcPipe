import copy

import pymel.core as pm
import os.path
from lcPipe.core import database


# done fazer o check de versoes ler xlo e caches
# version updated

def checkVersions():
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')

    if currentProject != projName:
        print 'ERROR checkVersions: This file is from a project different from the current project'

    itemMData = database.getItemMData(fromScene=True)
    components = itemMData['components']

    for component_ns, component in components.iteritems():
        if component_ns == 'cam':
            # todo tratar versoes da camera
            continue

        if component['assembleMode'] == 'reference':
            componentMData = database.getItemMData(code=component['code'], task=component['task'], itemType=component['type'])

        elif component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task='xlo', itemType=component['type'])

        if not componentMData:
            print 'checkVersions: missing data for %s : %s %s' \
                  % (component_ns, component['task'], component['code'])
            print 'ignoring...'
            continue

        if componentMData['publishVer'] == 0:
            print 'checkVersions: reference %s not yet published!!' \
                  % (component_ns + ':' + component['task'] + component['code'])
            continue

        if component['ver'] != componentMData['publishVer']:
            if component['updateMode'] == 'last':
                print 'checkVersions: reference %s version updated from %d to %d' %\
                      ((component_ns + ':' + component['task'] + component['code']), component['ver'], componentMData['publishVer'])

                component['ver'] = componentMData['publishVer']

            else:
                print 'checkVersions: reference %s version fixed to %d' %\
                      ((component_ns + ':' + component['task'] + component['code']), component['ver'])
                component['ver'] = int(component['updateMode'])

        else:
            print 'checkVersions: reference %s version ok' % (component_ns + ':' + component['task'] + component['code'])

        source = [x for x in itemMData['source'].itervalues()][0]
        sourceMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

        if not sourceMData:
            print 'checkVersions: missing data for %s : %s %s. Ignoring...' \
                  % (component_ns, component['task'], component['code'])
            continue

        if 'caches' in sourceMData:
            print 'checkVersions: This asset has caches'
            cache_ns = component_ns
            cache = sourceMData['caches'][cache_ns]

            if cache['cacheVer'] == 0:
                print 'checkVersions: Cache not yet published!!'
                continue

            if component['cacheVer'] != cache['cacheVer']:
                print 'checkVersions: Cache %s version updated from %d to %d'\
                      % ((component_ns + ':' + component['task'] + component['code']), component['cacheVer'], cache['cacheVer'])
                component['cacheVer'] = cache['cacheVer']

            else:
                print 'checkVersions: cache %s version ok' % (component_ns + ':' + component['task'] + component['code'])

    x = database.putItemMData(itemMData)


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


def addRef(itemMData=None, refToAdd=None):
    components = itemMData['components']

    for component_ns in refToAdd:
        component = components[component_ns]

        if component['assembleMode'] == 'reference' or component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])
            ver = 'v%03d_' % component['ver']
            path = database.getPath(componentMData, dirLocation='publishLocation')
            componentPath = os.path.join(path[0], ver + path[1])
            pm.createReference(componentPath, namespace=component_ns)


def addCache(itemMData=None, cacheToAdd=None):
    components = itemMData['components']

    for cache_ns in cacheToAdd:
        component = components[cache_ns]

        source = [x for x in itemMData['source'].itervalues()][0]
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


def updateRefVersion(itemMData=None, refOnSceneList=None, refToVerUpdate=None):
    components = itemMData['components']

    for component_ns in refToVerUpdate:
        ref = refOnSceneList[component_ns]
        component = components[component_ns]

        if component['assembleMode'] != 'reference' or component['assembleMode'] != 'xlo':
            print 'assemble mode not reference or xlo'
            return

        if component['assembleMode'] == 'reference':
            componentMData = database.getItemMData(code=component['code'], task=component['task'], itemType=component['type'])

        elif component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task='xlo', itemType=component['type'])

        ver = 'v%03d_' % component['ver']
        path = database.getPath(componentMData, dirLocation='publishLocation')
        componentPath = os.path.join(path[0], ver + path[1])
        ref.replaceWith(componentPath)


def updateCacheVersion(itemMData=None, refOnSceneList=None, cacheToUpdate=None):
    components = itemMData['components']
    print 'update caches'
    for cache_ns in cacheToUpdate:
        print cache_ns
        ref = refOnSceneList[cache_ns]
        component = components[cache_ns]

        source = [x for x in itemMData['source'].itervalues()][0]
        componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

        path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
        cachePath = os.path.join(*path)
        cache = componentMData['caches'][cache_ns]
        ver = 'v%03d_' % cache['cacheVer']
        cacheName = database.templateName(cache) + '_' + cache_ns
        cacheFileName = ver + cacheName + '.abc'
        cacheFullPath = os.path.join(cachePath, cacheFileName)
        print component['assembleMode']
        if component['assembleMode'] == 'cache':
            print 'cache'
            ref.replaceWith(cacheFullPath)
        elif component['assembleMode'] == 'xlo':
            print 'xlo cache'
            pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')


def delRef(refOnSceneList=None, refToDelete=None):
    for ns in refToDelete:
        ref = refOnSceneList[ns]
        print 'WARNING: Removing reference %s' % os.path.basename(ref.path)
        ref.remove()


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

    hasRefsOrCaches = [x for x in components if
                       (components[x]['assembleMode'] == 'reference' or components[x]['assembleMode'] == 'cache' or
                        components[x]['assembleMode'] == 'xlo')]

    if not hasRefsOrCaches:
        print 'WARNING sceneCheck: no reference, xlo or cache found'
        return
    print 'sceneCheck: %s ' % hasRefsOrCaches
    updated = True

    # get reference list and components on i
    refOnSceneList = pm.getReferences()
    # Check consistency:

    ToAdd = [x for x in components if x not in refOnSceneList]
    refToAdd = [x for x in ToAdd if
                components[x]['assembleMode'] == 'reference' or components[x]['assembleMode'] == 'xlo']

    cacheToAdd = [x for x in ToAdd if
                  components[x]['assembleMode'] == 'cache' or components[x]['assembleMode'] == 'xlo']

    print 'sceneCheck: refs to add %s ' % refToAdd
    print 'sceneCheck: caches to add %s ' % cacheToAdd

    if refToAdd:
        mode = 'add'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToAdd, mode))
        updated = False

        if x != 'Abort':
            refToAdd = x.split(',')
            addRef(itemMData=itemMData, refToAdd=refToAdd)
            updated = False

    if cacheToAdd:
        mode = 'add'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(cacheToAdd, mode))
        updated = False

        if x != 'Abort':
            cacheToAdd = x.split(',')
            addCache(itemMData=itemMData, cacheToAdd=cacheToAdd)
            updated = False

    refToDelete = [x for x in refOnSceneList if x not in components]
    print 'sceneCheck: refs to delete  %s ' % refToDelete

    if refToDelete:
        mode = 'delete'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToDelete, mode))
        updated = False

        if x != 'Abort':
            refToDelete = x.split(',')
            delRef(refOnSceneList=refOnSceneList, refToDelete=refToDelete)
            updated = False

    componentsForUpdate = [x for x in components if x not in refToAdd and x not in refToDelete]
    refToVerUpdate = [x for x in componentsForUpdate if
                      components[x]['ver'] != database.referenceInfo(refOnSceneList[x])['ver']]

    cacheToUpdate1 = [x for x in componentsForUpdate if 'cacheVer' in components[x]]

    cacheToUpdate2 = [x for x in cacheToUpdate1 if
                      components[x]['cacheVer'] != database.referenceInfo(refOnSceneList[x])['cacheVer']]

    print 'sceneCheck: refs to update  %s ' % refToVerUpdate
    print 'sceneCheck: caches to update  %s ' % cacheToUpdate2

    if refToVerUpdate:
        mode = 'update Version'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToVerUpdate, mode))
        updated = False

        if x != 'Abort':
            refToVerUpdate = x.split(',')
            updateRefVersion(itemMData=itemMData, refOnSceneList=refOnSceneList, refToVerUpdate=refToVerUpdate)

    if cacheToUpdate2:
        mode = 'update Version'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(cacheToUpdate2, mode))
        updated = False

        if x != 'Abort':
            cacheToUpdate2 = x.split(',')
            updateCacheVersion(itemMData=itemMData, refOnSceneList=refOnSceneList, cacheToUpdate=cacheToUpdate2)

    if updated:
        print 'Scene References OK!!'
        confirmPopUp('Scene References OK!!')


# add ref


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
