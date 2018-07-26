import pymel.core as pm

class FiltersWidget:
    def __init__(self, itemType='asset'):
        self.userFilter='non'
        self.statusFilter = 'created'
        self.favoritesFilter = ['0001','0002']
        self.parentWidget = None
        self.widgetName = None
        self.itemListWidget = None
        self.itemType=itemType

    def createFilters(self, parentWidget):
        self.parentWidget = parentWidget
        self.widgetName = pm.formLayout(p= self.parentWidget, numberOfDivisions=100)
        tx1 = pm.text (label='user')
        tf1 = pm.textField (tx='')
        tx2 = pm.text (label='status')
        tf2 = pm.textField (tx='')
        tx3 = pm.text (label='favorites')
        txscrll = pm.textScrollList()

        pm.formLayout (self.widgetName, edit=True,
                       attachForm=[(tx1, 'top', 5),
                                   (tx1, 'left', 5),(tx2, 'left', 5),(tx3, 'left', 5),
                                   (tf1, 'left', 5),(tf1, 'right', 5),
                                   (tf2, 'left', 5),(tf2, 'right', 5),
                                   (txscrll, 'left', 5),(txscrll, 'right', 5),
                                   (txscrll, 'bottom', 5),
                                   ],
                       attachControl=[(tf1, 'top', 5, tx1), (tx2, 'top', 5, tf1), (tf2, 'top', 5, tx2),
                                      (tx3, 'top', 5, tf2), (txscrll, 'top', 5, tx3)],
                       attachPosition=[],
                       attachNone=()
                       )


    def getFolderTree(self, fromDb=True):
        pass