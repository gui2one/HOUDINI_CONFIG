import os

sel = hou.selectedNodes()
if sel:
    for node in sel:
        defi = node.type().definition()
        keys = defi.sections().keys()

        choices = hou.ui.selectFromList(keys)
        print choices
        if len(choices):
            folder = hou.ui.selectFile(title="Choose a folder to extract files into",
                                       start_directory=hou.expandString('$HIP'), file_type=hou.fileType.Directory)
            print folder

            if len(folder) > 0:

                for i, choice in enumerate(choices):
                    section_name = keys[choice]
                    content = defi.sections()[section_name].contents()
                    file_path = os.path.join(folder, section_name)

                    f = open(file_path, "wb")
                    f.write(content)
                    f.close()
                    print file_path
            else:
                print "select a folder"
        else:
            print "no choice"

    pass
else:
    print "select a hda"
