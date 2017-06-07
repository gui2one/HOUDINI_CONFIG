#!python27
import hou
import os
import sys
# import inspect
#
# inspect.getfile(os)

sys.path.append("C:/Python27/Lib/site-packages/")

from PySide2 import QtWidgets
from PySide2.QtCore import *
from PySide2.QtGui import *


#
#
class MyCustomWidget(QtWidgets.QWidget):
    """A custom widget class that contains a label."""

    def __init__(self):

        self.rootPath = ""
        QtWidgets.QWidget.__init__(self)

        mainLayout = QtWidgets.QVBoxLayout()

        bottomLayout = QtWidgets.QHBoxLayout()

        btn1 = QtWidgets.QPushButton("btn1")
        btn2 = QtWidgets.QPushButton("btn2")

        bottomLayout.addWidget(btn1)
        bottomLayout.addWidget(btn2)
        # self.rootPath = hou.getenv("HIP")

        self.combo = QtWidgets.QComboBox()
        self.combo.addItem("JOB")
        self.combo.addItem("HIP")
        self.combo.addItem("choose folder ....")

        self.combo.activated.connect(self.comboChanged)

        reloadBtn = QtWidgets.QPushButton("Reload")
        reloadBtn.released.connect(self.reloadBtnClicked)

        self.listWidget = QtWidgets.QListWidget()
        # self.listWidget.resize(200,200)

        layout = QtWidgets.QVBoxLayout()

        layout.addWidget(reloadBtn)
        layout.addWidget(self.combo)
        layout.addWidget(self.listWidget)

        mainLayout.addLayout(layout)
        mainLayout.addLayout(bottomLayout)
        # layout.setAlignment(Qt.AlignTop)
        self.setLayout(mainLayout)

        # Apply Houdini styling to the main widget.
        self.setProperty("houdiniStyle", True)

    def comboChanged(self, index):
        # print "combo changed, index : ", index
        if index == 0:
            self.rootPath = hou.getenv("JOB")
        elif index == 1:
            self.rootPath = hou.getenv("HIP")
        elif index == self.combo.count() - 1:
            chosenPath = hou.ui.selectFile("", "select a project folder")
            self.rootPath = chosenPath
            # print '!!!!!!!!!!!!!!', self.rootPath
        # print self.combo.count()
        self.createList()

    def reloadBtnClicked(self):
        # print "clicked", self.rootPath
        pass

    def createList(self):
        files = os.listdir(self.rootPath)

        self.listWidget.clear()
        for f in files:
            if not os.path.isdir(os.path.join(proj, f)):
                if f.endswith('.hiplc') or f.endswith('.hip') or f.endswith('hipnc'):
                    self.listWidget.addItem(f)

        self.listWidget.doubleClicked.connect(self.openHipFile)

    def openHipFile(self, _file):
        hou.hipFile.load(os.path.join(self.rootPath, _file.data()))


proj = hou.getenv('JOB')


def createInterface():
    custom = MyCustomWidget()
    return custom
