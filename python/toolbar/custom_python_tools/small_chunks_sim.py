import toolutils
import soptoolutils

import sys
import os

TOOLS_PATH = hou.getenv('CUSTOM_PYTHON_TOOLS')
sys.path.append(TOOLS_PATH)
from gui2one_utils import gui2one_utils
reload(gui2one_utils)

#print kwargs

activepane = toolutils.activePane(kwargs)
if activepane.type() != hou.paneTabType.SceneViewer:
    raise hou.Error("This tool cannot run in the current pane")

scene_viewer = toolutils.sceneViewer()
nodetypename = "delete"

# Obtain a geometry selection
geo_types = (hou.geometryType.Primitives, )
selection = scene_viewer.selectGeometry(
    "Select the primitives from which to create debris and press Enter to complete",
    geometry_types=geo_types,
    allow_obj_sel=True)
# The following will raise an exception if nothing was selected.
if len(selection.nodes()) == 0:
    raise hou.Error("Nothing was selected.")

#
# Create Source
#
# Create a new SOP container with the merged geometry
container = soptoolutils.createSopNodeContainer(scene_viewer, "small_chunks_source")
merge_sop = selection.mergedNode(container, nodetypename, True, True)
# Turn back on the display flag for merged nodes
for sop in selection.nodes():
    sop.parent().setDisplayFlag(True)

merge_sop.moveToGoodPosition()

unpack_sop = container.createNode('unpack')
unpack_sop.parm('limit_iterations').set(False)
unpack_sop.parm('transfer_attributes').set('name')
unpack_sop.setFirstInput(merge_sop)
unpack_sop.moveToGoodPosition()

sort = container.createNode('sort')
sort.parm('primsort').set(5)  # random primtive sort
sort.setFirstInput(unpack_sop)
sort.setColor(hou.Color(0.9, 0.9, 0.0))

attribute_sop = container.createNode('attribute', 'remove_attributes')
attribute_sop.parm('ptdel').set('* ^name')
attribute_sop.parm('vtxdel').set('*')
attribute_sop.parm('primdel').set('*')
attribute_sop.parm('dtldel').set('*')
attribute_sop.setFirstInput(sort)
attribute_sop.moveToGoodPosition()


debrissource_sop = container.createNode('gui2one_debris_source')
debrissource_sop.setFirstInput(attribute_sop)
debrissource_sop.parm('source_type').set(0)  # type points
debrissource_sop.parm('lifespan').set(0)

small_chunks_sop = container.createNode('gui2one_generate_small_chunks')
small_chunks_sop.setFirstInput(debrissource_sop)

null_sop = container.createNode('null', 'OUT')
null_sop.setFirstInput(small_chunks_sop)
null_sop.moveToGoodPosition()
null_sop.setDisplayFlag(True)
null_sop.setRenderFlag(True)

container.setDisplayFlag(False)
container.layoutChildren()

#
# Create Simulation
#





dopnet = container.parent().createNode('dopnet', 'small_chunks_sim')
dopnet.moveToGoodPosition()

rbdpackedobject = dopnet.createNode('rbdpackedobject')
rbdpackedobject.setName("chunks", unique_name=True)
rbdpackedobject.parm('usesimframe').set(1)
rbdpackedobject.parm('soppath').set(debrissource_sop.parent().path() + '/OUT')
rbdpackedobject.parm('createframe').setExpression('$SF')
rbdpackedobject.parm('object_name').set('$OS`_`$SF')
rbdpackedobject.parm('inheritvelocity').set(1)


rigidbodysolver = dopnet.createNode('rigidbodysolver')
rigidbodysolver.parm('use_parallel_constraint_solver').set(1)
rigidbodysolver.setFirstInput(rbdpackedobject)



## create ground plane and static solver
ground = dopnet.createNode('groundplane')
staticobject = dopnet.createNode('staticobject')
staticobject.setName('fracture_sim_geo', unique_name=True)
staticobject.parm('soppath').set(hou.session.mergeSimGeo + "/OUT")
staticobject.parm('animategeo').set(1)
staticobject.parm('usetransform').set(1)
staticobject.parm('bullet_groupconnected').set(1)
# staticobject.parm('showguide2').set(1)
staticobject.parm('bullet_collision_margin').set(0.0)
staticobject.parm('collisiondetection').set(2)

staticSolver = dopnet.createNode('staticsolver')
mergeStatics = dopnet.createNode('merge')


mergeSolvers = dopnet.createNode('merge')

mergeSolvers.setNextInput(staticSolver)
mergeSolvers.setNextInput(rigidbodysolver)
staticSolver.setInput(0, mergeStatics)
mergeStatics.setNextInput(ground)
mergeStatics.setNextInput(staticobject)

gravity = dopnet.createNode('gravity')
gravity.setFirstInput(mergeSolvers)
output = gui2one_utils.findNodeByType(dopnet, 'output')


if output != None:
    output.setInput(0, gravity)
else:
    output = dopnet.createNode('output')
    output.setInput(0, gravity)

output.setDisplayFlag(1)

dopnet.layoutChildren()
dopnet.setDisplayFlag(False)

#
# Create Simulation
#


small_chunks_obj = container.parent().createNode('geo', 'small_chunks', False)
small_chunks_obj.moveToGoodPosition()

dopimport = small_chunks_obj.createNode('dopimport')
dopimport.parm('doppath').set(dopnet.path())
dopimport.parm('objpattern').set('chunks_*')
dopimport.parm('importstyle').set(3)

dopimport.moveToGoodPosition()

# Change our viewer to the dop network


scene_viewer.enterCurrentNodeState()
