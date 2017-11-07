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
container = soptoolutils.createSopNodeContainer(scene_viewer, "debris_source")
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
sort.parm('primsort').set(5) ## random primtive sort
sort.setFirstInput(unpack_sop)
sort.setColor(hou.Color(0.9,0.9,0.0))

attribute_sop = container.createNode('attribute', 'remove_attributes')
attribute_sop.parm('ptdel').set('* ^name')
attribute_sop.parm('vtxdel').set('*')
attribute_sop.parm('primdel').set('*')
attribute_sop.parm('dtldel').set('*')
attribute_sop.setFirstInput(sort)
attribute_sop.moveToGoodPosition()

attribpromote_sop = container.createNode('attribpromote')
attribpromote_sop.parm('inname').set('name')



trail_sop = container.createNode('trail', 'compute_velocity')
trail_sop.parm('result').set('velocity')
trail_sop.setFirstInput(attribute_sop)
trail_sop.moveToGoodPosition()

debrissource_sop = container.createNode('debrissource')
debrissource_sop.setFirstInput(trail_sop)
debrissource_sop.parm('edges').set(1000)
debrissource_sop.parm('lifespan').set(0.2)
debrissource_sop.moveToGoodPosition()

null_sop = container.createNode('null', 'OUT')
null_sop.setFirstInput(debrissource_sop)
null_sop.moveToGoodPosition()
null_sop.setDisplayFlag(True)
null_sop.setRenderFlag(True)

container.setDisplayFlag(False)
container.layoutChildren()

#
# Create Simulation
#
dopnet = container.parent().createNode('dopnet', 'debris_sim')
dopnet.moveToGoodPosition()

popobject = dopnet.createNode('popobject')
popobject.parm('friction').set(0.8)
popobject.parm('dynamicfriction').set(0.25)
popobject.moveToGoodPosition()

popsource = dopnet.createNode('popsource')
popsource.parm('emittype').set('point')
popsource.parm('soppath').set(null_sop.path())
popsource.parm('inheritattrib').set('* ^Cd')
popsource.parm('inheritvel').set(0.56)
popsource.moveToGoodPosition()

popstream = dopnet.createNode('popstream')
popstream.setFirstInput(popsource)
popstream.moveToGoodPosition()

popreplicate = dopnet.createNode('popreplicate')
popreplicate.parm('constantrate').set(100)
popreplicate.parm('killorig').set(True)
popreplicate.parm('shape').set('point')
popreplicate.parm('donoise').set(True)
popreplicate.parm('initvel').set('add')
popreplicate.parm('varx').set(0.7)
popreplicate.parm('vary').set(0.7)
popreplicate.parm('varz').set(0.7)
popreplicate.setFirstInput(popstream)
popreplicate.moveToGoodPosition()
popreplicate.bypass(1)

popinteract = dopnet.createNode('popinteract')
popinteract.parm('positionforce').set(0.005)
popinteract.parm('falloffradius').set(0.44)
popinteract.setFirstInput(popreplicate)
popinteract.moveToGoodPosition()

popdrag = dopnet.createNode('popdrag')
popdrag.parm('airresist').set(0.01)
popdrag.setFirstInput(popinteract)
popdrag.moveToGoodPosition()

popforce = dopnet.createNode('popforce')
popforce.parm('forcey').set(-9.80665)
popforce.setFirstInput(popdrag)
popforce.moveToGoodPosition()

popsolver = dopnet.createNode('popsolver')
popsolver.setFirstInput(popobject)
popsolver.setNextInput(popforce)
popsolver.setNextInput(popsource)
popsolver.moveToGoodPosition()

popsolver.setDisplayFlag(True)
dopnet.setDisplayFlag(False)

## create ground plane and static solver
ground = dopnet.createNode('groundplane')
staticobject = dopnet.createNode('staticobject')
staticobject.setName('fracture_sim_geo', unique_name=True)
staticobject.parm('soppath').set( hou.session.mergeSimGeo + "/OUT")
staticobject.parm('animategeo').set(1)
staticobject.parm('usetransform').set(1)
staticobject.parm('bullet_groupconnected').set(1)
# staticobject.parm('showguide2').set(1)
staticobject.parm('bullet_collision_margin').set(0.0)
staticobject.parm('collisiondetection').set(2)

staticSolver = dopnet.createNode('staticsolver')
mergeStatics = dopnet.createNode('merge')



mergeSolvers = dopnet.createNode('merge')

mergeSolvers.setNextInput( staticSolver)
mergeSolvers.setNextInput(popsolver)
staticSolver.setInput(0, mergeStatics)
mergeStatics.setNextInput(ground)
mergeStatics.setNextInput(staticobject)

output = gui2one_utils.findNodeByType(dopnet,'output')

if output != None:
    output.setInput(0,mergeSolvers)
else:
    output = dopnet.createNode('output')
    output.setInput(0, mergeSolvers)

output.setDisplayFlag(1)

dopnet.layoutChildren()





#
# Create Simulation
#
debris = container.parent().createNode('geo', 'debris', False)
debris.moveToGoodPosition()

dopimport = debris.createNode('dopimport')
dopimport.parm('doppath').set(dopnet.path())
dopimport.parm('objpattern').set('popobject*')
dopimport.parm('importstyle').set('fetch')
dopimport.moveToGoodPosition()


attribrandomize = debris.createNode('attribrandomize')
attribrandomize.setName('randomize_pscale',unique_name=True)
attribrandomize.parm('name').set('pscale')
attribrandomize.parm('minx').set(0.5)
attribrandomize.parm('scale').set(0.035)

attribrandomize.setInput(0,dopimport)
attribrandomize.setDisplayFlag(1)
attribrandomize.setRenderFlag(1)


# Change our viewer to the dop network
scene_viewer.setPwd(popsolver)
popsolver.setCurrent(True, True)
toolutils.homeToSelectionNetworkEditorsFor(popsolver)
scene_viewer.enterCurrentNodeState()
