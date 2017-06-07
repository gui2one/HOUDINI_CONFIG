import sys

sys.path.append("C:/Python27/Lib/site-packages/")

from PySide2 import QtWidgets, QtGui


class CustomWidget(QtWidgets.QWidget):

    def __init__(self):
        QtWidgets.QWidget.__init__(self)


        mainLayout = QtWidgets.QVBoxLayout()

        topLayout = QtWidgets.QVBoxLayout()

        groupBox = QtWidgets.QGroupBox()

        bottomLayout = QtWidgets.QVBoxLayout()
        self.addTrunkBtn = QtWidgets.QPushButton("Add a trunk")

        self.addBranchesBtn = QtWidgets.QPushButton("Add branches")

        topLayout.addStretch(0)
        topLayout.addWidget(self.addTrunkBtn)
        topLayout.addWidget(self.addBranchesBtn)
        groupBox.setLayout(topLayout)


        topLayout.addStretch(1)
        mainLayout.addWidget(groupBox)
        mainLayout.addLayout(bottomLayout)
        self.setLayout(mainLayout)
        # self.setMinimumHeight(20)


        # self.setSizePolicy( QtWidgets.QSizePolicy.Fixed,QtWidgets.QSizePolicy.Fixed)
        self.resize(100,200)

        self.setStyleSheet("border: 1px solid grey")

        self.setProperty("houdiniStyle", True)

        # print self

