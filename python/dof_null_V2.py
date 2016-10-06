if hou.selectedNodes().__len__() == 1:
    selectedNode = hou.selectedNodes()[0]
    if selectedNode.type().name() == 'cam' :
        cam = selectedNode
        
        if cam.parm('dof_target') == None :
            group = cam.parmTemplateGroup()
            
            template = hou.StringParmTemplate('dof_target','dof target',1)
            template.setStringType(hou.stringParmType.NodeReference)
            
            trans= group.findFolder('Transform')
            group.insertBefore(trans,template)
            
            cam.setParmTemplateGroup(group)
        
            

        nullNode = cam.parent().createNode('null')
        nullNode.setName('dof_null_'  + cam.name())
        nullNode.setPosition( cam.position() - hou.Vector2(0,1))
        
        cam.parm('dof_target').set(nullNode.path())
        
        expr = 'cam = hou.node(".")'
        expr +='\ncamPos = cam.worldTransform().extractTranslates()'
        expr +='\ndofNull = hou.node(cam.parm("dof_target").evalAsString())'
        expr +='\ndofNullPos = dofNull.worldTransform().extractTranslates()'        
        
        expr +='\n'
        expr +='\nreturn camPos.distanceTo(dofNullPos)'
        
        cam.parm('focus').setExpression(expr,language=hou.exprLanguage.Python)

        
    else:
        hou.ui.displayMessage("select a camera node")
else:
    hou.ui.displayMessage("select only one camera node")