'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
from string import Template

###
# goloble commands
#
# plugin commands
CMD_NEW_FRAME = 1002
CMD_SERVER_CLOSING = 5555
# mocap commnds
MOCAP_CLASSIFY_DATA = 2222
MOCAP_RAW_DATA = 3333
MOCAP_ROGE_DATA = 9999
# server commands
SERVER_RECORD_DATA = 4444

#DATA
MAX_NUM_POINTS = 25
POINT_DATA_SIZE = 6

class AsciiFile( object ):
    
    def __init__(self,rawFile):
        maxPoints = MAX_NUM_POINTS
        pointDataSize = POINT_DATA_SIZE
        
        locNameDict = {}
        
        numOfPointsX = 0
        numOfPointsY= 0
        
        numOfKeysX= 0
        numOfKeysY= 0
        
        frameNumberAndPosX = ''
        frameNumberAndPosY = ''
        
        frame = 0
        #for line in rawFile.readlines():
        while not rawFile.atEnd():
            line = str(rawFile.readLine())
            #print line
            line = line.replace("[",'')
            line = line.replace("]",'')
            unpacked_data = line.split(', ')
            
            for index in xrange(0,maxPoints):
                
                dataIndexOffset = 0
                if index != 0:
                    dataIndexOffset = index * pointDataSize

                tag = int(unpacked_data[dataIndexOffset])
                
                y = unpacked_data[dataIndexOffset+2]
                x = unpacked_data[dataIndexOffset+3]
                h = unpacked_data[dataIndexOffset+4] 
                w = unpacked_data[dataIndexOffset+5] 
                
                if int(tag) != MOCAP_ROGE_DATA:
                    
                    #print tag, x, y, w, h,frame
                    frameStr = str(frame)
                    if locNameDict.has_key(tag):
                        locNameDict[tag]['numOfPointsX'] = locNameDict[tag]['numOfPointsX'] + 1
                        locNameDict[tag]['numOfPointsY'] = locNameDict[tag]['numOfPointsY'] + 1
                        locNameDict[tag]['frameNumberAndPosX'] = locNameDict[tag]['frameNumberAndPosX'] + frameStr + ' ' + x + ' '
                        locNameDict[tag]['frameNumberAndPosY'] = locNameDict[tag]['frameNumberAndPosY'] + frameStr + ' ' + y + ' '
                        locNameDict[tag]['frameNumberAndScaleX'] = locNameDict[tag]['frameNumberAndScaleX'] + frameStr + ' ' + w + ' '
                        locNameDict[tag]['frameNumberAndScaleY'] = locNameDict[tag]['frameNumberAndScaleY'] + frameStr + ' ' + h + ' '
                    else:
                        locNameDict[tag] = dict(numOfPointsX=numOfPointsX,
                                                numOfPointsY=numOfPointsY,
                                                frameNumberAndPosX=frameStr + ' ' + x + ' ',
                                                frameNumberAndPosY=frameStr + ' ' + y + ' ',
                                                frameNumberAndScaleX=frameStr + ' ' + w + ' ',
                                                frameNumberAndScaleY=frameStr + ' ' + h + ' ' ) 
                         
            frame = frame + 1  
        
        asciifile = ''
        header =self.header()
        asciifile = asciifile + header
        for tag in locNameDict.keys():
            locName = "mocaploc_" + str(tag)
            loc = self.creatLocator().substitute(locName=locName)     
            asciifile = asciifile + loc
            
            numOfPointsX = locNameDict[tag]['numOfPointsX']
            numOfPointsY = locNameDict[tag]['numOfPointsY']
            numOfKeysX = numOfPointsX - 1
            numOfKeysY = numOfPointsY - 1
            frameNumberAndPosX = locNameDict[tag]['frameNumberAndPosX']
            frameNumberAndPosY = locNameDict[tag]['frameNumberAndPosY']
            frameNumberAndScaleX = locNameDict[tag]['frameNumberAndScaleX']
            frameNumberAndScaleY = locNameDict[tag]['frameNumberAndScaleY']
            animCurve = self.creatLocatorAnimCurve().substitute(locName=locName,
                                               numOfPointsX=numOfPointsX,
                                               numOfKeysX=numOfKeysX,
                                               frameNumberAndPosX=frameNumberAndPosX,
                                               frameNumberAndScaleX=frameNumberAndScaleX,
                                               numOfPointsY=numOfPointsY,
                                               numOfKeysY=numOfKeysY,
                                               frameNumberAndPosY=frameNumberAndPosY,
                                               frameNumberAndScaleY=frameNumberAndScaleY)
            asciifile = asciifile + animCurve
            
            conectAnim = self.connectAnimCurveToLocator().substitute(locName=locName)
            asciifile = asciifile + conectAnim
            
        footer = self.footer()
        asciifile = asciifile + footer
        #print asciifile
        self.__saveFileStr = asciifile
        
    def __str__(self):
        return self.__saveFileStr
        
    def header(self):
        headerStr = '''
//Maya ASCII 2015 scene
//Name: singleLocWithAnim.ma
//Last modified: Mon, Nov 16, 2015 10:23:55 AM
//Codeset: 1252
requires maya "2015";
currentUnit -l centimeter -a degree -t film;
fileInfo "application" "maya";
fileInfo "product" "Maya 2015";
fileInfo "version" "2015";
fileInfo "cutIdentifier" "201402282131-909040";
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)";\n'''
        return headerStr

    def footer(self):
        footer = '''
select -ne :time1;
    setAttr ".o" 1;
    setAttr ".unw" 1;
select -ne :renderPartition;
    setAttr -s 2 ".st";
select -ne :renderGlobalsList1;
select -ne :defaultShaderList1;
    setAttr -s 2 ".s";
select -ne :postProcessList1;
    setAttr -s 2 ".p";
select -ne :defaultRenderingList1;
select -ne :initialShadingGroup;
    setAttr ".ro" yes;
select -ne :initialParticleSE;
    setAttr ".ro" yes;
select -ne :defaultResolution;
    setAttr ".pa" 1;
select -ne :hardwareRenderGlobals;
    setAttr ".ctrs" 256;
    setAttr ".btrs" 512;
select -ne :hardwareRenderingGlobals;
    setAttr ".otfna" -type "stringArray" 22 "NURBS Curves" "NURBS Surfaces" "Polygons" "Subdiv Surface" "Particles" "Particle Instance" "Fluids" "Strokes" "Image Planes" "UI" "Lights" "Cameras" "Locators" "Joints" "IK Handles" "Deformers" "Motion Trails" "Components" "Hair Systems" "Follicles" "Misc. UI" "Ornaments"  ;
    setAttr ".otfva" -type "Int32Array" 22 0 1 1 1 1 1
         1 1 1 0 0 0 0 0 0 0 0 0
         0 0 0 0 ;
select -ne :defaultHardwareRenderGlobals;
    setAttr ".res" -type "string" "ntsc_4d 646 485 1.333";
// End of singleLocWithAnim.ma\n'''
        return footer

    def creatLocator(self):
        s=Template('''
createNode transform -n "${locName}";
createNode locator -n "${locName}Shape" -p "${locName}";
    setAttr -k off ".v";\n''')
        return s
    
    def creatLocatorAnimCurve(self):
        s=Template('''
createNode animCurveTL -n "${locName}_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsX} ".ktv[0:${numOfKeysX}]"  ${frameNumberAndPosX};
createNode animCurveTL -n "${locName}_translateY";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsY} ".ktv[0:${numOfKeysY}]"  ${frameNumberAndPosY};
createNode animCurveTL -n "${locName}_scaleX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsX} ".ktv[0:${numOfKeysX}]"  ${frameNumberAndScaleX};
createNode animCurveTL -n "${locName}_scaleY";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsY} ".ktv[0:${numOfKeysY}]"  ${frameNumberAndScaleY};\n''')
        return s
        
    def connectAnimCurveToLocator(self):
        s=Template('''
connectAttr "${locName}_translateX.o" "${locName}.tx";
connectAttr "${locName}_translateY.o" "${locName}.ty";
connectAttr "${locName}_scaleX.o" "${locName}.sx";
connectAttr "${locName}_scaleY.o" "${locName}.sy";\n''')
        return s
    
    
