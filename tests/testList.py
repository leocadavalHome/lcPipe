import pymel.core as pm
import os, sys
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
from PySide2 import QtGui, QtCore, QtWidgets

def getMayaWindow():
    ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(ptr), QtWidgets.QWidget)

class QCustomQWidget (QtWidgets.QWidget):
    def __init__ (self, parent = None):
        super(QCustomQWidget, self).__init__(parent)
        self.textQVBoxLayout = QtGui.QVBoxLayout()
        self.textUpQLabel    = QtGui.QLabel()
        self.textDownQLabel  = QtGui.QLabel()
        self.textQVBoxLayout.addWidget(self.textUpQLabel)
        self.textQVBoxLayout.addWidget(self.textDownQLabel)
        self.allQHBoxLayout  = QtGui.QHBoxLayout()
        self.iconQLabel      = QtGui.QLabel()
        self.allQHBoxLayout.addWidget(self.iconQLabel, 0)
        self.allQHBoxLayout.addLayout(self.textQVBoxLayout, 1)
        self.setLayout(self.allQHBoxLayout)
        # setStyleSheet
        self.setStyleSheet('''
            background: white;
        ''')
        self.textUpQLabel.setStyleSheet('''
            color: rgb(0, 0, 255);
            background: white;
        ''')
        self.textDownQLabel.setStyleSheet('''
            color: rgb(255, 0, 0);
            background: white;
        ''')

    def setTextUp (self, text):
        self.textUpQLabel.setText(text)

    def setTextDown (self, text):
        self.textDownQLabel.setText(text)

    def setIcon (self, imagePath):
        self.iconQLabel.setPixmap(QtGui.QPixmap(imagePath))

class exampleQMainWindow (QtGui.QMainWindow):
    def __init__ (self):
        super(exampleQMainWindow, self).__init__()
        # Create QListWidget
        self.myQListWidget = QtGui.QListWidget(self)
        self.myQListWidget.setResizeMode(QtGui.QListView.Adjust)
        self.myQListWidget.setFlow(QtGui.QListView.LeftToRight)
        #self.myQListWidget.setViewMode(QtGui.QListView.IconMode)
        self.myQListWidget.setWrapping(True)
        #self.myQListWidget.setGridSize(QtCore.QSize(192, 96))
        self.myQListWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.myQListWidget.setIconSize(QtCore.QSize(90, 90))
        self.myQListWidget.setSelectionRectVisible(True)
        #self.myQListWidget.isSelectionRectVisible(True)
        self.myQListWidget.setSpacing(5)
        self.myQListWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        for index, name, icon in [
            ('No.1', 'Meyoko',  r'D:\JOBS\PIPELINE\pipeExemple\scenes\icons\block.png'),
            ('No.2', 'Nyaruko', r'D:\JOBS\PIPELINE\pipeExemple\scenes\icons\block.png'),
            ('No.3', 'Louise',  r'D:\JOBS\PIPELINE\pipeExemple\scenes\icons\block.png')]:
            # Create QCustomQWidget
            myQCustomQWidget = QCustomQWidget()
            myQCustomQWidget.setTextUp(index)
            myQCustomQWidget.setTextDown(name)
            myQCustomQWidget.setIcon(icon)
            # Create QListWidgetItem
            myQListWidgetItem = QtGui.QListWidgetItem(self.myQListWidget)
            # Set size hint
            myQListWidgetItem.setSizeHint(myQCustomQWidget.sizeHint())
            # Add QListWidgetItem into QListWidget
            self.myQListWidget.addItem(myQListWidgetItem)
            self.myQListWidget.setItemWidget(myQListWidgetItem, myQCustomQWidget)

        self.setCentralWidget(self.myQListWidget)

x = exampleQMainWindow()
x.show()
