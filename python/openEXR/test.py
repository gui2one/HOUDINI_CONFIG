import OpenEXR, Imath
import numpy as np
import os

import sys
if len(sys.argv) > 1:
    try:
        numStrips = int(sys.argv[1])
        print "arg is a number"
        print "numStrips -->", numStrips
    except ValueError:
        print "error : an integer is required for numStrips"
        sys.exit(0)

else:
    print "this program needs a numStrips argument"
    sys.exit(0)


filePath = "D:/WORK/temp/strip_test_2.0048.exr"
dirName = os.path.dirname(filePath)
imgName, ext = os.path.splitext(filePath)
# print dirName
# print imgName, "---", ext
f = OpenEXR.InputFile(filePath)
displayWindow = f.header()['displayWindow']
print f.header()

curImgSize = (displayWindow.max.x + 1, displayWindow.max.y + 1)
# print "curImgSize : ", curImgSize

numPixels = curImgSize[0] * curImgSize[1]
# print "numPixels : ", numPixels

pt = Imath.PixelType(Imath.PixelType.FLOAT)


redstr = f.channel('R', pt)
red = np.fromstring(redstr, dtype=np.float32)
red.shape = (curImgSize[1], curImgSize[0]) ## numpy arrays are row then col

greenstr = f.channel('G', pt)
green = np.fromstring(greenstr, dtype=np.float32)
green.shape = (curImgSize[1], curImgSize[0])  # numpy arrays are row then col

bluestr = f.channel('B', pt)
blue = np.fromstring(bluestr, dtype=np.float32)
blue.shape = (curImgSize[1], curImgSize[0])  # numpy arrays are row then col

alphastr = f.channel('A', pt)
alpha = np.fromstring(alphastr, dtype=np.float32)
alpha.shape = (curImgSize[1], curImgSize[0])  # numpy arrays are row then col

stripHeight = curImgSize[1] / numStrips
newImageSize = (curImgSize[0] * numStrips, stripHeight)

stripsRed = []
stripsGreen = []
stripsBlue = []
stripsAlpha = []
for i in range(numStrips):
    startY = i * stripHeight
    endY = startY + stripHeight - 1

    stripsRed.append(red[startY:endY, 0:curImgSize[0] ])
    stripsGreen.append(green[startY:endY, 0:curImgSize[0] ])
    stripsBlue.append(blue[startY:endY, 0:curImgSize[0] ])
    stripsAlpha.append(alpha[startY:endY, 0:curImgSize[0] ])


newRed = np.zeros(numPixels, dtype=np.float32)
newRed.shape = (newImageSize[1], newImageSize[0])

newGreen = np.zeros(numPixels, dtype=np.float32)
newGreen.shape = (newImageSize[1], newImageSize[0])

newBlue = np.zeros(numPixels, dtype=np.float32 )
newBlue.shape = (newImageSize[1], newImageSize[0])

newAlpha = np.zeros(numPixels, dtype=np.float32 )
newAlpha.shape = (newImageSize[1], newImageSize[0])


for i in range(numStrips):
    print "iiiiiiiiiiiiiiii ---> ", i
    startY = 0
    endY = stripHeight -1
    print "startY 2 : ", startY
    print "endY 2 : ", endY
    startX = curImgSize[0] * i
    endX = (startX) + curImgSize[0]
    # print "startX 2 : ", startX
    # print "endX 2 : ", endX
    newRed[startY: endY, startX: endX] = stripsRed[i]
    newGreen[startY: endY, startX: endX] = stripsGreen[i]
    newBlue[startY: endY, startX: endX] = stripsBlue[i]
    newAlpha[startY: endY, startX: endX] = stripsAlpha[i]
    print "newRed = was asigned !!!!!"
    print "-------------"



outFilePath = imgName + '_converted.exr'

newHeader = OpenEXR.Header(newImageSize[0], newImageSize[1])
half_chan = Imath.Channel(Imath.PixelType(Imath.PixelType.FLOAT))
newHeader['channels'] = dict([(c, half_chan) for c in "RGBA"])

outFile = OpenEXR.OutputFile(outFilePath, newHeader)


outFile.writePixels({'R': newRed, 'G': newGreen,
                     'B': newBlue, 'A': newAlpha})



