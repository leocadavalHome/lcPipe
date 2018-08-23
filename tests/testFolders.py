import pymel.core as pm
import os, sys
try:
	from shiboken import wrapInstance
except:
	from shiboken2 import wrapInstance

try:
    from PySide import QtGui as widgets
except:
    from PySide2 import QtWidgets as widgets

import maya.OpenMayaUI as omui
from PySide import QtGui, QtCore

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), widgets.QWidget)

class exampleQMainWindow (QtGui.QMainWindow):
    def __init__ (self):
        super(exampleQMainWindow, self).__init__()
        # Create QListWidget
        self.treeWidget = QtGui.QTreeWidget(self)
        self.treeWidget.setColumnCount(1)

        self.setStyleSheet( """
                            QTreeView {
                                        font-size: 12pt; 
                                        font-family: Open Sans;
                                        font-weight: Bold;
                                        }
                            }
                            QTreeWidget::item {
                                                  padding: 3px 0;
                                                }   
                            QTreeView::branch:has-children:!has-siblings:closed,
                            QTreeView::branch:closed:has-children:has-siblings {
                                    border-image: none;
                                    image: url(D:/JOBS/PIPELINE/pipeExemple/scenes/icons/branch-closed.png);
                            }
                            
                            QTreeView::branch:open:has-children:!has-siblings,
                            QTreeView::branch:open:has-children:has-siblings  {
                                    border-image: none;
                                    image: url(D:/JOBS/PIPELINE/pipeExemple/scenes/icons/branch-open.png);
                            }
                            """)

        item0 = QtGui.QTreeWidgetItem(self.treeWidget, ['Title 0', 'Summary 0'])
        item00 = QtGui.QTreeWidgetItem (item0, ['ARPEGGIATOR', 'Summary 00'])
        item01 = QtGui.QTreeWidgetItem (item0, ['PADS', 'Summary 01'])

        # Second top level item and its kids
        item1 = QtGui.QTreeWidgetItem (self.treeWidget, ['Title 1', 'Summary 1'])
        item10 = QtGui.QTreeWidgetItem (item1, ['Title 10', 'Summary 10'])
        item11 = QtGui.QTreeWidgetItem (item1, ['Title 11', 'Summary 11'])
        item12 = QtGui.QTreeWidgetItem (item1, ['Title 12', 'Summary 12'])

        # Children of item11
        item110 = QtGui.QTreeWidgetItem (item11, ['Title 110', 'Summary 110'])
        item111 = QtGui.QTreeWidgetItem (item11, ['Title 111', 'Summary 111'])
        self.setCentralWidget(self.treeWidget)

x = exampleQMainWindow()
x.show()

