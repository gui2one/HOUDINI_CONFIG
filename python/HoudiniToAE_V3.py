import json
import math
import os

### functions
def isZoomTimeDependent(cam):
    parmList = [ 'focal', 'aperture']
    
    for parm in parmList:
        if cam.parm(parm).isTimeDependent():
            return True
            
    return False

def getCamZoomAtFrame(cam, frame=1):
    resx = cam.parm('resx').evalAtFrame(frame)
    resy = cam.parm('resy').evalAtFrame(frame)
    aspect = cam.parm('aspect').evalAtFrame(frame)
    aperture = cam.parm('aperture').evalAtFrame(frame)
    focal = cam.parm('focal').evalAtFrame(frame)
    fovx = 2 * math.atan((aperture/2)/focal) 
    zoom = ((resx/2)/math.tan(fovx/2)) 
    
    return zoom

def getTransformsAtFrame(obj, frame=1):
    hou.setFrame(frame)
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
    
    return([tx,ty,tz], [rx,ry,rz])
        
        
### actual code 

sel = hou.selectedNodes()

tStart = int(hou.expandString('$RFSTART'))
tEnd = int(hou.expandString('$RFEND'))

nodes = {}

cam = None

for node in sel:
    if node.type().name() == 'cam':
        cam = node
        break

        
### file selection 
dirPath = hou.expandString('$HIP')
fileName = hou.ui.selectFile( start_directory = dirPath,
        default_value = "%s_export.h2ae" % (cam.name()),
        file_type = hou.fileType.Any,
        collapse_sequences = False,
        multiple_select = False,
        image_chooser   = False)
        
print( fileName)

data = {}
compInfos = {}
compInfos["name"] = cam.name()
compInfos["resx"] = cam.parm('resx').eval()
compInfos["resy"] = cam.parm('resy').eval()    
compInfos["fps"] = hou.fps()
compInfos["fStart"] = hou.expandString('$RFSTART')   
compInfos["fEnd"] = hou.expandString('$RFEND')

data["compInfos"] = compInfos

for node in sel:

    
    infos = {}
    if node.type().name() == 'cam' :
    
        camInfos = {}
        if not isZoomTimeDependent(node):
            camInfos["zoom"] = [getCamZoomAtFrame(node)]
            infos["camInfos"] = camInfos
            
        else:
            zoom = []
            for i in range(tStart, tEnd+1):
                zoom.append(getCamZoomAtFrame(node,i))
            camInfos["zoom"] = zoom
            infos["camInfos"] = camInfos
        
   
        
    positions = []
    rotations = []    
    
    if node.isTimeDependent() :
        for i in range(tStart, tEnd+1):
            pos, rot = getTransformsAtFrame(node,i)
            positions.append(pos)
            rotations.append(rot)
    else:
        pos, rot = getTransformsAtFrame(node)
        positions.append(pos)
        rotations.append(rot)        
        
    infos["positions"] = positions 
    infos["rotations"] = rotations
    nodes[node.name()] = infos

data["layers"] = nodes
    

    
    
jsonData = json.dumps(data, sort_keys=True, indent=4, separators=(',', ': '))
# jsonData = json.dumps(nodes)

with open(fileName,'w') as f:
    #json.dump(data,f, sort_keys=True, indent=4, separators=(',', ': '))
    json.dump(data, f)

print( 'just written a file at : ', fileName)


