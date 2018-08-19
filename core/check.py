import pymel.core as pm
from lcPipe.core import database
from lcPipe.api.item import Item
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent
from lcPipe.api.referenceComponent import ReferenceComponent
import logging


logger = logging.getLogger(__name__)
logger.setLevel(10)

def checkVersions():
    """
    Update the current file metadata with component versions on the database

    :return:
    """
    item = Item(fromScene=True)

    for ns, componentMData in item.components.iteritems():
        if ns == 'cam':
            # todo tratar versoes da camera
            continue

        if componentMData['assembleMode'] == 'reference':
            refComponent = ReferenceComponent(ns, componentMData, parent=item)
            refComponent.checkDBForNewVersion()

        elif componentMData['assembleMode'] == 'xlo':
            xloComponent = XloComponent(ns, componentMData, parent=item)
            xloComponent.checkDBForNewVersion()
            xloComponent.checkDBForNewCacheVersion()

        elif componentMData['assembleMode'] == 'cache':
            cacheComponent = CacheComponent(ns, componentMData, parent=item)
            cacheComponent.checkDBForNewVersion()

    item.putDataToDB()


def sceneRefCheck(silent=False):
    """

    Compare the current scene references versions with metadata and update as needed

    :param silent: boolean
    :return:
    """
    uptodate = True
    logger.debug('init sceneChecking...')
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')

    if currentProject != projName:
        logger.error('This file is from a project different from the current project')
        return

    item = Item(fromScene=True)  # get current scene metadata


    # compare references and metadata and create lists of references to add, delete, update and replace
    logger.debug('creating lists of changes...')
    refOnSceneList = pm.getReferences()
    toDelete = [x for x in refOnSceneList if x not in item.components]
    toAdd = [x for x in item.components if x not in refOnSceneList and x != 'cam']
    toReplace = [x for x in item.components if item.components[x]['task'] != item.components[x]['proxyMode']]
    refToCheckUpdate = [x for x in refOnSceneList if x not in toDelete and x not in toReplace]
    toUpdate = {}

    # create the list of references to update depending on the assemble mode
    logger.debug('check update...')
    for ns in refToCheckUpdate:
        logger.debug('ns:%s' % ns)
        if item.components[ns]['assembleMode'] == 'camera':
            continue

        if item.components[ns]['assembleMode'] == 'reference':
            component = ReferenceComponent(ns, item.components[ns], parent=item)
            toUpdate[ns] = component.updateVersion(refOnSceneList[ns])


        if item.components[ns]['assembleMode'] == 'xlo':
            component = XloComponent(ns, item.components[ns], parent=item)
            toUpdate[ns] = component.updateVersion(refOnSceneList[ns])

        if item.components[ns]['assembleMode'] == 'cache':
            cache = CacheComponent(ns, item.components[ns], parent=item)
            toUpdate[ns] = cache.updateVersion(refOnSceneList[ns])

    # If not in silent mode, show dialogs to the user choose which references should be processed
    logger.debug('prompt if needed')
    if not silent:
        if toDelete:
            uptodate = False
            toDelete = pm.layoutDialog(ui=lambda: refCheckPrompt(toDelete, 'delete')).split(',')

        if toAdd:
            uptodate = False
            toAdd = pm.layoutDialog(ui=lambda: refCheckPrompt(toAdd, 'add')).split(',')

        if toReplace:
            uptodate = False
            toReplace = pm.layoutDialog(ui=lambda: refCheckPrompt(toReplace, 'replace')).split(',')

        upDateList = [x for x, y in toUpdate.iteritems() if y ]
        if upDateList:
            uptodate = False
            upDateList = pm.layoutDialog(ui=lambda: refCheckPrompt(upDateList, 'update')).split(',')
            toUpdate = {x: y for x, y in toUpdate.iteritems() if x in upDateList}
        else:
            toUpdate = {}

        if uptodate:
            pm.confirmDialog(title='Scene Check', ma='center',
                             message='Versions ok!',
                             button=['OK'], defaultButton='OK', dismissString='OK')


    logger.debug('processing...')
    # Do the processing
    # delete
    logger.info('toDelete:%s' % toDelete)
    for ns in toDelete:
        refOnSceneList[ns].remove()

    # add
    logger.info('toAdd:%s' % toAdd)
    for ns in toAdd:
        if item.components[ns]['assembleMode'] == 'camera':
            continue

        if item.components[ns]['assembleMode'] == 'reference':
            component = ReferenceComponent(ns, item.components[ns], parent=item)
            component.addToScene()

        elif item.components[ns]['assembleMode'] == 'xlo':
            component = XloComponent(ns, item.components[ns], parent=item)
            component.addToScene()

            cache = CacheComponent(ns, item.components[ns], parent=item)
            cache.importCache()

        elif item.components[ns]['assembleMode'] == 'cache':
            cache = CacheComponent(ns, item.components[ns], parent=item)
            cache.addToScene()

    #update versions
    for ns, versions in toUpdate.iteritems():
        if item.components[ns]['assembleMode'] == 'camera':
            continue

        if item.components[ns]['assembleMode'] == 'reference':
            component = ReferenceComponent(ns, item.components[ns], parent=item)
            componentPath = component.getPublishPath()
            refOnSceneList[ns].replaceWith(componentPath)

        if item.components[ns]['assembleMode'] == 'xlo':
            if 'ver' in versions:
                component = XloComponent(ns, item.components[ns], parent=item)
                componentPath = component.getPublishPath()
                refOnSceneList[ns].replaceWith(componentPath)

            if 'cacheVer' in versions:
                #todo check if need to delete old cache node
                cache = CacheComponent(ns, item.components[ns], parent=item)
                cache.importCache()

        if item.components[ns]['assembleMode'] == 'cache':
            component = CacheComponent(ns, item.components[ns], parent=item)
            componentPath = component.getPublishPath()
            refOnSceneList[ns].replaceWith(componentPath)

    # Replace
    for ns in toReplace:
        if item.components[ns]['assembleMode'] == 'reference':
            logger.debug('task:%s, proxyMode:%s'%(item.components[ns]['task'], item.components[ns]['proxyMode']))

            item.components[ns]['task'] = item.components[ns]['proxyMode']
            logger.debug ('task:%s, proxyMode:%s'%(item.components[ns]['task'], item.components[ns]['proxyMode']))
            component = ReferenceComponent(ns, item.components[ns], parent=item)
            logger.debug ( component.getPublishPath())
            logger.debug (refOnSceneList[ns].path)
            # todo check if existe uma versao
            refOnSceneList[ns].replaceWith(component.getPublishPath())
    item.putDataToDB()

    logger.info('done sceneChecking!')

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

