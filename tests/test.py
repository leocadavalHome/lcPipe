

import pymel.core as pm

win = pm.window(w=200)

form = pm.formLayout(numberOfDivisions=100)
allowedAreas = ['right', 'left']
pm.dockControl(label='BROWSER', w=200, area='left', content=win, allowedArea=allowedAreas)

pane = pm.paneLayout(configuration='top3',ps=[(1, 20, 80), (2, 80, 80), (3, 100, 20)], shp=0)

pm.treeView(p=pane)

pm.flowLayout(p=pane)

pm.columnLayout(p=pane)

pm.formLayout( form, edit=True,
                 attachForm=[(pane, 'top', 5), (pane, 'left', 5), (pane, 'bottom', 5), (pane, 'right', 5)],
                 attachControl=[],
                 attachPosition=[],
                 attachNone=()
               )

pm.showWindow()
