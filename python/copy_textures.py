import os
import shutil


chosenPath = hou.ui.selectFile("","select a folder to copy file into")
hipPath = hou.expandString(chosenPath)
#print os.path.abspath(hipPath)
#print chosenPath

sel = hou.selectedNodes()

filesToCopy = []
linksDict = {}

for node in sel:
    for child in node.children():
    
        if child.type().name() == "octane::NT_TEX_IMAGE" or child.type().name() == "octane::NT_TEX_FLOATIMAGE" or child.type().name() == "octane::NT_TEX_ALPHAIMAGE":
    
            filePath = child.parm("A_FILENAME").eval()
            
            if not filePath in filesToCopy:
                filesToCopy.append(filePath)
            
    #print filesToCopy
    
    ### copy files to chosen directory
    for file in filesToCopy:
        shutil.copy2(file, hipPath)
        linksDict[ file ] = str(hipPath)+ str(os.path.basename(file))
        
        
    
    
    ### loop back through texture node in octane network to update image file paths
    for child in node.children():
    
        if child.type().name() == "octane::NT_TEX_IMAGE" or child.type().name() == "octane::NT_TEX_FLOATIMAGE" or child.type().name() == "octane::NT_TEX_ALPHAIMAGE":
            filePath = child.parm("A_FILENAME").eval()
            
            expandedHipString = hou.expandString("$HIP")
            newPath = linksDict[filePath].replace( expandedHipString, "$HIP")
            child.parm("A_FILENAME").set(newPath)
        
    
    
    
    
    
    
