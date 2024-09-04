import os 
import sys
import re
from glob import glob


path = str(sys.argv[1])
print(path)
# all_files = os.listdir(path)

glob_file = glob(path)

base_dir = os.path.dirname(path)
base_name = os.path.basename(path)
list_path = os.path.join(base_dir,base_name.replace("*","")+".ifl")
with open(list_path,'w') as f:
    for item in glob_file:
        f.write(item + '\n')

# list_titles = []
# img_files = []
# for f in all_files :
#     if not os.path.isdir(os.path.join(path,f)) == 1:
#         print( f, "is a file ")
#     else : 
#         print (f, "is a dir")


# for f in all_files:
#     if not os.path.isdir(os.path.join(path, f)):

#         img_files.append(f)
#         regex = re.compile('\d+', re.IGNORECASE)

#         startId = -1
#         digits = ""
#         for match in regex.finditer(f):
#             if match.start() > startId:
#                 startId = match.start()
#                 digits = match.group(0)
#                 # print ("%s:%s -- %s" % (match.start(),digits, f))

#         # print "startId :",startId,"digits :", digits, "file :",f
#         # mo = re.findall('\d+', f)
#         strippedStr = f.replace(digits, "!!!")

#         if not strippedStr in list_titles:

#             list_titles.append(strippedStr)

# print (list_titles)
