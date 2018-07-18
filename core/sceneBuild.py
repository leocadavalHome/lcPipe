import pymel.core as pm
import os.path
from lcPipe.core import database
import copy


def referenceCache(sourceMData):
    path = database.getPath(sourceMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    for cache_ns, cacheMData in sourceMData['caches'].iteritems():
        if cacheMData['ver'] == 0:
            print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
            continue

        ver = 'v%03d_' % cacheMData['ver']
        cacheName = database.templateName(cacheMData) + '_' + cache_ns
        cacheFileName = ver + cacheName + '.abc'
        cacheFullPath = os.path.join(cachePath, cacheFileName)

        pm.createReference(cacheFullPath, namespace=cache_ns, groupReference=True, groupName='geo_group',
                           type='Alembic')


def importCaches(sourceMData):
    path = database.getPath(sourceMData, dirLocation='cacheLocation', ext='')
    cachePath = os.path.join(*path)

    for cache_ns, cacheMData in sourceMData['caches'].iteritems():
        if cacheMData['cacheVer'] == 0:
            print 'Component %s not yet published!!' % (cache_ns + ':' + cacheMData['task'] + cacheMData['code'])
            continue

        ver = 'v%03d_' % cacheMData['cacheVer']
        cacheName = database.templateName(cacheMData) + '_' + cache_ns
        cacheFileName = ver + cacheName + '.abc'
        cacheFullPath = os.path.join(cachePath, cacheFileName)

        pm.AbcImport(cacheFullPath, mode='import', fitTimeRange=True, setToStartFrame=True, connect='/')

    return


def referenceXlos(sourceMData):
    parcial = False
    empty = True

    for xlo_ns, xlo in sourceMData['components'].iteritems():
        if xlo['code']=='9999':
            xloMData = database.getItemMData(task=xlo['task'], code=xlo['code'], itemType=xlo['type'])
        else:
            xloMData = database.getItemMData(task='xlo', code=xlo['code'], itemType=xlo['type'])

        if xloMData['publishVer'] == 0:
            print 'Component %s not yet published!!' % (xlo_ns + ':' + xloMData['task'] + xloMData['code'])
            parcial=True
            continue
        else:
            version = 'v%03d_' % xloMData['publishVer']

        empty = False
        path = database.getPath(xloMData, dirLocation='publishLocation')
        xloPath = os.path.join(path[0], version + path[1])
        pm.createReference(xloPath, namespace=xlo_ns)

    return empty, parcial


def build(itemType, task, code):
    parcial = False
    empty = True

    print 'start assembling'

    itemMData = database.getItemMData(task=task, code=code, itemType=itemType)

    if not itemMData:
        print 'ERROR: No metadata for this item'
        return

    itemSources = itemMData['source']
    if not itemSources:
        itemSources = itemMData['components']

    pm.newFile(f=True, new=True)

    for source_ns, source in itemSources.iteritems():
        # read components item
        sourceMData = database.getItemMData(code=source['code'], task=source['task'],itemType=source['type'])

        if not sourceMData:
            print 'ignoring...'
            continue

        if sourceMData['publishVer'] == 0:
            print 'Component %s not yet published!!' % (source_ns + ':' + source['task'] + source['code'])
            parcial = True
            continue

        empty = False

        path = database.getPath(sourceMData, dirLocation='publishLocation')
        version = 'v%03d_' % sourceMData['publishVer']
        componentPath = os.path.join(path[0], version + path[1])

        # import
        if source['assembleMode'] == 'import':
            pm.importFile(componentPath, defaultNamespace=True)

            # reference, , ,
        elif source['assembleMode'] == 'reference':
            ns = source_ns
            pm.createReference(componentPath, namespace=ns)

            print itemMData
        # copy from another scene
        elif source['assembleMode'] == 'copy':
            pm.openFile(componentPath, force=True)
            itemMData['components'] = copy.deepcopy(sourceMData['components'])
            # pm.renameFile ( sceneFullPath )

        elif source['assembleMode'] == 'cache':
            pm.namespace(add=source_ns)
            pm.namespace(set=source_ns)

            referenceCache(sourceMData)

            itemMData['components'] = copy.deepcopy(sourceMData['caches'])

            pm.namespace(set=':')

        # xlo
        elif source['assembleMode'] == 'xlo':
            referenceXlos(sourceMData)
            importCaches(sourceMData)

            itemMData['components'] = copy.deepcopy(sourceMData['components'])

            for ns, component in itemMData['components'].iteritems():
                component['cacheVer'] = sourceMData['caches'][ns]['cacheVer']
                component['task']= 'xlo'
            # pm.namespace( set=':')

    # update infos on scene and database
    if not empty or not itemSources:
        pm.fileInfo['projectName'] = database.getCurrentProject()
        pm.fileInfo['task'] = itemMData['task']
        pm.fileInfo['code'] = itemMData['code']
        pm.fileInfo['type'] = itemMData['type']
        itemMData['workVer'] = 1
        itemMData['status'] = 'created'

        collection = database.getCollection(itemMData['type'])
        collection.find_one_and_update({'task': task, 'code': code}, {'$set': itemMData})

        itemPath = database.getPath(itemMData)
        sceneDirPath = itemPath[0]
        sceneFullPath = os.path.join(*itemPath)

        if not os.path.exists(sceneDirPath):
            os.makedirs(sceneDirPath)

        pm.saveAs(sceneFullPath)

        if parcial:
            itemMData['status'] = 'partial'
            pm.confirmDialog(title='Warning', ma='center', message='WARNING build: Some components have no publish to complete build this file!', button=['OK'],
                             defaultButton='OK', dismissString='OK')

        else:
            pm.confirmDialog(title='Warning', ma='center',
                             message='%s assembled sucessfully!' % itemMData['filename'],
                             button=['OK'], defaultButton='OK', dismissString='OK')

    else:
        pm.confirmDialog(title='Warning', ma='center', message='ERROR build: No component published to build this file',
                         button=['OK'], defaultButton='OK', dismissString='OK')

