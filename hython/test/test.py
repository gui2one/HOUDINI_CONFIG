import subprocess
import time
import sys
# sys.path.append('C:/Python27/Lib/site-packages')

hou.hipFile.load('D:/WORK/SPRAYFILM/Phaze_Graphik/3D/HOUDINI/render_test.hiplc')

# hou.setFrame(101)
hou.cd('/out')
rop = hou.node("/out").children()[0]

print rop
rop.parm("execute").pressButton()

print "-------------------------------"
print hou

while True:
    cmd = 'WMIC PROCESS get Caption'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    for line in proc.stdout:
        if 'mantra' in line:
            print line

    print 'sleeping a second ....'
    time.sleep(1)