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


class AsciiFile( object ):
    
    def __init__(self):
        pass

    
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
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";'''

    def footer(self):
        footer = '''// End of singleLocWithAnim.ma\n'''

    def creatLocator(self):
        s=Template('''
createNode transform -n "${locName}";
createNode locator -n "${locName}Shape" -p "${locName}";
    setAttr -k off ".v";\n''')
        return s
    
    def creatLocatorAnimCurve(self,locName):
        s=Template('''
createNode animCurveTL -n "${locName}_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsX} ".ktv[0:${numOfKeysX}]"  &{frameNumberAndPosX};
createNode animCurveTL -n "${locName}_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsY} ".ktv[0:${numOfKeysY}]"  &{frameNumberAndPosY};
createNode animCurveTL -n "${locName}_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s ${numOfPointsZ} ".ktv[0:${numOfKeysZ}]"  &{frameNumberAndPosZ};''')
        return s
        
    def connectAnimCurveToLocator(self):
        s=Template('''
connectAttr "&{locName}_translateX.o" "&{locName}.tx";
connectAttr "&{locName}_translateY.o" "&{locName}.ty";
connectAttr "&{locName}_translateZ.o" "&{locName}.tz";\n''')
        return s
    
    
'''
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
fileInfo "osv" "Microsoft Windows 7 Business Edition, 64-bit Windows 7 Service Pack 1 (Build 7601)\n";



createNode transform -n "singleLocWithAnim_locator1";
createNode locator -n "singleLocWithAnim_locator1Shape" -p "singleLocWithAnim_locator1";
    setAttr -k off ".v";
createNode transform -n "locator1";
createNode locator -n "locatorShape1" -p "locator1";
    setAttr -k off ".v";
createNode animCurveTL -n "singleLocWithAnim_locator1_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 4 ".ktv[0:3]"  1 0 2 0 3 4.1385087966918945 4 2.3590928557227313;
createNode animCurveTL -n "singleLocWithAnim_locator1_translateY";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 4 ".ktv[0:3]"  1 0 2 6.3018579483032227 3 14.74535083770752
         4 16.605308624234183;
createNode animCurveTL -n "singleLocWithAnim_locator1_translateZ";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 4 ".ktv[0:3]"  1 0 2 0 3 -2.504094123840332 4 2.1347544772986282;
createNode animCurveTL -n "locator1_translateX";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 7 ".ktv[0:6]"  1 6.6998325815324193 2 30.231028960496985
         3 1.5523515048082857 4 1.1674736695450747 5 7.858830578224584 6 16.109259216797682
         7 -14.486480337679723;
createNode animCurveTL -n "locator1_translateY";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 7 ".ktv[0:6]"  1 0 2 36.222388672868554 3 33.900538497918781
         4 18.863794507813573 5 15.878558568607282 6 21.959594741070752 7 36.332952966903527;
createNode animCurveTL -n "locator1_translateZ";
    setAttr ".tan" 18;
    setAttr ".wgt" no;
    setAttr -s 7 ".ktv[0:6]"  1 0 2 -32.557221237161087 3 -2.1395848638321979
         4 9.507122152304845 5 5.0515695662945177 6 -7.7532752851278417 7 12.077480493516617;
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
connectAttr "singleLocWithAnim_locator1_translateX.o" "singleLocWithAnim_locator1.tx"
        ;
connectAttr "singleLocWithAnim_locator1_translateY.o" "singleLocWithAnim_locator1.ty"
        ;
connectAttr "singleLocWithAnim_locator1_translateZ.o" "singleLocWithAnim_locator1.tz"
        ;
connectAttr "locator1_translateX.o" "locator1.tx";
connectAttr "locator1_translateY.o" "locator1.ty";
connectAttr "locator1_translateZ.o" "locator1.tz";
// End of singleLocWithAnim.ma
'''