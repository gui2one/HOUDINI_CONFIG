import sys

desk = hou.ui.curDesktop() 
viewer = desk.paneTabOfType(hou.paneTabType.SceneViewer)
currentView = viewer.curViewport()

cam = None

if(currentView.camera() == None):
    print 'no camera in current view'
    for v in viewer.viewports():
        if v.camera() != None:
            
            print ' camera is finally :', v.camera()    
            cam = v.camera()
            cam.setSelected(True, True)
else:
    print ' camera is :', currentView.camera()
    cam = currentView.camera()
    cam.setSelected(True, True)
        
