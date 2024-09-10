import hou


def findNodeByType(parent, type):
    for child in parent.children():
        if child.type().name() == type:
            return child
    
    return None

def updateSessionVariable(var_name, node_path):

    
    curSource = hou.sessionModuleSource()
    lines = curSource.split("\n")

    for i, line in enumerate(lines):
        if line.split('=')[0].strip(' ') == var_name:
            line = "%s = '%s'" % (var_name, node_path)
            lines[i] = line
    data = '\n'.join(lines)
    # print data

    hou.setSessionModuleSource(data)


def deleteSessionVariable(var_name):
    # print 'utils function : delete variable'
    curSource = hou.sessionModuleSource()
    lines = curSource.split("\n")

    for i, line in enumerate(lines):
        if line.split('=')[0].strip(' ') == var_name:
            del lines[i]
            break
    data = '\n'.join(lines)
    # print data

    hou.setSessionModuleSource(data)

    # then the value stays in memory, so explicitly delete it
    cmdString = 'del hou.session.%s' %(var_name)
    try:
        exec(cmdString)
    except:
        print 'unable to delete variable "%s"from memory' % (var_name)

