import toolutils
import soptoolutils
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
unpack_sop.setFirstInput(merge_sop)
unpack_sop.moveToGoodPosition()

attribute_sop = container.createNode('attribute', 'remove_attributes')
attribute_sop.parm('ptdel').set('*')
attribute_sop.parm('vtxdel').set('*')
attribute_sop.parm('primdel').set('* ^name')
attribute_sop.parm('dtldel').set('*')
attribute_sop.setFirstInput(unpack_sop)
attribute_sop.moveToGoodPosition()

trail_sop = container.createNode('trail', 'compute_velocity')
trail_sop.parm('result').set('velocity')
trail_sop.setFirstInput(attribute_sop)
trail_sop.moveToGoodPosition()

debrissource_sop = container.createNode('debrissource')
debrissource_sop.setFirstInput(trail_sop)
debrissource_sop.moveToGoodPosition()

null_sop = container.createNode('null', 'OUT')
null_sop.setFirstInput(debrissource_sop)
null_sop.moveToGoodPosition()
null_sop.setDisplayFlag(True)
null_sop.setRenderFlag(True)

container.setDisplayFlag(False)

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

popinteract = dopnet.createNode('popinteract')
popinteract.parm('positionforce').set(-0.2)
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

#
# Create Simulation
#
debris = container.parent().createNode('geo', 'debris', False)
debris.moveToGoodPosition()

dopimport = debris.createNode('dopimport')
dopimport.parm('doppath').set(dopnet.path())
dopimport.parm('importstyle').set('fetch')
dopimport.moveToGoodPosition()

# Change our viewer to the dop network
scene_viewer.setPwd(popsolver)
popsolver.setCurrent(True, True)
toolutils.homeToSelectionNetworkEditorsFor(popsolver)
scene_viewer.enterCurrentNodeState()
