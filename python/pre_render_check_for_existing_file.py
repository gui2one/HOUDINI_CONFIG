import os
import sys
root = hou.node(".")
saveName = root.parm("vm_picture").eval()
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
