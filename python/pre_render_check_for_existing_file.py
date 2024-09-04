import os
import sys
root = hou.node(".")

start_frame = int(root.parm("f1").eval())
end_frame = int(root.parm("f2").eval())
increment_frame = int(root.parm("f3").eval())

for i in range(start_frame, end_frame+1):
    saveName = root.parm("vm_picture").evalAsStringAtFrame(i)
    # hou.ui.displayMessage(saveName)
    # print dir(os.path)
    exists = os.path.isfile(saveName)
    if exists:
        res = hou.ui.displayMessage(
            "File already exists. Overwrite ?", buttons=('yes', 'no'))
        # hou.ui.displayMessage(str(res))
    
        if res == 0:
            pass
        elif res == 1:
            raise ValueError('file exists')