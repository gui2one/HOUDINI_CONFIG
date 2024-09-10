import math
import hou



def writeBackgroundShader():
	string = '<!-- Background Shader -->\n'
	string += '<background>\n'
	string += '\t<background name="bg" strength="2.0" color="0.2, 0.2, 0.2" />\n'
	string += '\t<connect from="bg background" to="output surface" />\n'
	string += '</background>\n'
	return string

def writeDefaultShader():

	string = '<shader name="default_shader">\n'
	string += '\t<diffuse_bsdf name="diffuse" roughness="0.2" color="1.0, 0.0, 0.0"/>\n'
	string += '\t<connect from="diffuse bsdf" to="output surface" />\n'
	string += '</shader>\n'

	return string








def writeShader(obj,objName):

	color1 = obj.parmTuple('color1')
	bsdf1 = obj.parm('bsdf1').evalAsString()
	rough1 = obj.parm('roughness1').eval()

	color2 = obj.parmTuple('color2')
	bsdf2 = obj.parm('bsdf2').evalAsString()
	rough2 = obj.parm('roughness2').eval()

	string = '<shader name="%s" >\n' % (objName)
	string += '\t<%s_bsdf name="bsdf1" roughness="%s" color="%s, %s, %s" />\n' % (bsdf1, rough1, color1[0].eval(), color1[1].eval(), color1[2].eval())
	string += '\t<%s_bsdf name="bsdf2" roughness="%s" color="%s, %s, %s" />\n' % (bsdf2, rough2, color2[0].eval(), color2[1].eval(), color2[2].eval())
	string += '\t<add_closure name="mix" />\n'
	string += '\t<fresnel name="fresnel" />\n'	
	string += '\t<connect from="fresnel fac" to="bsdf2 color" />\n'	
	string += '\t<connect from="bsdf1 bsdf" to="mix closure1" />\n'
	string += '\t<connect from="bsdf2 bsdf" to="mix closure2" />\n'
	string += '\t<connect from="mix closure" to="output surface" />\n'
	string += '</shader>\n'
	return string




def writeLight(obj):

	mat = obj.worldTransform()
	#mat = mat.inverted()
	translates = mat.extractTranslates()
	translates[0] *= -1.0 # negate x coordinate   	
	
	string =  '<!-- Point Light -->\n'
	string += '<shader name="point_shader">\n'
	string += '\t<emission name="emission" color="1.0 1.0 1.0" strength="100" />\n'
	string += '\t<connect from="emission emission" to="output surface" />\n'
	string += '</shader>\n'

	string += '<transform translate="%s %s %s" >\n' % (translates[0], translates[1], translates[2])

	string += '\t<state shader="point_shader">\n'
	string += '\t\t<light type="0" size="1.0"  />\n'
	string += '\t</state>\n'
	string += '</transform>\n'
	# <!-- Point Light -->
	# <shader name="point_shader">
	# 	<emission name="emission" color="0.8 0.1 0.1" strength="100" />
	# 	<connect from="emission emission" to="output surface" />
	# </shader>

	# <state shader="point_shader">
	# 	<light type="0" P="-2.0 1 0.0" size="0.01" />
	# </state>

	return string





def writeObject(objName):
	objStr = '\t\t\t\t<state interpolation="smooth" shader="%s" >\n' % (objName)
	objStr += '\t\t\t\t\t<include src="./objects/%s.xml" />\n' % (objName)
	objStr += '\t\t\t\t</state>\n'
	return objStr

def writeCamera(obj):
	apx = obj.parm('aperture').eval()
	focal = obj.parm('focal').eval()
	resx = obj.parm('resx').eval()
	resy = obj.parm('resy').eval()
	asp = obj.parm('aspect').eval() # aspect ratio

	fovx = 2 * math.atan( (apx/2) / focal )
	apy = (resy*apx) / (resx*asp)
	fovy = 2*math.atan( (apy/2) / focal )

	camStr = '\t\t\t\t<camera type="perspective" ' 
	camStr += ('fov="%s" ') % (math.degrees(fovy))

	camStr += ' />\n'
	return (camStr)

def writeTransformsStart(obj):

	mat = obj.worldTransform()
	#mat = mat.inverted()
	translates = mat.extractTranslates()
	translates[0] *= -1.0 # negate x coordinate    
	rotates = mat.extractRotates()
	quat = hou.Quaternion(mat)
	angleAxis = quat.extractAngleAxis()


	translateString = '<transform translate="%s %s %s" >\n' % (translates[0], translates[1], translates[2])

	trzString = '\t<transform rotate="%s 0 0 1" >\n' % (rotates[2]*-1)
	if obj.type().name() == 'cam':
		tryString = '\t\t<transform rotate="%s 0 1 0" >\n' % ((rotates[1]-180)*-1)
	else:
		tryString = '\t\t<transform rotate="%s 0 1 0" >\n' % ((rotates[1])*-1)
	trxString = '\t\t\t<transform rotate="%s 1 0 0" >\n' % (rotates[0]*-1)

	transformsStringStart = translateString + trzString + tryString + trxString

	return transformsStringStart


def writeTransformsEnd():

	transformsStringEnd = "\t\t\t</transform>\n"
	transformsStringEnd += "\t\t</transform>\n"
	transformsStringEnd += "\t</transform>\n"	
	transformsStringEnd += "</transform>\n"	

	return transformsStringEnd


