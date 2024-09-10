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
container = soptoolutils.createSopNodeContainer(scene_viewer, "dust_source")
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
debrissource_sop.parm('source_type').set(1) ### type dust



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

## add dust limits asset
dust_limits = container.parent().createNode('dust_limits')


dopnet = container.parent().createNode('dopnet', 'dust_sim')
dopnet.moveToGoodPosition()
gasresizefluiddynamic = dopnet.createNode('gasresizefluiddynamic')
gasresizefluiddynamic.parm('delay_frames').set(10)

gasdissipate = dopnet.createNode('gasdissipate')
gasdissipate.parm('diffusion').set(0.2)
gasdissipate.parm('evaporation').set(0.2)
gasdissipate.parm('subtractovertime').set(1)
gasdissipate.parm('subtractrate').set(0.05)

gasturbulence = dopnet.createNode('gasturbulence')
mergeVelUpdate = dopnet.createNode('merge')
mergeVelUpdate.setNextInput(gasdissipate)
mergeVelUpdate.setNextInput(gasturbulence)

smokeobject = dopnet.createNode('smokeobject')
smokeobject.setName('dust', unique_name=True)
## set expressions
smokeobject.parm('sizex').setExpression('ch("../../%s/sizex")' % (dust_limits.name()))
smokeobject.parm('sizey').setExpression('ch("../../%s/sizey")'% (dust_limits.name()))
smokeobject.parm('sizez').setExpression('ch("../../%s/sizez")'% (dust_limits.name()))

smokeobject.parm('tx').setExpression('ch("../../%s/t2x")'% (dust_limits.name()))
smokeobject.parm('ty').setExpression('ch("../../%s/t2y")'% (dust_limits.name()))
smokeobject.parm('tz').setExpression('ch("../../%s/t2z")'% (dust_limits.name()))

sourcevolume = dopnet.createNode('sourcevolume')
sourcevolume.parm('source_path').set(null_sop.path())
sourcevolume.parm('velocity_merge').set(1) ## add
sourcevolume.parm('normalizevel').set(0) ## uncheck normalize vel
sourcevolume.parm('scale_source').set(0.2)
sourcevolume.parm('scale_temperature').set(0.1)
sourcevolume.parm('scale_velocity').set(0.1)

smokesolver = dopnet.createNode('smokesolver')
smokesolver.setFirstInput(smokeobject)
smokesolver.setInput(1, gasresizefluiddynamic)
smokesolver.setInput(2, mergeVelUpdate)
smokesolver.setInput(4, sourcevolume)




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
mergeSolvers.setNextInput(smokesolver)
staticSolver.setInput(0, mergeStatics)
mergeStatics.setNextInput(ground)
mergeStatics.setNextInput(staticobject)

output = gui2one_utils.findNodeByType(dopnet, 'output')



if output != None:
    output.setInput(0, mergeSolvers)
else:
    output = dopnet.createNode('output')
    output.setInput(0, mergeSolvers)

output.setDisplayFlag(1)

dopnet.layoutChildren()
dopnet.setDisplayFlag(False)

#
# Create Simulation
#





dust_obj = container.parent().createNode('geo', 'dust', False)
dust_obj.moveToGoodPosition()

billowysmoke_mat = hou.galleries.galleryEntries('billowysmoke')[0].createChildNode(hou.node("/mat"))
dust_obj.parm("shop_materialpath").set(billowysmoke_mat.path())
dopimport = dust_obj.createNode('dopimportfield')
dopimport.parm('doppath').set(dopnet.path())
dopimport.parm('dopnode').set(dopnet.path()+"/dust")
dopimport.parm('fields').set(3)

dopimport.parm('fieldname1').set('density')
dopimport.parm('fieldname2').set('vel')
dopimport.parm('visible2').set(3) ## invisible
dopimport.parm('fieldname3').set('temperature')
dopimport.parm('visible3').set(3) ## invisible
# dopimport.parm("presets").set(0)
dopimport.moveToGoodPosition()

# Change our viewer to the dop network



scene_viewer.enterCurrentNodeState()
