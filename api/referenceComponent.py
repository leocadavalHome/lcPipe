from lcPipe.api.component import Component

class ReferenceComponent(Component):
    def __init__(self, ns, componentMData, parent=None):
        super(ReferenceComponent, self).__init__(ns=ns, componentMData=componentMData, parent=parent)
