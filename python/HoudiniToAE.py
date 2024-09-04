# This script exports Houdini objects to Adobe After Effects 8.x
# A .jsx file will be created
# You can run it as a script in AE
# ver 0.01 Andrew V.K.

import toolutils
import hou 
import string
import math

viewer = toolutils.sceneViewer()
objsel = viewer.selectObjects("Select objects and press Enter",
        use_existing_selection=False,
        allow_multisel = True,
        quick_select=True,
        allowed_types = ('cam','hlight','null','geo','subnet'))

dir = hou.expandString('$HIP')
hip = hou.expandString('$HIPNAME')
dirpath = dir + '/' + hip + '.jsx'
fname = hou.ui.selectFile( start_directory = dirpath,
        file_type = hou.fileType.Any,
        collapse_sequences = False,
        multiple_select = False,
        image_chooser   = False)
if not fname.endswith('.jsx'):
	fname = fname + '.jsx'
fp = open(fname,'w')

fps = hou.fps()
duration = hou.expandString('$TLENGTH')
fend = string.atoi(hou.expandString('$FEND'))
fstart = string.atoi(hou.expandString('$FSTART'))
firstCam = 0
objCamera = []
objLight = []
objNull = []

for obj in objsel:
    name = obj.name()
    objType = obj.type().name()
    if objType == 'cam':
        resx = obj.parm('resx').eval()
        resy = obj.parm('resy').eval()
        aspect = obj.parm('aspect').eval()
        aperture = obj.parm('aperture').eval()
	focal = obj.parm('focal').eval()
	fovx = 2 * math.atan((aperture/2)/focal) 
	zoom = ((resx/2)/math.tan(fovx/2))
	if firstCam == 0:
        	objCamera.append('var myItemCollection = app.project.items;\n')
        	objCamera.append('var myComp = myItemCollection.addComp("'+name+'"'+','+`resx`+','+`resy`+','+`aspect`+','+duration+','+`fps`+');\n')
        	objCamera.append('var SceneScaleNull = myComp.layers.addNull();\n')
        	objCamera.append('SceneScaleNull.threeDLayer = true;\n')
        	objCamera.append('SceneScaleNull.name = "Scene Scale";\n')
        	objCamera.append('SceneScaleNull.property("Position").setValue([0.0,0.0,0.0]);\n')
        	objCamera.append('SceneScaleNull.enabled = false;\n')
		firstCam = 1
        objCamera.append('var '+name+' = myComp.layers.addCamera("'+name+'",[0,0]);\n')
        objCamera.append(name+'.autoOrient = AutoOrientType.NO_AUTO_ORIENT;\n')
        objCamera.append(name+'.property("Zoom").setValue('+`zoom`+');\n') 
        objCamera.append(name+'.parent = SceneScaleNull;\n')
    elif objType == 'hlight':
	lighttype = obj.parm('light_type').eval()
	intensity = obj.parm('light_intensity').eval()
	cr = obj.parm('light_colorr').eval()
	cg = obj.parm('light_colorg').eval()
	cb = obj.parm('light_colorb').eval()
	coneangle = obj.parm('coneangle').eval()
	shadow = obj.parm('shadow_type').eval()
        objLight.append('var '+name+' = myComp.layers.addLight("'+name+'",[0,0]);\n')
        objLight.append(name+'.autoOrient = AutoOrientType.NO_AUTO_ORIENT;\n')
        objLight.append(name+'.property("Intensity").setValue('+`intensity*100`+');\n') 
        objLight.append(name+'.property("Color").setValue(['+`cr`+','+`cg`+','+`cb`+']);\n') 
	if shadow > 0:
        	objLight.append(name+'.property("castsShadows").setValue(1);\n') 
	if lighttype == 1:
        	objLight.append(name+'.property("coneAngle").setValue('+`coneangle`+');\n') 
        objLight.append(name+'.parent = SceneScaleNull;\n')
    else:
        objNull.append('var '+name+' = myComp.layers.addNull()\n')
        objNull.append(name+'.threeDLayer = true;\n') 
        objNull.append(name+'.name = "'+name+'";\n')
        objNull.append(name+'.parent = SceneScaleNull;\n')

if firstCam == 0:
	fp.write('var myItemCollection = app.project.items;\n')
	fp.write('var myComp = myItemCollection.addComp("Camera1",640,480,1,%s,%s);\n'%(duration,fps))
	fp.write('var myCamera = myComp.layers.addCamera("Camera1",[0,0]);\n')
	fp.write('myCamera.autoOrient = AutoOrientType.NO_AUTO_ORIENT;\n')
	fp.write('var SceneScaleNull = myComp.layers.addNull();\n')
	fp.write('SceneScaleNull.threeDLayer = true;\n')
	fp.write('SceneScaleNull.name = "Scene Scale";\n')
	fp.write('SceneScaleNull.property("Position").setValue([0.0,0.0,0.0]);\n')
	fp.write('SceneScaleNull.enabled = false;\n')
	fp.write('myCamera.parent = SceneScaleNull;\n')
for x in objCamera:
   fp.write('%s'%x)
for x in objLight:
   fp.write('%s'%x)
for x in objNull:
   fp.write('%s'%x)

i = fstart
while i <= fend:
   	hou.setFrame(i)
   	ftime = hou.frameToTime(i)
   	for obj in objsel:
      	    name = obj.name()
      	    objType = obj.type().name()
            wtm = obj.worldTransform()
            objt = wtm.extractTranslates("srt")
	    tx = objt.__getitem__(0)
	    ty = objt.__getitem__(1) * -1
	    tz = objt.__getitem__(2) * -1
            objr = wtm.extractRotates("srt","zyx")
	    rx = objr.__getitem__(0)
	    ry = objr.__getitem__(1) * -1
	    rz = objr.__getitem__(2) * -1
	    fp.write('%s.property("X Rotation").setValueAtTime(%f,%f);\n'%(name,ftime,rx)) 
	    fp.write('%s.property("Y Rotation").setValueAtTime(%f,%f);\n'%(name,ftime,ry)) 
	    fp.write('%s.property("Z Rotation").setValueAtTime(%f,%f);\n'%(name,ftime,rz)) 
	    fp.write('%s.property("Position").setValueAtTime(%f,[%f,%f,%f]);\n'%(name,ftime,tx,ty,tz)) 
    	    if (objType == 'cam') and (len(obj.parm('focal').keyframes()) != 0):
        	resx = obj.parm('resx').eval()
        	resy = obj.parm('resy').eval()
        	aspect = obj.parm('aspect').eval()
        	aperture = obj.parm('aperture').eval()
		focal = obj.parm('focal').eval()
		fovx = 2 * math.atan((aperture/2)/focal) 
		zoom = ((resx/2)/math.tan(fovx/2))
		fp.write('%s.property("Zoom").setValueAtTime(%f,%f);\n'%(name,ftime,zoom)) 
    	    if objType == 'hlight':
		if len(obj.parm('light_intensity').keyframes()) != 0:
		   intensity = obj.parm('light_intensity').eval()
		   fp.write('%s.property("Intensity").setValueAtTime(%f,%f);\n'%(name,ftime,intensity*100)) 
		if len(obj.parm('coneangle').keyframes()) != 0:
		   coneangle = obj.parm('coneangle').eval()
		   fp.write('%s.property("coneAngle").setValueAtTime(%f,%f);\n'%(name,ftime,coneangle)) 
		kr = len(obj.parm('light_colorr').keyframes())
		kg = len(obj.parm('light_colorg').keyframes())
		kb = len(obj.parm('light_colorb').keyframes())
		if (kr != 0) or (kg != 0) or (kb != 0):
		   cr = obj.parm('light_colorr').eval()
		   cg = obj.parm('light_colorg').eval()
		   cb = obj.parm('light_colorb').eval()
	           fp.write('%s.property("Color").setValueAtTime(%f,[%f,%f,%f]);\n'%(name,ftime,cr,cg,cb)) 
    	    if (objType == 'geo') or (objType == 'null') or (objType == 'subnet'):
                objs = wtm.extractScales("srt")
	        sx = objs.__getitem__(0)
	        sy = objs.__getitem__(1)
	        sz = objs.__getitem__(2)
	        fp.write('%s.property("Scale").setValueAtTime(%f,[%f,%f,%f]);\n'%(name,ftime,sx,sy,sz)) 
	i = i + 1
fp.close()
hou.setFrame(fstart)
	