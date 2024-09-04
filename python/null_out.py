import sys

if(hou.selectedNodes().__len__() > 0):

    sel = hou.selectedNodes()[0]
    #print sel.outputs()
else:
    hou.ui.displayMessage("Select a node")
    # if selection is empty exit the tool
    sys.exit()
    

#print sel.children()   

nullNode = sel.parent().createNode("null")
nullNode.setName("OUT", True)
nullNode.setColor(hou.Color((1.0,0.0,0.0)))



for conn in sel.outputConnections():
    index = conn.inputIndex()
    outputNode = conn.outputNode()
    outputNode.setInput(index,nullNode)
    #print outputNode.name
  
nullNode.insertInput(0,sel)    

nullNode.moveToGoodPosition()

nullNode.setDisplayFlag(1)
nullNode.setRenderFlag(1)
nullNode.setTemplateFlag(1)