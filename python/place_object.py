sel = hou.selectedNodes()[0]

for pane in hou.ui.curDesktop().panes():
    for tab in pane.tabs():
        if tab.type() == hou.paneTabType.SceneViewer :

            sceneViewer = tab
            break
    
newPos = sceneViewer.selectPositions()[0]

sel.parm("tx").set(newPos.x())
sel.parm("ty").set(newPos.y())
sel.parm("tz").set(newPos.z())