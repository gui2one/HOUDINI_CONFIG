s = hou.selectedNodes()[0]
root = s.parent()

def findLights():
    lightPlanes = []
    print "Find Lights Function ----"
    for i in range(nPlanes):
        plane = s.planes()[i]
    
        ### if it's an "light" plane
        if plane.find("obj_") != -1:
            lightPlanes.append(plane)
            
    print len(lightPlanes), "Light Planes"
    
    nameArray = []
    
    for lightPlane in lightPlanes:
        lightName = lightPlane.split("_")[1]
        if not lightName in nameArray:
            nameArray.append(lightName)    

    return nameArray
            
            
            
myPlanes = ()
nPlanes = len(s.planes())
print nPlanes


lights = findLights()
colors = []
colors.append(hou.Color((255,0,0)))
colors.append(hou.Color((0,255,0)))
colors.append(hou.Color((0,0,255)))
colors.append(hou.Color((255,255,0)))

inc = 0
for light in lights:
    nodes = []
    for plane in s.planes():
        if plane.find(light) != -1 and plane.find("coat") == -1  and plane.find("reflect") == -1:
            extract = root.createNode("gui2one_COP_extract_channel")
            nodes.append(extract)
            extract.setInput(0,s)
            extract.setColor(colors[inc % 4])
            extract.parm("plane_name").set(plane)
            extract.setName(light +"__"+ plane.split("_")[2] + "__" +plane.split("_")[3])
            
    inc += 1
    
    
    for i in range(len(nodes)-1):
        addNode = root.createNode("add")
        
        if i == 0:
            addNode.setInput(0,nodes[i])
            addNode.setInput(1,nodes[i+1])
            oldAdd = addNode
        else:
            addNode.setInput(0, oldAdd    )
            addNode.setInput(1,nodes[i+1])
            oldAdd = addNode

inc = 0
for light in lights:
    nodes = []
    for plane in s.planes():
        if plane.find(light) != -1 :
            if plane.find("coat") != -1 or plane.find("reflect") != -1:
                extract = root.createNode("gui2one_COP_extract_channel")
                nodes.append(extract)
                extract.setInput(0,s)
                extract.setColor(colors[inc % 4])
                extract.parm("plane_name").set(plane)
                extract.setName(light +"__"+ plane.split("_")[2] + "__" +plane.split("_")[3])
            
    inc += 1
    
    
    for i in range(len(nodes)-1):
        addNode = root.createNode("add")
        
        if i == 0:
            addNode.setInput(0,nodes[i])
            addNode.setInput(1,nodes[i+1])
            oldAdd = addNode
        else:
            addNode.setInput(0, oldAdd    )
            addNode.setInput(1,nodes[i+1])
            oldAdd = addNode            
       