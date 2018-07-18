import copy

import pymel.core as pm
import os.path
from lcPipe.core import database


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


# replace ref
def replaceRef(wrongRef):
    currentProject = database.getCurrentProject()

    projName = pm.fileInfo.get('projectName')
    if currentProject != projName:
        print 'ERROR replaceRef: This file is from a project different from the current project'
        return

    item = database.getItemMData(fromScene=True)
    components = item['components']
    refOnSceneList = pm.getReferences()

    for component_ns in wrongRef:
        ref = refOnSceneList[component_ns]
        component = components[component_ns]

        if component['assembleMode'] == 'reference':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])

            if componentMData['publishVer'] == 0:
                print 'Component %s not yet published!!' % (component_ns + ':' + component['task'] + component['code'])
                continue

            else:
                version = 'v%03d_' % componentMData['publishVer']

            path = database.getPath(componentMData, dirLocation='publishLocation')
            componentPath = os.path.join(path[0], version + path[1])
            ref.replaceWith(componentPath)

        elif component['assembleMode'] == 'cache':
            source = [x for x in item['source'].itervalues()][0]
            componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

            path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
            # name=path[1]
            cachePath = os.path.join(*path)
            # pm.namespace( set=':'+componentMData['task'])

            cache_ns = component_ns
            cache = componentMData['caches'][cache_ns]

            if cache['cacheVer'] == 0:
                print 'Component not yet published!!'
                continue

            else:
                ver = 'v%03d_' % cache['ver']

            cacheName = database.templateName(cache) + '_' + cache_ns
            cacheFileName = ver + cacheName + '.abc'
            cacheFullPath = os.path.join(cachePath, cacheFileName)

            ref.replaceWith(cacheFullPath)


def delRef(refToDelete):
    refOnSceneList = pm.getReferences()

    for ns in refToDelete:
        ref = refOnSceneList[ns]
        print 'WARNING: Removing reference %s' % os.path.basename(ref.path)
        ref.remove()


# add ref
def addRef(refToAdd):
    currentProject = database.getCurrentProject()

    projName = pm.fileInfo.get('projectName')
    if currentProject != projName:
        print 'ERROR addRef: This file is from a project different from the current project'
        return

    item = database.getItemMData(fromScene=True)
    components = item['components']

    for component_ns in refToAdd:
        component = components[component_ns]

        if component['type'] == 'cache':
            source = [x for x in item['source'].itervalues()][0]
            componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

            path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
            cachePath = os.path.join(*path)

            pm.namespace(set=':' + componentMData['task'])

            cache_ns = component_ns
            cache = componentMData['caches'][cache_ns]

            if cache['cacheVer'] == 0:
                print 'Component not yet published!!'
                continue

            else:
                ver = 'v%03d_' % cache['ver']

            cacheName = database.templateName(cache) + '_' + cache_ns
            cacheFileName = ver + cacheName + '.abc'
            cacheFullPath = os.path.join(cachePath, cacheFileName)
            pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True, groupName='geo_group',
                               type='Alembic')
            pm.rename(componentMData['task'] + ':geo_group', cache_ns + ':geo_group')

            pm.namespace(set=':')

        else:
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])

            if componentMData['publishVer'] == 0:
                print 'Component %s not yet published!!' % (component_ns + ':' + component['task'] + component['code'])
                continue

            else:
                version = 'v%03d_' % componentMData['publishVer']

                # use files
            path = database.getPath(componentMData, dirLocation='publishLocation')
            componentPath = os.path.join(path[0], version + path[1])

            # import
            if component['assembleMode'] == 'import':
                pm.importFile(componentPath, defaultNamespace=True)

                # reference
            elif component['assembleMode'] == 'reference':
                ns = component_ns
                pm.createReference(componentPath, namespace=ns)

            # copy from another scene
            elif component['assembleMode'] == 'copy':
                pm.openFile(componentPath, force=True)
                item['source'] = copy.deepcopy(item['components'])
                item['components'] = copy.deepcopy(componentMData['components'])  # pm.saveAs(sceneFullPath)


# version updated
def checkVersions():
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')

    if currentProject != projName:
        print 'ERROR checkVersions: This file is from a project different from the current project'
        return

    itemMData = database.getItemMData(fromScene=True)
    components = itemMData['components']

    for component_ns, component in components.iteritems():
        if component['assembleMode'] == 'reference' or component['assembleMode'] == 'xlo':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])
            if not componentMData:
                print 'missing data for %s : %s %s' % (component_ns, component['task'], component['code'])
                print 'ignoring...'
                continue

            if componentMData['publishVer'] == 0:
                print 'Component %s not yet published!!' % (component_ns + ':' + component['task'] + component['code'])
                continue

            if component['updateMode'] == 'last':
                component['ver'] = componentMData['publishVer']
                print 'Component %s version updated to %d' % (
                    (component_ns + ':' + component['task'] + component['code']), component['ver'])
            else:
                component['ver'] = int(component['updateMode'])
                print 'Component %s version fixed to %d' % (
                    (component_ns + ':' + component['task'] + component['code']), component['ver'])

        elif component['assembleMode'] == 'cache' or component['assembleMode'] == 'xlo':
            source = [x for x in itemMData['source'].itervalues()][0]
            sourceMData = database.getItemMData(code=source['code'], task=source['task'],
                                                itemType=source['type'])
            if not sourceMData:
                print 'missing data for %s : %s %s' % (component_ns, component['task'], component['code'])
                print 'ignoring...'
                continue

            cache_ns = component_ns
            cache = sourceMData['caches'][cache_ns]

            if cache['cacheVer'] == 0:
                print 'Component not yet published!!'
                continue
            else:
                if component['cacheVer'] != cache['cacheVer']:
                    component['cacheVer'] = cache['cacheVer']
                    print 'Component %s version updated to %d' % (
                        (component_ns + ':' + component['task'] + component['code']), cache['cacheVer'])

                else:
                    print 'Component %s version ok' % (component_ns + ':' + component['task'] + component['code'])

    x = database.putItemMData(itemMData)

# todo implementar updateCacheVersion e possivelmente tirar da outra def.
def updateCacheVersion(cacheToVerUpdata):
    pass

def updateRefVersion(refToVerUpdate):
    currentProject = database.getCurrentProject()

    projName = pm.fileInfo.get('projectName')
    if currentProject != projName:
        print 'ERROR checkVersions: This file is from a project different from the current project'
        return

    item = database.getItemMData(fromScene=True)
    components = item['components']
    refOnSceneList = pm.getReferences()

    for component_ns in refToVerUpdate:
        ref = refOnSceneList[component_ns]
        component = components[component_ns]

        if component['assembleMode'] == 'reference':
            componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                                   itemType=component['type'])

            ver = 'v%03d_' % component['ver']
            path = database.getPath(componentMData, dirLocation='publishLocation')
            componentPath = os.path.join(path[0], ver + path[1])
            ref.replaceWith(componentPath)

        elif component['assembleMode'] == 'cache':
            source = [x for x in item['source'].itervalues()][0]
            componentMData = database.getItemMData(code=source['code'], task=source['task'], itemType=source['type'])

            path = database.getPath(componentMData, dirLocation='cacheLocation', ext='')
            cachePath = os.path.join(*path)
            cache_ns = component_ns
            cache = componentMData['caches'][cache_ns]
            ver = 'v%03d_' % cache['ver']
            cacheName = database.templateName(cache) + '_' + cache_ns
            cacheFileName = ver + cacheName + '.abc'
            cacheFullPath = os.path.join(cachePath, cacheFileName)
            ref.replaceWith(cacheFullPath)


def sceneRefCheck():
    currentProject = database.getCurrentProject()

    projName = pm.fileInfo.get('projectName')
    if currentProject != projName:
        print 'ERROR sceneRefCheck: This file is from a project different from the current project'
        return

    checkVersions()
    # get scene name and item
    item = database.getItemMData(fromScene=True)

    components = item['components']

    hasRefsOrCaches = [x for x in components if
                       (components[x]['assembleMode'] == 'reference' or components[x]['assembleMode'] == 'cache' or
                        components[x]['assembleMode'] == 'xlo')]

    if not hasRefsOrCaches:
        return

    updated = True

    # get reference list and components on i
    refOnSceneList = pm.getReferences()
    # Check consistency:
    refToAdd = [x for x in components if x not in refOnSceneList]

    if refToAdd:
        mode = 'add'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToAdd, mode))
        updated = False

        if x != 'Abort':
            refToAdd = x.split(',')
            addRef(refToAdd)
            updated = False

    refToDelete = [x for x in refOnSceneList if x not in components]

    if refToDelete:
        mode = 'delete'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToDelete, mode))
        updated = False

        if x != 'Abort':
            refToDelete = x.split(',')
            delRef(refToDelete)
            updated = False

    wrongRef = [x for x in components if x not in refToAdd and x not in refToDelete and (
            components[x]['code'] != database.referenceInfo(refOnSceneList[x])['code'] or components[x]['task'] !=
            database.referenceInfo(refOnSceneList[x])['task'])]

    for x in components:
        print database.referenceInfo(refOnSceneList[x])

    if wrongRef:
        mode = 'wrong'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(wrongRef, mode))
        updated = False

        if x != 'Abort':
            wrongRef = x.split(',')
            replaceRef(wrongRef)

    refToVerUpdate = [x for x in components if
                      x not in refToAdd and x not in refToDelete and x not in wrongRef and components[x]['ver'] !=
                      database.referenceInfo(refOnSceneList[x])['ver']]

    if refToVerUpdate:
        mode = 'update Version'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToVerUpdate, mode))
        updated = False

        if x != 'Abort':
            refToVerUpdate = x.split(',')
            updateRefVersion(refToVerUpdate)


# todo implementar updateCacheVersion

    cacheToVerUpdate = [x for x in components if x not in refToAdd
                        and x not in refToDelete and x not in wrongRef
                        and components[x]['cacheVer'] != database.referenceInfo(refOnSceneList[x])['cacheVer']]

    if cacheToVerUpdate:
        mode = 'update Version'
        x = pm.layoutDialog(ui=lambda: refCheckPrompt(refToVerUpdate, mode))
        updated = False

        if x != 'Abort':
            cacheToVerUpdate = x.split(',')
            updateCacheVersion(cacheToVerUpdate)

    if updated:
        print 'Scene References OK!!'
