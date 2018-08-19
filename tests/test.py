def browseCallBack(*args):
    resultDir = pm.fileDialog2(cap='choose directory', okCaption='Select', fm=3, dialogStyle=2)
    if resultDir:
        pm.textField('pathTxtField', e=True, tx=os.path.normpath(resultDir[0]))
        listSets()

def listSets():
    searchDir = pm.textField('pathTxtField', q=True, tx=True)
    sets = next(os.walk(searchDir))[1]
    pm.textScrollList('setScrollList', e=True, ra=True)
    pm.textScrollList('setScrollList', e=True, append=sets)

def selectSetCallback(*args):
    sel = pm.textScrollList('setScrollList', q=True, si=True)
    searchDir = pm.textField ('pathTxtField', q=True, tx=True)
    if sel:
        groupDir = os.path.join(searchDir, sel[0], 'wolftv', 'asset', 'group')
        print groupDir
        if os.path.isdir(groupDir):
            pm.text('groupTxt', e=True, l='   found!')
        else:
            pm.text('groupTxt', e=True, l='   no diretory found')

        set_pieceDir = os.path.join(searchDir, sel[0], 'wolftv', 'asset', 'set_piece')
        print set_pieceDir
        if os.path.isdir(set_pieceDir):
            pm.text('pieceTxt', e=True, l='   found!')
        else:
            pm.text('pieceTxt', e=True, l='   no diretory found')

        descriptionFileDir = os.path.join(searchDir, sel[0])
        descList = pm.getFileList (folder=descriptionFileDir, filespec='*.json')
        if len(descList)==1:
            pm.text ('descriptionTxt', e=True, l='   found!')
        elif len(descList)>1:
            pm.text ('descriptionTxt', e=True, l='   more than one found!')
        else:
            pm.text ('descriptionTxt', e=True, l='   no json file found!')

def importCallback (*args):
    pass

def cancelCallback (*args):
    pm.deleteUI('FlyingBarkIngestTool', window=True)

def fbIngestTool():
    if pm.window('FlyingBarkIngestTool', exists=True):
        pm.deleteUI('FlyingBarkIngestTool', window=True)

    pm.window('FlyingBarkIngestTool')
    pm.columnLayout()
    pm.rowLayout (nc=3)
    pm.text(l= 'PATH')
    pm.textField('pathTxtField', w=205)
    pm.button(l='...', c=browseCallBack)
    pm.setParent('..')
    pm.separator(h=20)
    pm.text(label='SETS')
    pm.separator(h=5)
    pm.textScrollList('setScrollList', h=150, sc=selectSetCallback)
    pm.separator(h=10)
    pm.rowLayout (nc=2)
    pm.text(label='GROUP DIR')
    pm.text('groupTxt', l='')
    pm.setParent('..')
    pm.separator(h=10)
    pm.rowLayout (nc=2)
    pm.text(label='SET_PIECES DIR')
    pm.text('pieceTxt', l='')
    pm.setParent('..')
    pm.separator(h=10)
    pm.rowLayout (nc=2)
    pm.text(label='DESCRIPTION FILE')
    pm.text('descriptionTxt', l='')
    pm.setParent('..')
    pm.separator(h=20)
    pm.rowLayout(nc=2)
    pm.button('Import', label='Import', w=125, h=50, c=importCallback)
    pm.button('CancelBtn', label='Cancel', w=125, h=50)
    pm.showWindow()