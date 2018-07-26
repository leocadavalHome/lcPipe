import pymel.core as pm
from core import database
from lcPipe.ui.infoWidget import InfoWidget
from lcPipe.ui.filtersWidget import FiltersWidget
from lcPipe.ui.itemListFiltersWidget import ItemListFiltersWidget
from lcPipe.ui.projectSelectWidget import ProjectSelectWidget

class item2Browser:
    def __init__(self):
        self.projectSelectWidget = None
        self.folderTreeWidget = None
        self.itemListWidget = None
        self.infoWidget = None
        self.createBrowser()
        self.typeOpt = None

    def createBrowser(self):
        win = pm.window(w=200)

        form = pm.formLayout(numberOfDivisions=100)
        col2 = pm.columnLayout(p=form, adjustableColumn=True)
        allowedAreas = ['right', 'left']
        pm.dockControl(label='BROWSER', w=200, area='left', content=win, allowedArea=allowedAreas)

        self.projectSelectWidget = ProjectSelectWidget()
        self.projectSelectWidget.createProjectSelect(col2)

        pm.rowLayout(nc=3, adj=1)
        self.typeOpt = pm.optionMenuGrp(label='Item Type', changeCommand=self.changeTypeCallback, cat=[[1,'left',5],[2,'left',-80]])
        types = ['asset', 'shot', 'model', 'uvs', 'texture', 'blendShape', 'rig', 'layout', 'animation',
                 'shotFinalizing', 'lightining', 'render']

        for assetType in types:
            pm.menuItem(label=assetType)

        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/small.png', c=lambda x, y=2: self.changeViewCallback(y))
        pm.symbolButton(image=r'D:/JOBS/PIPELINE/pipeExemple/scenes/icons/big.png', c=lambda x, y=1: self.changeViewCallback(y))

        pane = pm.paneLayout(p=form, configuration='top3', ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)], shp = 0)

        self.folderTreeWidget = FiltersWidget('asset')
        self.folderTreeWidget.createFilters(pane)

        self.itemListWidget = ItemListFiltersWidget()
        self.itemListWidget.createList(pane)
        self.itemListWidget.refreshList(user=self.folderTreeWidget.userFilter,
                                        status=self.folderTreeWidget.statusFilter,
                                        favorites=self.folderTreeWidget.favoritesFilter,
                                        task='asset')

        self.infoWidget = InfoWidget()
        self.infoWidget.createInfo(pane)

        self.folderTreeWidget.itemListWidget = self.itemListWidget
        self.folderTreeWidget.itemListWidget.type = 'asset'
        self.folderTreeWidget.itemListWidget.task = 'asset'
        self.projectSelectWidget.folderTreeWidget = self.folderTreeWidget
        self.projectSelectWidget.itemListWidget = self.itemListWidget
        self.itemListWidget.infoWidget = self.infoWidget

        pm.formLayout(form, edit=True,
                      attachForm=[(pane, 'left', 5), (pane, 'bottom', 5), (pane, 'right', 5),
                                  (col2, 'top', 5), (col2, 'left', 5), (col2, 'right', 5)],
                      attachControl=[(pane, 'top', 5, col2)],
                      attachPosition=[],
                      attachNone=()
                      )

        pm.showWindow()

    def changeTypeCallback(self, newTaskToSearch, *args):
        assetType = database.getTaskType(newTaskToSearch)

        self.itemListWidget.type = assetType

        self.folderTreeWidget.type = assetType
        self.folderTreeWidget.getFolderTree()

        self.itemListWidget.task = newTaskToSearch
        self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)

    def changeViewCallback(self, opt):
        self.itemListWidget.viewOption = opt
        self.itemListWidget.refreshList(path=self.itemListWidget.path, task=self.itemListWidget.task)

x = item2Browser()
x.createBrowser()