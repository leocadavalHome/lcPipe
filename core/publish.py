
from lcPipe.core.modelPublish import *
from lcPipe.core.uvPublish import *
from lcPipe.core.texPublish import *

def skip(*args):
    for a in args:
        print a

    print 'skip'
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
                              'fix': [fixGeoGroup]},
                        4.0: {'status': 'run','label': 'No Construction History', 'check': noConstructionHistory,
                              'fix': [deleteHistory]},
                        5.0: {'status': 'run','label': 'No Intermediate Shapes', 'check': noIntermediateShapes,
                              'fix': [deleteIntermediateShapes, selectIntermediateShapes]},

                        6.0: {'status': 'run', 'label': 'Valid Names', 'check': validNames,
                              'fix': [fixInvalidNames, selectInvalidNames]},
                        7.0: {'status': 'run','label': 'No Duplicated Names', 'check': duplicatedNames,
                              'fix': [fixDuplicatedNames, selectDuplicatedNames]},
                        8.0: {'status': 'run','label': 'All geometry has "_geo" sulfix', 'check': geoHasSulfix,
                              'fix': [fixGeoSulfix, selGeoNoSulfix]},
                        9.0: {'status': 'run','label': 'All grp nodes has "_grp" sulfix', 'check': grpHasSulfix,
                              'fix': [fixGrpSulfix, selGrpNoSulfix]},
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
                         2.0: {'status': 'run', 'label': 'all textures on Default Work dir', 'check': noObjWithDefaultShader,
                              'fix': [selObjWithDefaultShader]},
                        },
            'xlo': {},
            'rig': {},
            'blendShape': {},
        }

        if task in self.checkProcedures.keys():
            self.checksDict = self.checkProcedures[task]
        else:
            self.checksDict = {}

        self.checksWidgets = {}

    def createWin(self):
        if (pm.window('publishTest', exists=True)):
            pm.deleteUI('publishTest', window=True)

        self.win = pm.window('publishTest', w=200, h=300)
        self.parentCol = pm.columnLayout(adj=1)
        self.col = pm.columnLayout()
        self.btn = pm.button(p=self.parentCol, l='VALIDATE', w=200, h=50, c=self.runChecks)

        pm.showWindow(self.win)

        order = self.checksDict.keys()
        order.sort()

        for id in order:
            self.checksWidgets[id] = pm.iconTextButton(p=self.col, style='iconAndTextHorizontal',
                                                       image1='D:JOBS/PIPELINE/pipeExemple/scenes/icons/empty.png',
                                                       label=self.checksDict[id]['label'])

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
            print 'item valid!'
            pm.button(self.btn, e=True, l='PUBLISH', c=self.publishFile)

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

    def publishFile(self, *args):
        pass
