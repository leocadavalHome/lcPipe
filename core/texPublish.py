import pymel.core as pm
import lcPipe.core.database as database

def imagesOnDir(*args):

fileNodes = pm.ls(type='file')
for fileNode in fileNodes:
    imgPath = fileNode.getAttr ('fileTextureName')
    print imgPath





# todo no unnused shaders nodes
# todo valid shader name convention
# todo valid images name convention
# todo no object with default shader

# todo images on standard dir


#todo delete unused node (Hypershade)
#todo unique Shader name ( project prefix_ch,pr,bg,vech_objname )
#todo check for sourceimage naming ( color=clr, bump=bmp, Specular=spc, normal=nrm, Ambient= amb, incandescence=inc, reflectivity= rlf, roughness= rghns, glossiness= glsns )
#todo find object and select with default shaders(lambert)
#todo check missing shader sourceimages
#todo before publish file save in the bounding box