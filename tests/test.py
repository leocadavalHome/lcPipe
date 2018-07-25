import pymel.core as pm
def addMultiPromp():
    form = pm.setParent(q=True)
    f = pm.formLayout(form, e=True, width=150)
    row = pm.columnLayout()
    nameField = pm.textFieldGrp('addMulti_nameField', label='Name', cw=[(1, 80), (2, 20)], text='',
                                cat=[(1, 'left', 10), (2, 'left', 5)], editable=True)
    rangeField = pm.intFieldGrp('addMulti_rangeField', label= 'start-end-step', cw=(1, 80),
                                cat=[(1, 'left', 10), (2, 'left', 5)], numberOfFields=3, value1=1, value2=10, value3=1)
    rangeField = pm.intFieldGrp('addMulti_zeroField',label= 'zeroPad', cw=(1, 80), cat=[(1, 'left', 10), (2, 'left', 5)],
                                numberOfFields=1, value1=3)


    b1 = pm.button(p=f, l='Cancel')
    b2 = pm.button(p=f, l='OK')

    spacer = 5
    top = 5
    edge = 5
    pm.formLayout(form, edit=True,
                  attachForm=[(row, 'right', edge), (row, 'top', top), (row, 'left', edge),
                              (row, 'right', edge),
                              (b1, 'right', edge), (b1, 'bottom', edge), (b2, 'left', edge),
                              (b2, 'bottom', edge)],
                  attachNone=[], attachControl=[],
                  attachPosition=[(b1, 'right', spacer, 90), (b2, 'left', spacer, 10)])

print pm.layoutDialog(ui=addMultiPromp)