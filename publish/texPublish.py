import os.path
import shutil

import lcPipe.core.database as database
import pymel.core as pm
import logging
logger = logging.getLogger(__name__)

def imagesOnDir(*args):
    fileNodes = pm.ls(type='file')
    for fileNode in fileNodes:
        imgPath = fileNode.getAttr('fileTextureName')
        imgDir = os.path.dirname(imgPath)
        workPath = database.getSceneImagesPath('imagesWorkLocation')
        if not os.path.normpath(imgDir) == os.path.normpath(workPath):
            return True


def copyImagesToDir(*args):
    fileNodes = pm.ls(type='file')
    for fileNode in fileNodes:
        imgPath = fileNode.getAttr('fileTextureName')
        imgDir = os.path.dirname(imgPath)
        imageName = os.path.basename(imgPath)
        workPath = database.getSceneImagesPath('imagesWorkLocation')

        if not os.path.normpath(imgDir) == os.path.normpath(workPath):
            if not os.path.exists(workPath):
                os.makedirs(workPath)
            shutil.copy2(imgPath, os.path.join(workPath, imageName))
            fileNode.setAttr('fileTextureName', os.path.join(workPath, imageName))
    return 'ok'


def noObjWithDefaultShader(*args):
    defaultShaderSG = pm.PyNode ('initialShadingGroup')

    geoList = defaultShaderSG.listConnections(type='surfaceShape')

    if geoList:
        return True


def selObjWithDefaultShader(*args):
    defaultShaderSG = pm.PyNode('initialShadingGroup')
    geoList = defaultShaderSG.listConnections(type='surfaceShape')
    pm.select(geoList)
    return 'select'


def checkUnused(*args):
    pass

#PrePublish
def importReferences(*args):
    try:
        refs = pm.getReferences()
        for ref in refs.itervalues():
            ref.importContents(removeNamespace=True)
        return False
    except IndexError:
        pass


# todo no unnused shaders nodes
# todo valid shader name convention
# todo valid images name convention
# done no object with default shader
# done images on standard dir

'''
# todo delete unused node (Hypershade)
# todo unique Shader name ( project prefix_ch,pr,bg,vech_objname )
# todo check for sourceimage naming ( color=clr, bump=bmp, Specular=spc, normal=nrm, Ambient= amb, incandescence=inc, reflectivity= rlf, roughness= rghns, glossiness= glsns )
# todo find object and select with default shaders(lambert)
# todo check missing shader sourceimages
# todo before publish file save in the bounding box
'''