node = hou.pwd()
geo = node.geometry()

#########
#### it needs a "osm_file" ui 'file' parameter
###############
filePath = hou.parm('osm_file').eval()

import string
from array import *
from lxml import etree
print "OSM Data Converter"

#f = open(hou.expandString("$HIP")+"/osm_data/quartier_fonderie.osm",'r')
f = open(hou.expandString(filePath),"r")

content = f.read()
root = etree.XML(content)


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
    
    

print(str(inc) + " node(s)found")

inc = 0
for element in root.iter("relation"):
    for item in element.iter("member"):
        print item.attrib["ref"]
    inc+=1    
    
    

print(str(inc) + " relation(s)found")

idAttr = geo.addAttrib(hou.attribType.Point,"myAttrib","");
#geo.setAttribValue("myAttrib",20)
#geo.setGlobalAttribValue("myAttrib",idArray)
#size = geo.globalAttribs()[1].size()
#print size
#nodeId = geo.globalAttribs()[1].dataType()
#print latArray[0]

inc = 0
for element in idArray:
    point = geo.createPoint()
    
    point.setPosition((lonArray[inc],0.0,-latArray[inc]*1.45))
    point.setAttribValue(idAttr,str(idArray[inc]))
    inc+=1
    