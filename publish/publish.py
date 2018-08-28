from lcPipe.publish.modelPublish import *
from lcPipe.publish.uvPublish import *
from lcPipe.publish.texPublish import *
from lcPipe.publish.shotFinalizingPublish import *
from lcPipe.publish.layoutPublish import *

import logging
logger = logging.getLogger(__name__)

def skip(*args):
    for a in args:
        logger.debug (a)

    logger.debug ('skip')
    return 'skip'


## Main routine
class PublishWidget(object):
    def __init__(self, task):

        self.checkProcedures = {
            'model':   {1.0: {'status': 'run', 'label': 'No namespace', 'check': noNameSpaces,
                              'fix': [deleteNameSpaces]},
                        2.0: {'status': 'run','label': 'No display layers', 'check': noDisplayLayers,
                              'fix': [delDisplayLayers]},
                        3.0: {'status': 'run','label': 'All geometry in geo_group', 'check': geosInsideGeoGroup,
                              'fix': [fixGeoGroup,skip]},
                        4.0: {'status': 'run','label': 'No Construction History', 'check': noConstructionHistory,
                              'fix': [deleteHistory]},
                        5.0: {'status': 'run','label': 'No Intermediate Shapes', 'check': noIntermediateShapes,
                              'fix': [deleteIntermediateShapes, selectIntermediateShapes]},

                        6.0: {'status': 'run', 'label': 'Valid Names', 'check': validNames,
                              'fix': [fixInvalidNames, selectInvalidNames,skip]},
                        7.0: {'status': 'run','label': 'No Duplicated Names', 'check': duplicatedNames,
                              'fix': [fixDuplicatedNames, selectDuplicatedNames]},
                        8.0: {'status': 'run','label': 'All geometry has "_geo" sulfix', 'check': geoHasSulfix,
                              'fix': [fixGeoSulfix, selGeoNoSulfix, skip]},
                        9.0: {'status': 'run','label': 'All grp nodes has "_grp" sulfix', 'check': grpHasSulfix,
                              'fix': [fixGrpSulfix, selGrpNoSulfix, skip]},
                        10.0: {'status': 'run','label': 'Valid Shape Names', 'check': validShapeNames,
                               'fix': [fixShapeNames, selectInvalidShapeNames]},

                        11.0: {'status': 'run','label': 'No NonManifold', 'check': noNonManifold,
                               'fix': [cleanNonManifold, selectNonManifold, skip]},
                        12.0: {'status': 'run','label': 'No LaminaFaces', 'check': noLaminaFaces,
                               'fix': [cleanLaminaFaces, selectLaminaFaces, skip]},
                        13.0: {'status': 'run','label': 'All vertex froozen', 'check': noVertexTransforms,
                               'fix': [freezeVertices, skip]},
                        14.0: {'status': 'run', 'label': 'No Locked Normals', 'check': unlockNormals,
                               'fix': [fixNormals, selectUnlockNormals, skip]},
                        15.0: {'status': 'skip', 'label': 'No hard Edges', 'check': noHardEdges,
                               'fix': [fixHardEdges, selHardEdges, skip]},

                        16.0: {'status': 'run','label': 'No Shaders', 'check': noShaders,
                               'fix': [fixShaders, selectShaderedObjs, skip]},
                        17.0: {'status': 'run','label': 'All names in lower case', 'check': islowercase,
                               'fix': [fixNotLowercase, selNotLowercase, skip]},
                        18.0: {'status': 'skip','label': 'All faces are Quad', 'check': nonQuad, 'fix': [selNonQuad, skip]},
                        19.0: {'status': 'skip','label': 'No holes on faces', 'check': noHoles, 'fix': [selHoles, skip]},
                        20.0: {'status': 'skip','label': 'All objs froozen transform', 'check': froozenTransforms,
                               'fix': [freezeTransforms, selNotFroozenTransforms,  skip]},
                        21.0: {'status': 'skip','label': 'geo_group pivot zeroed', 'check': geoGroupPivotZeroed,
                               'fix': [resetGeoGroupPivot, skip]},


                        },
            'uvs':     {1.0: {'status': 'run','label': 'No namespace', 'check': noNameSpaces, 'fix': [deleteNameSpaces]},
                        2.0: {'status': 'run','label': 'All geometry in geo_group', 'check': geosInsideGeoGroup, 'fix': [fixGeoGroup]},
                        3.0: {'status': 'run','label': 'No Construction History', 'check': noConstructionHistory, 'fix': [deleteHistory]},
                        4.0: {'status': 'run','label': 'No Intermediate Shapes', 'check': noIntermediateShapes,
                              'fix': [deleteIntermediateShapes, selectIntermediateShapes]},
                        5.0: {'status': 'run', 'label': 'Valid Names', 'check': validNames, 'fix': [fixInvalidNames, selectInvalidNames]},
                        6.0: {'status': 'run', 'label': 'No Duplicated Names', 'check': duplicatedNames,
                              'fix': [fixDuplicatedNames, selectDuplicatedNames]},
                        7.0: {'status': 'run', 'label': 'Valid Shape Names', 'check': validShapeNames,
                              'fix': [fixShapeNames, selectInvalidShapeNames]},
                        8.0: {'status': 'run', 'label': 'No Shaders', 'check': noShaders, 'fix': [fixShaders, selectShaderedObjs, skip]},

                        9.0: {'status': 'run', 'label': 'No Multiple UVmap', 'check': noMultipleUVsets,
                              'fix': [delMultipleUVsets, selMultipleUVsets]},
                        10.0: {'status': 'run', 'label': 'At least One UVmap', 'check': noMissingUVsets,
                               'fix': [applyAutomaticUV, selMissingUVsets]},

                        },


            'texture': {1.0: {'status': 'run', 'label': 'all textures on Default Work dir', 'check': imagesOnDir,
                               'fix': [copyImagesToDir]},
                         2.0: {'status': 'run', 'label': 'No object with default shader', 'check': noObjWithDefaultShader,
                              'fix': [selObjWithDefaultShader]},
                        },
            'xlo': {},
            'rig': {},
            'blendShape': {},
            'layout':  {1.0: {'status': 'run', 'label': 'correct fps', 'check': correctFps,
                              'fix': [fixFpsNoChangeKey, fixFpsChangeKey]},
                        2.0: {'status': 'run', 'label': 'correct camera name', 'check': cameraNameCheck,
                              'fix': [renameCamera]},
                        3.0: {'status': 'run', 'label': 'correct camera aspect', 'check': cameraAspectCheck,
                              'fix': [fixCameraAspect, skip]},
                        4.0: {'status': 'run', 'label': 'no reference unloaded', 'check': NoReferenceOff,
                              'fix': [removeUnloadedRefs, skip]},
                        5.0: {'status': 'skip', 'label': 'No sound or Correct name', 'check': checkAudioFile,
                              'fix': [skip]}
                        }
            }

        self.prePublishProcedures = {
                                'texture': {1.0: {'prePublish': importReferences}},
                                'rig': {1.0: {'prePublish': importReferences}},
                                'layout': {1.0: {'prePublish': doSceneCheck},
                                           2.0: {'prePublish': doPlayBlast}},
                                'shotFinalizing': {1.0: {'prePublish': doSceneCheck},
                                                   2.0: {'prePublish': cacheCameraAnimation}}
                                }

        if task in self.checkProcedures.keys():
            self.checksDict = self.checkProcedures[task]
        else:
            self.checksDict = {}

        if task in self.prePublishProcedures.keys():
            self.prePublishDict = self.prePublishProcedures[task]
        else:
            self.prePublishDict = {}

        self.checksWidgets = {}

    def createWin(self):
        if (pm.window('publishTest', exists=True)):
            pm.deleteUI('publishTest', window=True)

        order = self.checksDict.keys()
        height = (len(order)*30)+1

        self.win = pm.window('publishTest',rtf=True)
        form = pm.formLayout(numberOfDivisions=100)
        self.col = pm.columnLayout(p=form, w=200, h=500)
        self.btn = pm.button(p=form, l='VALIDATE', w=200, h=50, c=self.runChecks)

        pm.formLayout(form, edit=True,
                      attachForm=[(self.col, 'left', 5), (self.col, 'right', 5),(self.col, 'bottom', 5),
                                  (self.btn, 'left', 5), (self.btn, 'top', 5),(self.btn, 'right', 5)
                                  ],
                      attachControl=[(self.col, 'top', 5, self.btn)],
                      attachPosition=[],
                      attachNone=()
                      )

        order.sort()

        for id in order:
            self.checksWidgets[id] = pm.iconTextButton(p=self.col, style='iconAndTextHorizontal',
                                                       image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/empty.png',
                                                       label=self.checksDict[id]['label'])
        pm.showWindow(self.win)

    def closeWin(self):
        pm.deleteUI(self.win)

    def runChecks(self, *args):
        sucess = True

        order = self.checksDict.keys()
        order.sort()
        for id in order:
            result = self.checksDict[id]['check']()

            if result:
                if self.checksDict[id]['status'] == 'skip':
                    pm.iconTextButton(self.checksWidgets[id], e=True,
                                      image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/skip.png',
                                      label=self.checksDict[id]['label'] + '')
                else:
                    sucess = False
                    pm.iconTextButton(self.checksWidgets[id], e=True,
                                      image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/fix.png',
                                      label=self.checksDict[id]['label'] + ' failled')

                if not self.checksDict[id]['fix']:
                    continue

                popup = pm.popupMenu(p=self.checksWidgets[id])

                for fix in self.checksDict[id]['fix']:
                    pm.menuItem(p=popup, l=fix.__name__, c=lambda x, y=fix, z=id: self.runFix(y, z))

            else:
                pm.iconTextButton(self.checksWidgets[id], e=True,
                                  image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/valid.png',
                                  label=self.checksDict[id]['label'] + ' Ok')

        if sucess:
            self.runPrePublish()

    def runFix(self, fix, id):
        x = fix()

        if x == 'ok':
            pm.iconTextButton(self.checksWidgets[id], e=True,
                              image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/valid.png',
                              label=self.checksDict[id]['label'] + ' Ok')
        elif x == 'skip':
            pm.iconTextButton(self.checksWidgets[id], e=True,
                              image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/skip.png',
                              label=self.checksDict[id]['label'] + ' skipped')

            self.checksDict[id]['status'] = 'skip'

    def runPrePublish(self, *args):
        error = False

        resp = pm.confirmDialog(title='Save', ma='center',
                                message='Save before publish?',
                                button=['Ok', 'No'], defaultButton='Ok', dismissString='No')

        if resp == 'Ok':
            pm.saveFile()

        pm.button(self.btn, e=True, label='PUBLISH', c=self.prePublish, bgc=[0.0,0.5,0.0] )


    def prePublish(self, *args):
        error = False
        order = self.prePublishDict.keys()
        order.sort()

        for id in order:
            resp = self.prePublishDict[id]['prePublish']()
            if resp:
                error = True

        if not error:
            logger.debug('prePublish succeeded')
            self.publishFile()
        else:
            resp = pm.confirmDialog(title='Warning', ma='center',
                                    message='Error: Pre Publish Procedure Failled !',
                                    button=['Ok'], defaultButton='ok', dismissString='ok')
            logger.debug('prePublish failed')


    def publishFile(self, *args):
        pass
