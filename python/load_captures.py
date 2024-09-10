import os
import glob
import collections

sel =  hou.selectedNodes()[0]
root = sel.parent()



### get bounds of selected geometry
geoBounds = sel.geometry().boundingBox()

### get data on disk
os.chdir("F:/PYTHON_playground/misc/google_maps/captures")

pngFiles =  glob.glob("*.png")
txtFiles =  glob.glob("*.txt")



dataDict = {}
for txt in txtFiles : 
    bboxValues = []
    f = open(txt,"r")
    content = f.read()
    
    f.close()
    
    data = content.split(",")
    bounds = []
    inc = 0
    for item in data:
        bounds.append(item.translate(None, '{ }').split(":")[1])
        bounds[inc] = float(bounds[inc])
        inc += 1
        
    dataDict[txt.replace(".txt","")] = bounds   


sortedData = collections.OrderedDict(sorted(dataDict.items()))    
#print(len(dataDict))
chosenDict = {}
chosenKeyArray = []
mapInc = 0
for item in sortedData :
    if sortedData[item][0] > 45.0 and sortedData[item][0] < 46.0 :
        if sortedData[item][1] > 6.0 and sortedData[item][1] < 7.0 :
            chosenDict[item] = sortedData[item]
            chosenKeyArray.append(item)
            mapInc += 1
        
        
print (" nombre de captures selectionnées : %d "% len(chosenDict))
print geoBounds


try : 
    hou.node(root.path() + "/sattelite_shader").destroy()
except:
    print "nothing to destroy"
    
### create shopnet
shopnet = root.createNode("shopnet")
shopnet.setName("sattelite_shader")

### create vopmaterial

vopMat = shopnet.createNode("vopmaterial")
vopMat.setName("sattelite_shader")

### create texture vops
inc = 0
for item in chosenDict :
    texVop = vopMat.createNode("texture")
    texVop.setName(item)
    texVop.parm("map").set("F:/PYTHON_playground/misc/google_maps/captures/"+ item +".png")
    texVop.parm("wrap").set("decal")
    surfGlob = hou.node(vopMat.path() + "/surface_globals")
    #print surfGlob.outputs()
    
    ### vector to float    
    vecToFloat = vopMat.createNode("vectofloat")
    texVop.setInput(2,vecToFloat,0)
    texVop.setInput(3,vecToFloat,2)  
    
    
    ### xform
    xForm = vopMat.createNode("xform")
    vecToFloat.setInput(0,xForm,0)
    inc += 1
    
    ### transform
    transform = vopMat.createNode("transform")
    xForm.setInput(0, transform,0)
    
    transform.setInput(0,surfGlob,3)
    
    S = chosenDict[item][0]
    E = chosenDict[item][1]
    W = chosenDict[item][2]
    N = chosenDict[item][3]    
    
    
    xForm.parm("trs").set(4) ### Trans Scale Rotate
    
    xParm = 1/(E-W)
    zParm = 1/(S-N)
    xForm.parm("scale1").set(xParm)
    xForm.parm("scale3").set(zParm)
    
    xForm.parm("trans3").set(1-(S-N))
    
