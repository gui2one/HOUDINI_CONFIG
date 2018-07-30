import sys

import hou

hou.hipFile.load('D:/WORK/HOUDINI_16_playground/hython_test.hiplc')

# hou.setFrame(101)
hou.cd('/out')

octaneRops = []

for child in hou.pwd().children():
	if child.type().name() == 'Octane_ROP':
		octaneRops.append(child)

print "octaneRops : "
for i, rop in enumerate(octaneRops):
	print "\t",i, " : ",rop,"\n"


userInput = raw_input("chose a Octane ROP Driver:")

print userInput
rop = hou.pwd().children()[int(userInput)]

rTarget = hou.node(rop.parm("HO_renderTarget").evalAsString())

rTarget.parm("maxsamples").set(500)

# disable mplay rendering
rop.parm("HO_renderToMPlay").set(1)

# override render resolution
rop.parm('HO_overrideCameraRes').set(1)
rop.parm('HO_overrideResScale').set(7)

rop.parm('HO_overrideRes1').deleteAllKeyframes()
rop.parm('HO_overrideRes2').deleteAllKeyframes()

rop.parm('HO_overrideRes1').set(960)
rop.parm('HO_overrideRes2').set(540)

#set render begin frame number
rop.parm("f1").deleteAllKeyframes()
rop.parm("f2").deleteAllKeyframes()
rop.parm("f3").deleteAllKeyframes()
rop.parm("f1").set(102)
rop.parm("f2").set(103)
rop.parm("f3").set(1)

# set render frame range : 1 or 2(strict) , or 0 for single frame
rop.parm('trange').set(1)
hou.setFrame(50)

#print "ROP : ", hou.getenv('HIP')
# press render button
rop.parm('execute').pressButton()

print "rendering task FINISHED, good bye ...."


# sys.exit(0)