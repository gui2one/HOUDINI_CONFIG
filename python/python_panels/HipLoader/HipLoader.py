import hou
from PySide2 import QtWidgets

class HipLoader( QtWidgets.QWidget):

    def __init__(self):
        super(HipLoader, self).__init__()

        self.button = QtWidgets.QPushButton("cool ?")
        self.createInterface()

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget( self.button)

        self.setLayout(mainLayout)

    def buttonClicked(self):
        
        print "ha !!!!"
        hou.hipFile.load("D:/WORK/HOUDINI_16_5_playground/aaa.hiplc")

    def createInterface(self):         

        self.button.clicked.connect( self.buttonClicked)


