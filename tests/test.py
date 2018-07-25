import pymel.core as pm


def browseCallback(opt, *args):
    print 'browse'
    selectDir = pm.fileDialog2(cap='choose directory', okCaption='Select', fm=3, dialogStyle=2)
    if opt == 1:
        print opt


win = pm.window(w=800, h=600)
col = pm.columnLayout(adjustableColumn=True, columnAlign='left', )
workLocTxt = pm.textFieldButtonGrp(label='Work Location', text='teste',
                                                buttonLabel='...', bc =lambda: browseCallback(1))
pm.showWindow()



