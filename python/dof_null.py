if hou.selectedNodes().__len__() > 0 : 
    c = hou.selectedNodes()[0]
    if c.type().name() == "cam" :
        root = c.parent()
        nullNode = root.createNode("null")
        nullNode.setName(c.name() + "_dof_null")
        nullNode.setPosition((c.position()[0], c.position()[1]-0.6))
        nullNode.parm("dcolorr").set(0.9)
        nullNode.parm("dcolorg").set(0.9)
        nullNode.parm("dcolorb").set(0.0)
        
        nullNode.parm("controltype").set(4)
        
        #################
        chopnet = root.createNode("chopnet")
        chopnet.setName(c.name()+"_chopnet")
        chopnet.setPosition((c.position()[0], c.position()[1]-1.1))
        nullObjNode = chopnet.createNode("object")
        nullObjNode.setName("dof_null_position")
        nullObjNode.parm("targetpath").set(nullNode.path())
        
        camObjNode = chopnet.createNode("object")
        camObjNode.setName("cam_position")
        camObjNode.parm("targetpath").set(c.path())        
        
        exp = 'distance('
        exp += 'chop("'+ camObjNode.path()+'/tx"),'
        exp += 'chop("'+ camObjNode.path()+'/ty"),'
        exp += 'chop("'+ camObjNode.path()+'/tz"),'        
        exp += 'chop("'+ nullObjNode.path()+'/tx"),'
        exp += 'chop("'+ nullObjNode.path()+'/ty"),'
        exp += 'chop("'+ nullObjNode.path()+'/tz"))'
        c.parm("focus").setExpression(exp)
        #print nullNode
    else :
        hou.ui.displayMessage("select a camera node")        
else :
    hou.ui.displayMessage("select a camera")
