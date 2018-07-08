import pymel.core as pm
import os.path
from lcPipe.core import database
import copy

reload(database)


def referenceCache(componentMData):
    path = database.getPath(componentMData, location='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    for cache_ns, cacheMData in componentMData['caches'].iteritems():
        if cacheMData['ver'] == 0:
            print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
            continue

        ver = 'v%03d_' % cacheMData['ver']
        cacheName = database.templateName(cacheMData) + '_' + cache_ns
        cacheFileName = ver + cacheName + '.abc'
        cacheFullPath = os.path.join(cachePath, cacheFileName)

        pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True, groupName='geo_group',
                           type='Alembic')


def importCaches(componentMData):
    path = database.getPath(componentMData, location='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    for cache_ns, cacheMData in componentMData['caches'].iteritems():
        if cacheMData['ver'] == 0:
            print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
            continue

        ver = 'v%03d_' % cacheMData['ver']
        cacheName = database.templateName(cacheMData) + '_' + cache_ns
        cacheFileName = ver + cacheName + '.abc'
        cacheFullPath = os.path.join(cachePath, cacheFileName)

        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')

    return


def referenceXlos(componentMData):
    version = 0
    for ns, xlo in componentMData['components'].iteritems():
        xloMData = database.getItemMData(task='xlo', code=xlo['code'], itemType=xlo['type'])
        path = database.getPath(xloMData, location='publishLocation')

        for xlo_ns, xloMData in componentMData['caches'].iteritems():
            if xloMData['ver'] == 0:
                print 'Component %s not yet published!!' % (xlo_ns + ':' + xloMData['task'] + xloMData['code'])
                # parcial = True
                continue

            else:
                version = 'v%03d_' % xloMData['publishVer']

        xloPath = os.path.join(path[0], version + path[1])

        pm.importFile(xloPath, namespace=ns)


def assemble(itemType, task, code):
    empty = True
    parcial = False
    fromSource = False

    print 'start assembling'

    # read from database
    collection = database.getCollection(itemType)
    itemMData = database.getItemMData(task=task, code=code, itemType=itemType)

    if not itemMData:
        print 'ERROR: No metadata for this item'
        return

    pm.newFile(f=True, new=True)

    if 'source' in itemMData:
        fromSource = True
        itemComponents = itemMData['source']
    else:
        itemComponents = itemMData['components']

    for component_ns, component in itemComponents.iteritems():
        # read components item
        componentMData = database.getItemMData(code=component['code'], task=component['task'],
                                               itemType=component['type'])

        if not componentMData:
            print 'ignoring...'
            continue

        if componentMData['publishVer'] == 0:
            print 'Component %s not yet published!!' % (component_ns + ':' + component['task'] + component['code'])
            parcial = True
            continue

        path = database.getPath(componentMData, location='publishLocation')
        version = 'v%03d_' % componentMData['publishVer']
        componentPath = os.path.join(path[0], version + path[1])

        empty = False

        # use caches
        if component['assembleMode'] == 'cache':

            pm.namespace(add=component_ns)
            pm.namespace(set=component_ns)

            referenceCache(componentMData)

            if not fromSource:
                itemMData['source'] = copy.deepcopy(itemMData['components'])

            itemMData['components'] = copy.deepcopy(componentMData['caches'])

            pm.namespace(set=':')

        # xlo
        elif component['assembleMode'] == 'xlo':
            referenceXlos(componentMData)
            importCaches(componentMData)

            if not fromSource:
                itemMData['source'] = copy.deepcopy(itemMData['components'])

            itemMData['components'] = copy.deepcopy(componentMData['components'])
            # pm.namespace( set=':')

        # import
        elif component['assembleMode'] == 'import':
            pm.importFile(componentPath, defaultNamespace=True)

            # reference
        elif component['assembleMode'] == 'reference':
            ns = component_ns
            pm.createReference(componentPath, namespace=ns)

        # copy from another scene
        elif component['assembleMode'] == 'copy':
            pm.openFile(componentPath, force=True)

            if not fromSource:
                itemMData['source'] = copy.deepcopy(itemMData['components'])

            itemMData['components'] = copy.deepcopy(componentMData['components'])
            # pm.renameFile ( sceneFullPath )

    # update infos on scene and database
    if not empty or not itemComponents:
        pm.fileInfo['projectName'] = database.getCurrentProject()
        pm.fileInfo['task'] = itemMData['task']
        pm.fileInfo['code'] = itemMData['code']
        pm.fileInfo['type'] = itemMData['type']
        itemMData['workVer'] = 1
        itemMData['status'] = 'created'
        collection.find_one_and_update({'task': task, 'code': code}, {'$set': itemMData})

        itemPath = database.getPath(itemMData)
        sceneDirPath = itemPath[0]
        sceneFullPath = os.path.join(*itemPath)

        if not os.path.exists(sceneDirPath):
            os.makedirs(sceneDirPath)

        pm.saveAs(sceneFullPath)

        if parcial:
            print 'WARNING assemble: Some components have no publish to complete assemble this file!'

        else:
            print '%s assembled sucessfully!' % itemMData['filename']

    else:
        print 'ERROR assemble: No component published to assemble this file'
