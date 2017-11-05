import sys
import os

TOOLS_PATH = hou.getenv('CUSTOM_PYTHON_TOOLS')
sys.path.append(TOOLS_PATH)

from gui2one_utils import gui2one_utils

reload(gui2one_utils)
### begin functions
def findNodeByType(parent, type):
    for child in parent.children():
        if child.type().name() == type:
            return child


def initFractureSim():

    global mergeConstraintsPath
    print "init fracture simulation ..."
    root = hou.node('/obj')
    
    dopnetNode = root.createNode('dopnet')
    dopnetNode.setName('fracture_sim', unique_name=True)
    dopnetNode.moveToGoodPosition()
    hou.appendSessionModuleSource("fractureSim = '%s'" % (dopnetNode.path()))
    
    rigidBodySolver = dopnetNode.createNode('rigidbodysolver')
    mergeObjectsNode = dopnetNode.createNode('merge')
    
    outputNode = hou.node(dopnetNode.path() + "/output")
    
    
    ## create ground plane and static solver
    ground = dopnetNode.createNode('groundplane')
    staticSolver = dopnetNode.createNode('staticsolver') 
    mergeStatics = dopnetNode.createNode('merge')
    
    mergeSolvers = dopnetNode.createNode('merge')
    
    ## forces
    gravity = dopnetNode.createNode('gravity')
    

    ### build constraints
    dopConstraints = dopnetNode.createNode('dop_build_glue_constraints')
    dopConstraints.parm('soppath').set(mergeConstraintsPath)
    


    ### wire all the nodes
    outputNode.setInput(0, dopConstraints)
    dopConstraints.setInput(0, gravity)
    gravity.setInput(0,mergeSolvers)
    mergeSolvers.setInput(0,staticSolver)
    mergeSolvers.setInput(1,rigidBodySolver)
    rigidBodySolver.setInput(0,mergeObjectsNode)
    
    
    staticSolver.setInput(0,mergeStatics)
    mergeStatics.setInput(0,ground)    
    
    
    dopnetNode.layoutChildren()
    ### add event callbacks
    
    dopnetNode.addEventCallback((hou.nodeEventType.NameChanged,), dopRename)
    dopnetNode.addEventCallback((hou.nodeEventType.BeingDeleted,), onDeleteFractureSim)  

def initConstraintsSop():
    print 'init merge constraints sop'
    global curConstraintsPath
    global selection
    global mergeConstraintsPath
    print 'curConstraintsPath -->', curConstraintsPath
    root = hou.node('/obj')
    
    sop = root.createNode('geo')
    sop.children()[0].destroy() # delete default file sop
    sop.setName('merge_glue_constraints', unique_name=True)
    sop.moveToGoodPosition()
    hou.appendSessionModuleSource("mergeConstraintsSop = '%s'" % (sop.path()))
    sop.addEventCallback((hou.nodeEventType.NameChanged,), constraintsSopRenamed)
    sop.addEventCallback((hou.nodeEventType.BeingDeleted,), onDeleteMergeConstraintsSop)  


    # adding node to merge constraints
    OUT = sop.createNode('null')
    OUT.setName('OUT', unique_name=True)

    merge = sop.createNode('merge')
    # objectMerge = sop.createNode('object_merge')
    # objectMerge.setName( selection.name() + '_constraints', unique_name = True)
    # objectMerge.parm('objpath1').set(curConstraintsPath)

    ### link nodes
    OUT.setInput(0,merge)
    # merge.setInput(0, objectMerge)

    sop.layoutChildren()

    OUT.setDisplayFlag(1)
    OUT.setRenderFlag(1)
    OUT.setTemplateFlag(1)

    mergeConstraintsPath = OUT.path()
    

def constraintsSopRenamed(**kwargs) :
    # print "renamed constraints sop"
    
    gui2one_utils.updateSessionVariable('mergeConstraintsSop', kwargs['node'].path()) 
    pass
    
def fractureGeometry(selection):
    global curConstraintsPath
    displayNode = selection.displayNode()
    shatter = selection.createNode('gui2one_shatter')
    shatter.setInput(0,displayNode)
    shatter.moveToGoodPosition()
    
    constraints = selection.createNode('build_glue_constraints')
    constraints.parm('dop_object_name').set(selection.name())
    constraints.setInput(0,shatter)
    constraints.moveToGoodPosition()

    curConstraintsPath = constraints.path()

    null = selection.createNode('null')    
    null.setName('OUT', unique_name=True)
    null.setInput(0, shatter)
    null.moveToGoodPosition()

    dopImport = selection.createNode('dopimport')
    dopImport.parm('doppath').set(hou.session.fractureSim)
    dopImport.parm('objpattern').set(selection.name())
    dopImport.parm('importstyle').set(2) ### fetch packed geometry from dopnet
    
    dopImport.setDisplayFlag(1)
    dopImport.setRenderFlag(1)
    dopImport.setTemplateFlag(1)

    dopImport.setInput(0,null)
    dopImport.moveToGoodPosition()
    
    
def dopRename(**kwargs):
    nodePath =  kwargs['node'].path()
    # print ';;;;;;;;;;;;;;;;;;',nodePath
    gui2one_utils.updateSessionVariable('fractureSim', nodePath)   

def onDeleteFractureSim(**kwargs):
    gui2one_utils.deleteSessionVariable('fractureSim')
        
def onDeleteMergeConstraintsSop(**kwargs):
    gui2one_utils.deleteSessionVariable('mergeConstraintsSop')

def addSelectionConstraints():
    global selection
    global curConstraintsPath
    cNode = hou.node(hou.session.mergeConstraintsSop)
    objMerge = cNode.createNode("object_merge")
    objMerge.setName(selection.name(), unique_name = True)
    objMerge.parm("objpath1").set(curConstraintsPath)
    objMerge.parm('xformpath').set('.')
    ###find OUT null sop
    merge = hou.node(cNode.path()+'/merge1')
    merge.setInput( len(merge.inputs() ), objMerge)

    cNode.layoutChildren()
    
def addSelectionRBDs():
    
    global selection
    fractureSim = hou.node(hou.session.fractureSim)

    rbdpackedNode = fractureSim.createNode('rbdpackedobject')
    rbdpackedNode.setName(selection.name(), unique_name=True)
    rbdpackedNode.parm('soppath').set(selection.path() + '/OUT')
    rbdpackedNode.parm('usetransform').set(1)
    rbdpackedNode.moveToGoodPosition()

    rbdSolver = findNodeByType(fractureSim, 'rigidbodysolver')
    mergeRBDs = rbdSolver.inputs()[0]
    
    mergeRBDs.setInput( len(mergeRBDs.inputs()), rbdpackedNode)
    rbdpackedNode.moveToGoodPosition()



###
### end functions         
  


### begin script     

curConstraintsPath = ''
mergeConstraintsPath = ''

if len(hou.selectedNodes()) > 0:
    selection =  hou.selectedNodes()[0] 
else:
    selection = None


if selection :    
    try :
        print hou.session.mergeConstraintsSop
        if hou.session.mergeConstraintsSop == None:
            raise(AttributeError)
    except AttributeError:
        print 'no variable with this name in hou.session'
        initConstraintsSop()            

    try :
        print hou.session.fractureSim
        if hou.session.fractureSim == None:
            raise(AttributeError)
    except AttributeError:
        print 'no variable with this name in hou.session'        
        initFractureSim()

    fractureGeometry(selection)
    addSelectionConstraints()
    addSelectionRBDs()
        
      


    
    
