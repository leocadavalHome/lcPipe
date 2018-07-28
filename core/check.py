import pymel.core as pm
from lcPipe.core import database
from lcPipe.api.item import Item
from lcPipe.api.cacheComponent import CacheComponent
from lcPipe.api.xloComponent import XloComponent
from lcPipe.api.referenceComponent import ReferenceComponent

def checkVersions():
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
    uptodate = True
    print 'init sceneChecking...'
    currentProject = database.getCurrentProject()
    projName = pm.fileInfo.get('projectName')

    if currentProject != projName:
        print 'ERROR sceneRefCheck: This file is from a project different from the current project'
        return

    item = Item(fromScene=True)

    refOnSceneList = pm.getReferences()

    toDelete = [x for x in refOnSceneList if x not in item.components]
    toAdd = [x for x in item.components if x not in refOnSceneList]
    refToCheckUpdate = [x for x in refOnSceneList if x not in toDelete]
    toUpdate = {}

    for ns in refToCheckUpdate:
        print ns
        print item.components[ns]

        if item.components[ns]['assembleMode'] == 'camera':
            continue

        if item.components[ns]['assembleMode'] == 'reference':
            component = ReferenceComponent(ns, item.components[ns],parent=item)
            toUpdate[ns] = component.updateVersion(refOnSceneList[ns])

        if item.components[ns]['assembleMode'] == 'xlo':
            print 'entrou'
            print ns, item.components[ns]
            component = XloComponent(ns, item.components[ns], parent=item)
            toUpdate[ns] = component.updateVersion(refOnSceneList[ns])

        if item.components[ns]['assembleMode'] == 'cache':
            cache = CacheComponent(ns, item.components[ns], parent=item)
            toUpdate[ns] = cache.updateVersion(refOnSceneList[ns])

    if not silent:
        if toDelete:
            uptodate = False
            toDelete = pm.layoutDialog(ui=lambda: refCheckPrompt(toDelete, 'delete')).split(',')

        if toAdd:
            uptodate = False
            toAdd = pm.layoutDialog(ui=lambda: refCheckPrompt(toAdd, 'add')).split(',')


        upDateList = [x for x, y in toUpdate.iteritems() if y ]
        if upDateList:
            uptodate = False
            upDateList = pm.layoutDialog(ui=lambda: refCheckPrompt(upDateList, 'update')).split(',')
            toUpdate = {x: y for x, y in toUpdate.iteritems() if x in upDateList}
        else:
            toUpdate = {}

        if uptodate == True:
            pm.confirmDialog(title='Scene Check', ma='center',
                             message='Versions ok!',
                             button=['OK'], defaultButton='OK', dismissString='OK')

    print 'toDelete:%s' % toDelete
    for ns in toDelete:
        refOnSceneList[ns].remove()

    print 'toAdd:%s' % toAdd
    for ns in toAdd:
        if item.components[ns]['assembleMode'] == 'camera':
            continue

        print ns
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

    print 'done sceneChecking!'

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

