import hou

if len(hou.selectedNodes()):
    
    sel = hou.selectedNodes()[0]

    
    root = sel
    attr_names = ("active", "animated", "deforming")
    attr_values = (0, 1, 0)
    attr_node = None
    new_nodes = []
    for i, attr_name in enumerate(attr_names):
        attr_node = sel.parent().createNode("attribcreate")
        new_nodes.append(attr_node)
        attr_node.setInput(0, root)

        # attr_node.moveToGoodPosition()
        attr_node.parm("name1").set(attr_name)
        attr_node.parm("type1").set(1)  # integer type
        attr_node.parm("value1v1").set(attr_values[i])

        attr_node.setPosition(root.position() + hou.Vector2(0, -1))
        # if i > 0:
        #     attr_node.setPosition(new_nodes[i-1].position() + hou.Vector2(0, -1))
        root = attr_node

    null_node = sel.parent().createNode('null')
    null_node.setName("STATIC_ANIMATED_ATTRS", unique_name = True)
    null_node.setInput(0, new_nodes[len(new_nodes)-1])
    null_node.setPosition(new_nodes[len(new_nodes)-1].position() + hou.Vector2(0, -1))


else:
        hou.ui.displayMessage("select a node to branch out of")
