import sys
import math
import os
import re

# print sys.argv[1]

if sys.argv[2]:
    sourceDirectory = sys.argv[2]
else:
    sourceDirectory = None
numStrips = int(sys.argv[1])
import OpenEXR
import Imath, array, numpy
from PIL import Image



def convert(_filePath):

    print _filePath

    outName = os.path.splitext(_filePath)[0]
    pt = Imath.PixelType(Imath.PixelType.FLOAT)
    # exrFile = OpenEXR.InputFile("D:/WORK/temp/strip_test_2.0062.exr")
    # print "numStrips ------->" ,numStrips
    exrFile = OpenEXR.InputFile(os.path.join(sourceDirectory, _filePath))
    
    dataWindow = exrFile.header()['dataWindow']
    displayWindow = exrFile.header()['displayWindow']

    chans = exrFile.header()['channels'].keys()

    exrSize = (displayWindow.max.x - displayWindow.min.x + 1,
                 displayWindow.max.y - displayWindow.min.y + 1)

    
    numPixels = exrSize[0] * exrSize[1]
    # for item in exrFile.header():
    #     print item, "----- ", exrFile.header()[item]

    # print "exrSize = = ", exrSize
    dataPixelStartIndex = (dataWindow.min.y * exrSize[0]) + dataWindow.min.x + 1
    dataPixelEndIndex = ((dataWindow.max.y) * exrSize[0]) + dataWindow.max.x + 1

    # print "dataPixelStartIndex : ", dataPixelStartIndex
    # print "dataPixelEndIndex : ", dataPixelEndIndex
    # print "displayWindow :", displayWindow
    # print "dataWindow : ", dataWindow
    

    
    # print zerosArray

    # print "------------------> ",dataPixelStartIndex
    # print "------------------> ", dataPixelEndIndex

    redstr = exrFile.channel('R', pt)
    red = numpy.fromstring(redstr, dtype=numpy.float32)

    greenstr = exrFile.channel('G', pt)
    green = numpy.fromstring(greenstr, dtype=numpy.float32)

    bluestr = exrFile.channel('B', pt)
    blue = numpy.fromstring(bluestr, dtype=numpy.float32)

    alphaStr = exrFile.channel('A', pt)
    alpha = numpy.fromstring(alphaStr, dtype=numpy.float32)
    if dataPixelStartIndex != 1:
        zerosArray = numpy.zeros( max(dataPixelStartIndex -1 , 1), dtype=numpy.float32)
        red = numpy.concatenate((zerosArray, red))
        green = numpy.concatenate((zerosArray, green))
        blue = numpy.concatenate((zerosArray, blue))
        alpha = numpy.concatenate((zerosArray, alpha))

        
        print "applying patch 1 ...."

    if dataPixelEndIndex != ((exrSize[0] * exrSize[1])):
        patch2 = numpy.zeros(max((exrSize[0] * exrSize[1]) - dataPixelEndIndex , 1), dtype=numpy.float32)
        red = numpy.concatenate((red, patch2))
        green = numpy.concatenate((green, patch2))
        blue = numpy.concatenate((blue, patch2))
        alpha = numpy.concatenate((alpha, patch2))
        

        # print "dataPixelEndIndex : ", dataPixelEndIndex
        print exrSize[0] * exrSize[1]
        print "applying patch 2 ...."

    # print "length RED :", len(red)
    
    red.shape = (exrSize[1], exrSize[0])  # Numpy arrays are (row, col)
    green.shape = (exrSize[1], exrSize[0])  # Numpy arrays are (row, col)
    blue.shape = (exrSize[1], exrSize[0])  # Numpy arrays are (row, col)
    alpha.shape = (exrSize[1], exrSize[0])  # Numpy arrays are (row, col)


    newImageRes = (exrSize[0] * numStrips, exrSize[1] / numStrips)
    outEXRPath = os.path.join(sourceDirectory, outName + " _converted.exr")
    outEXR = OpenEXR.OutputFile(outEXRPath, OpenEXR.Header(newImageRes[0], newImageRes[1]))

    
    out = Image.new("RGBA", newImageRes)
    outPixels = out.load()

    stripHeight = exrSize[1] / numStrips
    # print "stripHeight ---> ", stripHeight

    emptyArray = numpy.zeros( numPixels, dtype=numpy.float32)
    print len(red)
    print len(emptyArray)
    exrFinalRed = emptyArray
    exrFinalRed.shape = (newImageRes[0], newImageRes[1])

    exrFinalGreen = emptyArray
    exrFinalGreen.shape = (newImageRes[0], newImageRes[1])

    exrFinalBlue = emptyArray
    exrFinalBlue.shape = (newImageRes[0], newImageRes[1])

    exrFinalAlpha = emptyArray
    exrFinalAlpha.shape = (newImageRes[0], newImageRes[1])

    

    for x in xrange(exrSize[0]):

        for y in xrange(exrSize[1]):
            curTile = math.floor(y / (float(stripHeight)))
            newX = x + curTile * exrSize[0]
            newY = y % stripHeight
            if x == 0:                
                # print "current X -->", x, ", current Y -->",y
                # print "new X --> ", newX, "new Y -->" ,newY
                pass

            a = math.pow(alpha[y, x], 1/2.2)
            outPixels[newX, newY] = (int(math.pow(red[y, x], 1.0 / 2.2) * 255),
                                     int(math.pow(green[y, x] , 1.0 / 2.2) * 255),
                                     int(math.pow(blue[y, x], 1.0 / 2.2) * 255),
                                     int(math.pow(alpha[y, x], 2.2) * 255))

            # print "newX :", newY

            # exrFinalRed[int(newX)][int(newY)] = red[y,x]
            # exrFinalGreen[int(newX)][int(newY)] = green[y, x]
            # exrFinalBlue[int(newX)][int(newY)] = blue[y, x]
            # exrFinalAlpha[int(newX)][int(newY)] = alpha[y, x]


    # out.show()

    exrFinalRed = red
    exrFinalGreen = red
    exrFinalBlue = red
    exrFinalAlpha = red

    outEXR.writePixels({'R': exrFinalRed, 'G':exrFinalGreen, 'B':exrFinalBlue, 'A':exrFinalAlpha})
    outPath = os.path.join(sourceDirectory, outName + " _converted.png")
    out.save(outPath)
    print" ----------------- ////////////"


# print os.path.dirname(os.path.abspath(sys.argv[0]))
# print os.path.isdir(sourceDirectory)

ext = '.exr'
imgFiles = []
if os.path.isdir(sourceDirectory):
    allFiles = os.listdir(sourceDirectory)
    # print allFiles
    for f in allFiles:
        if not os.path.isdir(os.path.join(sourceDirectory,f)):
            # print os.path.splitext(f)[1]
            if os.path.splitext(f)[1] == ext:
                imgFiles.append(f)
                regex = re.compile('\d+', re.IGNORECASE)
                # print 'hello'
                startId = -1
                digits = ""
                for match in regex.finditer(f):
                    if match.start() > startId:
                        startId = match.start()
                        digits = match.group(0)
                    # print "%s: %s" % (match.start(), f)

                # # print "startId :",startId,"digits :", digits, "file :",f
                # # mo = re.findall('\d+', f)
                # strippedStr = f.replace(digits, "$F4")

                # if not strippedStr in listTitles:

                #     listTitles.append(strippedStr)

    # print imgFiles

for file in imgFiles:
    convert(file)

