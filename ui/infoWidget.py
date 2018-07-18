import pymel.core as pm


class InfoWidget():
    def __init__(self):
        self.widgetName = None
        self.parentWidget = None
        self.thumb = None
        self.statusField = None
        self.nameInfoField = None
        self.taskField = None
        self.codeField = None
        self.workVerField = None
        self.publishVerField = None
        self.task = False
        self.col = None

    def createInfo(self, parent):
        self.parentWidget = parent
        self.widgetName = pm.rowLayout(p=self.parentWidget, nc=2, adj=2)
        pm.picture(p=self.widgetName, image=u'D:\JOBS\PIPELINE\pipeExemple\scenes\icons\dragon.png', w=90, h=90)
        self.col = pm.columnLayout('col', adjustableColumn=True)
        self.statusField = pm.textFieldGrp('statusInfo', label='Status', cw=(1, 50), text='', adj=2,
                                           cat=(1, 'left', 5), editable=False)
        self.nameInfoField = pm.textFieldGrp('nameInfo', label='Name', cw=(1, 50), text='', adj=2, cat=(1, 'left',5),
                                             editable=False)
        self.codeField = pm.textFieldGrp('codeInfo', label='Code', cw=(1, 50), text='', adj=2, cat=(1, 'left', 5),
                                         editable=False)
        self.taskField = pm.textFieldGrp('taskinfo', label='Task', cw=(1, 50), text='', adj=2, cat=(1, 'left', 5),
                                         editable=False)

        #self.workVerField = pm.intFieldGrp('WorkVersion', p=self.col1, label='Work Version', cw=(1, 50), value1=1, adj=2,
        #                                   cat=(1, 'left', 5), enable=False)
        #self.publishVerField = pm.intFieldGrp('PublishVersion', p=self.col1, label='Publish Version', cw=(1, 50), value1=1,
        #                                      adj=2, cat=(1, 'left', 5), enable=False)

    def putItemInfo(self, item):
        pm.textFieldGrp(self.nameInfoField, e=True, tx=item['name'])
        pm.textFieldGrp(self.codeField, e=True, tx=item['code'])
        pm.textFieldGrp(self.taskField, e=True, tx=item['task'])
        #pm.intFieldGrp(self.workVerField, e=True, value1=item['workVer'])
        #pm.intFieldGrp(self.publishVerField, e=True, value1=item['publishVer'])

    def putInfo(self, itemWidget):
        name = itemWidget.name.split('_')[1]
        # short = itemWidget.name[0:2]
        code = itemWidget.name.split('_')[0][3:]  ### hard coding!!
        pm.textFieldGrp(self.nameInfoField, e=True, tx=name)
        pm.textFieldGrp(self.codeField, e=True, tx=code)
        pm.textFieldGrp(self.taskField, e=True, tx=itemWidget.task)
        #pm.intFieldGrp(self.workVerField, e=True, value1=itemWidget.workVer)
        #pm.intFieldGrp(self.publishVerField, e=True, value1=itemWidget.publishVer)
