import sys
import atexit

sys.path.append("C:/Python27/Lib/site-packages")

# from PySide2 import QtCore, QtGui, QtWidgets
from PySide import QtGui


class myWindow(QtGui.QWidget):

	def __init__(self):

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
		mainLayout.addRow("Choose ROP Driver:", self.ropComboBox)
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

		mainLayout.addRow("Max Samples:", self.maxSamplesSB)

		self.disablePassesToggle = QtGui.QCheckBox()
		mainLayout.addRow("Disable Passes:", self.disablePassesToggle)

		self.renderBtn = QtGui.QPushButton('render', self)
		mainLayout.addWidget(self.renderBtn)
		# self.renderBtn.move(0,50)
		self.renderBtn.clicked.connect(self.launchRender);

		self.infosLabel = QtGui.QLabel("...")
		self.infosLabel.setStyleSheet("QLabel { background-color : white; color : red; }")
		mainLayout.addWidget(self.infosLabel)
		self.setGeometry(300, 300, 680, 380)
		self.setWindowTitle('Hython -- RENDER OCTANE SCENE')

		self.renderToMPlayToggle = QtGui.QCheckBox()
		mainLayout.addRow("Render to MPlay:", self.renderToMPlayToggle)

		self.overwriteMPlayToggle = QtGui.QCheckBox()
		mainLayout.addRow("Overwrite Mplay Frame:", self.overwriteMPlayToggle)

		frameRangeLabel = QtGui.QLabel("Frame Range")
		mainLayout.addWidget(frameRangeLabel)

		self.frameStartSB = QtGui.QSpinBox()
		self.frameStartSB.setMaximum(10000000)
		mainLayout.addRow("Start:", self.frameStartSB)

		self.frameEndSB = QtGui.QSpinBox()
		self.frameEndSB.setMaximum(10000000)
		mainLayout.addRow("End:", self.frameEndSB)

		self.frameIncSB = QtGui.QSpinBox()
		self.frameIncSB.setMaximum(10000000)
		mainLayout.addRow("Increment:", self.frameIncSB)

		self.outputImageFilesToggle = QtGui.QCheckBox()
		mainLayout.addRow("Output image Files:", self.outputImageFilesToggle)

		self.createDirectoriesToggle = QtGui.QCheckBox()
		mainLayout.addRow("Create Directories:", self.createDirectoriesToggle)

		self.outputFilePath = QtGui.QLineEdit()
		mainLayout.addRow("Output File Path:", self.outputFilePath)

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

		# print "chosen Kernel :", index

	def setCurrentRop(self, index):
		self.rop = self.availableRops[index]
		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())

		self.renderToMPlayToggle.setChecked(self.rop.parm("HO_renderToMPlay").eval())
		self.overwriteMPlayToggle.setChecked(self.rop.parm("HO_overwriteMPlay").eval())

		# set frame range
		self.frameStartSB.setValue(self.rop.parm("f1").eval())
		self.frameEndSB.setValue(self.rop.parm("f2").eval())
		self.frameIncSB.setValue(self.rop.parm("f3").eval()	)



		self.outputFilePath.setText( self.rop.parm("HO_img_fileName").unexpandedString())

		self.outputImageFilesToggle.setChecked( self.rop.parm("HO_img_enable").eval())
		self.createDirectoriesToggle.setChecked( self.rop.parm("HO_img_createDir").eval())

		if renderTarget != None :
			kID = renderTarget.parm("parmKernel").eval()
			self.kernelCB.setCurrentIndex(kID)
			self.infosLabel.setText("")
			self.chooseKernel(kID)

			self.disablePassesToggle.setChecked( renderTarget.parm("enablePassesNode").eval() )




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

		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())
		renderTarget.parm("enablePassesNode").set(self.disablePassesToggle.isChecked())

		# # baking Keyframe because of a bug of frame interpolation ... might not be necessary ...

		# camera = hou.node( self.rop.parm("HO_renderCamera").eval())
		# # print "camera .... :", camera
		# self.bakeKeyframes(camera)

		self.rop.parm("HO_renderToMPlay").set(self.renderToMPlayToggle.isChecked())
		self.rop.parm("HO_overwriteMPlay").set(self.overwriteMPlayToggle.isChecked())

		# override render resolution
		self.rop.parm('HO_overrideCameraRes').set(1)
		self.rop.parm('HO_overrideResScale').set(3)

		self.rop.parm('HO_overrideRes1').deleteAllKeyframes()
		self.rop.parm('HO_overrideRes2').deleteAllKeyframes()

		self.rop.parm('HO_overrideRes1').set(1280)
		self.rop.parm('HO_overrideRes2').set(720)

		# set render begin frame number
		self.rop.parm("f1").deleteAllKeyframes()
		self.rop.parm("f2").deleteAllKeyframes()
		self.rop.parm("f3").deleteAllKeyframes()
		self.rop.parm("f1").set(self.frameStartSB.value())
		self.rop.parm("f2").set(self.frameEndSB.value())
		self.rop.parm("f3").set(self.frameIncSB.value())



		self.rop.parm("HO_img_enable").set(self.outputImageFilesToggle.isChecked())

		self.rop.parm("HO_img_createDir").set(self.createDirectoriesToggle.isChecked())

		self.rop.parm("HO_img_fileName").set( self.outputFilePath.text())

		self.rop.parm("HO_img_fileFormat").set(2) ## 2 --> PNG 8 bits



		# set render frame range : 1 or 2(strict) , or 0 for single frame
		self.rop.parm('trange').set(1)
		# for single frame rendering
		hou.setFrame(50)

		# print "!!!!!!!!!!!!! : " ,self.maxSamplesSB.value()
		renderTarget = hou.node(self.rop.parm("HO_renderTarget").eval())
		# print renderTarget.path()
		renderTarget.parm("parmKernel").set(self.kernelIndex)
		self.maxSamplesParm.set(self.maxSamplesSB.value())

		hou.hscript('Octane_setGPU -g 0 -s 1 -p 0')
		hou.hscript('Octane_setGPU -g 1 -s 1 -p 0')


		# # press render button on the driver node itself
		self.rop.parm("execute").pressButton()


		print "R E N D E R I N G    F I N I S H E D ....."

	def bakeKeyframes(self, node):
		animatedParms = []

		frameRange = range(int(self.frameStartSB.value()), int(self.frameEndSB.value()) + 1, 1)

		# print frameRange

		obj = node
		# print obj.name()

		bakeNull = hou.node("/obj/").createNode("null")
		# print hou.node("baking_null_" + obj.name())
		if hou.node("/obj/baking_null_" + obj.name()) != None:
			# print "hey"
			hou.node("/obj/baking_null_" + obj.name()).destroy()
		bakeNull.setName("baking_null_" + obj.name())
		bakeNull.moveToGoodPosition()

		for parm in obj.parms():
			if len(parm.keyframes()) > 1:
				animatedParms.append(parm)

		# print animatedParms

		keyframes_TX = []
		keyframes_TY = []
		keyframes_TZ = []

		keyframes_RX = []
		keyframes_RY = []
		keyframes_RZ = []

		for i in frameRange:
			time = float(i - 1) / hou.fps()

			tr = obj.worldTransformAtTime(time).extractTranslates()
			#        print i, " ----- " , tr.x()
			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(tr.x())
			keyframes_TX.append(key)

			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(tr.y())
			keyframes_TY.append(key)

			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(tr.z())
			keyframes_TZ.append(key)

			rot = obj.worldTransformAtTime(time).extractRotates()

			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(rot.x())
			keyframes_RX.append(key)

			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(rot.y())
			keyframes_RY.append(key)

			key = hou.Keyframe()
			key.setTime(time)
			key.setValue(rot.z())
			keyframes_RZ.append(key)


		# print keyframes_TX

		bakeNull.parm("tx").setKeyframes(keyframes_TX)
		bakeNull.parm("ty").setKeyframes(keyframes_TY)
		bakeNull.parm("tz").setKeyframes(keyframes_TZ)

		bakeNull.parm("rx").setKeyframes(keyframes_RX)
		bakeNull.parm("ry").setKeyframes(keyframes_RY)
		bakeNull.parm("rz").setKeyframes(keyframes_RZ)

		# # transfer keyframes to original object
		# # unparent before



		obj.parm("tx").deleteAllKeyframes()
		obj.parm("tx").setKeyframes(keyframes_TX)

		obj.parm("ty").deleteAllKeyframes()
		obj.parm("ty").setKeyframes(keyframes_TY)

		obj.parm("tz").deleteAllKeyframes()
		obj.parm("tz").setKeyframes(keyframes_TZ)

		obj.parm("rx").deleteAllKeyframes()
		obj.parm("rx").setKeyframes(keyframes_RX)

		obj.parm("ry").deleteAllKeyframes()
		obj.parm("ry").setKeyframes(keyframes_RY)

		obj.parm("rz").deleteAllKeyframes()
		obj.parm("rz").setKeyframes(keyframes_RZ)

		obj.setInput(0, None)

if __name__ == '__main__':

	# import sys

	app = QtGui.QApplication(sys.argv)
	window = myWindow()
	# window.show()
	# sys.exit(app.exec_())
	atexit.register(app.exec_)
# sys.exit(0)
