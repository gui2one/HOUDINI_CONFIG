node = hou.pwd()
geo = node.geometry()

# Add code to modify contents of geo.
# Use drop down menu to select examples.

import string
from array import *
from lxml import etree
print "OSM Data Converter"

f = open(hou.expandString("$HIP")+"/osm_data/vern.osm",'r')

content = f.read()
root = etree.XML(content)

#print f


f.close()


tree = etree.ElementTree(root)

print(tree.docinfo.xml_version)
print("root tag -->" + root.tag)

inc = 0
idArray = array('I')
latArray = array("f")
lonArray = array("f")
for element in root.iter("node"):

    idArray.append(int(element.attrib["id"]))
    latArray.append(float(element.attrib["lat"]))
    lonArray.append(float(element.attrib["lon"]))
    inc+=1    
    
    

#print(str(inc) + " node(s)found")

d = dict(root.attrib)
#print(sorted(d.items()))
#print(d.items())


geo.addAttrib(hou.attribType.Global,"myAttrib",0);
geo.setGlobalAttribValue("myAttrib",20)
#geo.setGlobalAttribValue("myAttrib",idArray)
size = geo.globalAttribs()[1].size()
#print size
nodeId = geo.globalAttribs()[1].dataType()
#print latArray[0]

inc = 0
for element in idArray:
    point = geo.createPoint()
    
    point.setPosition((lonArray[inc],0.0,-latArray[inc]*1.45))
    inc+=1
    