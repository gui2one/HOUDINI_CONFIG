import sys
import atexit

sys.path.append("C:/Python27/Lib/site-packages")

# from PySide2 import QtCore, QtGui, QtWidgets
from PySide import QtGui





class myWindow(QtGui.QWidget):
	
	def __init__(self):
		global hipFilePath
		super(myWindow, self).__init__()

		self.hipFilePath = ""
		self.availableRops = []
		self.rop = None
		self.maxSamplesParm = None
		self.kernelIndex = -1
		self.kernelParm = None

		mainLayout = QtGui.QFormLayout()

		self.hipFileBtn = QtGui.QPushButton('Choose a .hip file', self)
		mainLayout.addRow("HIP File", self.hipFileBtn)
		# mainLayout.addWidget(self.hipFileBtn)

		self.hipFileBtn.clicked.connect(self.chooseHipFile)



		self.ropComboBox = QtGui.QComboBox(self)
		mainLayout.addRow("Choose ROP Driver:",self.ropComboBox)
		self.ropComboBox.activated.connect(self.setCurrentRop)
		# self.ropComboBox.move(0,25)


		self.kernelCB = QtGui.QComboBox(self)
		self.kernelCB.addItem("Direct")
		self.kernelCB.addItem("Path Tracer")
		self.kernelCB.addItem("PMC")
		self.kernelCB.addItem("Infos")
		self.kernelCB.setCurrentIndex(-1)
		self.kernelCB.activated.connect(self.chooseKernel)
		mainLayout.addRow("Kernel", self.kernelCB)


		self.maxSamplesSB = QtGui.QSpinBox()
		self.maxSamplesSB.setMaximum(10000000)
		# self.maxSamples.setValidator(QtGui.QIntValidator)

		mainLayout.addRow("Max Samples:",self.maxSamplesSB)
		

		self.renderBtn = QtGui.QPushButton('render', self)
		mainLayout.addWidget(self.renderBtn)
		# self.renderBtn.move(0,50)
		self.renderBtn.clicked.connect(self.launchRender);


		self.infosLabel = QtGui.QLabel("...")
		self.infosLabel.setStyleSheet("QLabel { background-color : white; color : red; }")
		mainLayout.addWidget(self.infosLabel)
		self.setGeometry(300, 300, 680, 380)
		self.setWindowTitle('Hython -- RENDER OCTANE SCENE') 

		
		frameRangeLabel = QtGui.QLabel("Frame Range")
		mainLayout.addWidget(frameRangeLabel)

		self.frameStartSB = QtGui.QSpinBox()
		self.frameStartSB.setMaximum(10000000)
		mainLayout.addRow("Start:",self.frameStartSB)

		self.frameEndSB = QtGui.QSpinBox()
		self.frameEndSB.setMaximum(10000000)
		mainLayout.addRow("End:",self.frameEndSB)	
			
		self.frameIncSB = QtGui.QSpinBox()
		self.frameIncSB.setMaximum(10000000)
		mainLayout.addRow("Increment:",self.frameIncSB)	


		self.setLayout(mainLayout)
		self.show()

	def chooseKernel(self, index):
		self.kernelIndex = index
		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())
		if index == 0:
			self.maxSamplesSB.setValue(renderTarget.parm("maxsamples").eval())
			self.maxSamplesParm = renderTarget.parm("maxsamples")
			
		elif index == 1:
			self.maxSamplesSB.setValue(renderTarget.parm("maxsamples2").eval())
			self.maxSamplesParm = renderTarget.parm("maxsamples2")
		elif index == 2:
			self.maxSamplesSB.setValue(renderTarget.parm("maxsamples3").eval())
			self.maxSamplesParm = renderTarget.parm("maxsamples3")
		elif index == 3:
			self.maxSamplesSB.setValue(renderTarget.parm("maxsamples4").eval())	
			self.maxSamplesParm = renderTarget.parm("maxsamples4")		

		print "chosen Kernel :", index

	def setCurrentRop(self, index):
		self.rop = self.availableRops[index]
		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())

		# set frame range
		self.frameStartSB.setValue(self.rop.parm("f1").eval() ) 
		self.frameEndSB.setValue(self.rop.parm("f2").eval() ) 
		self.frameIncSB.setValue(self.rop.parm("f3").eval()	 ) 

		if renderTarget != None :
			kID = renderTarget.parm("parmKernel").eval()
			self.kernelCB.setCurrentIndex(kID)
			self.infosLabel.setText("")
			self.chooseKernel(kID)


			

		else:

			self.infosLabel.setText("no renderTarget defined in this driver")



	def chooseHipFile(self):

		dialog = QtGui.QFileDialog(self)
		# dialog.setFileMode(QtGui.QFileDialog.DirectoryOnly)
		# dialog.setOption(QtGui.QFileDialog.ShowDirsOnly)   
		if dialog.exec_() :
			self.hipFilePath = dialog.selectedFiles()[0]					
			self.loadHipFile()

			self.hipFileBtn.setText(dialog.selectedFiles()[0])
			# print hipFilePath

	def loadHipFile(self):
		self.infosLabel.setText("")	
		hou.hipFile.clear()
		self.ropComboBox.clear()
		# self.kernelCB.clear()
		self.rop = None
		self.maxSamplesParm = None
		self.availableRops = []
		self.kernelIndex = -1
		hou.hipFile.load(self.hipFilePath)
		hou.cd('/out')
		for child in hou.pwd().children():
			if child.type().name() == "Octane_ROP":
				self.availableRops.append(hou.node(child.path()))
				self.ropComboBox.addItem(child.name())

		if len(self.availableRops) > 0:
			self.ropComboBox.setCurrentIndex(0)
			
			self.setCurrentRop(0)

		else:
			self.infosLabel.setText("No Octane driver detected")			
					
		
	def launchRender(self):

		self.rop.parm("HO_renderToMPlay").set(0)

		# override render resolution
		self.rop.parm('HO_overrideCameraRes').set(1)
		self.rop.parm('HO_overrideResScale').set(7)

		self.rop.parm('HO_overrideRes1').deleteAllKeyframes()
		self.rop.parm('HO_overrideRes2').deleteAllKeyframes()

		self.rop.parm('HO_overrideRes1').set(1280)
		self.rop.parm('HO_overrideRes2').set(720)

		#set render begin frame number
		self.rop.parm("f1").deleteAllKeyframes()
		self.rop.parm("f2").deleteAllKeyframes()
		self.rop.parm("f3").deleteAllKeyframes()
		self.rop.parm("f1").set(self.frameStartSB.value())
		self.rop.parm("f2").set(self.frameEndSB.value())
		self.rop.parm("f3").set(self.frameIncSB.value())

		# set render frame range : 1 or 2(strict) , or 0 for single frame
		self.rop.parm('trange').set(1)
		hou.setFrame(50)		

		print "!!!!!!!!!!!!! : ",self.maxSamplesSB.value()
		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())
		print renderTarget.path()
		renderTarget.parm("parmKernel").set(self.kernelIndex)
		self.maxSamplesParm.set(self.maxSamplesSB.value())

		hscript = hou.hscript('Octane_setGPU -g 1 -s 1 -p 0')
		# print hscript

		# press render button on the driver node itself
		self.rop.parm("execute").pressButton()
		

		print "R E N D E R I N G ....."

if __name__ == '__main__':

    # import sys

    app = QtGui.QApplication(sys.argv)
    window = myWindow()
    # window.show()
    # sys.exit(app.exec_())
    atexit.register(app.exec_)
    # sys.exit(0)

