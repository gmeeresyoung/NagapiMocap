'''
Created on 5 Oct 2015

@author: gregmeeresyoung
'''
import sys,os

from PyQt4 import QtCore
from PyQt4 import QtGui 
from PyQt4.QtGui import QMessageBox

from MocapMainWindow_ui import Ui_MainWindow
from MocapEditDialog import EditDiolog
from MocapClientDialog import ClientDiolog
import yaml
import re

from MocapGraphicsView import MocapBox
from nagapi.MocapServer import Server,LocalClient,LocalPixey
from nagapi.MocapUtils import *

from nagapi.nagapi import FpsClock
###
# Initalize fps clock
fpsclock = FpsClock(10)
###

class MainWindow( QtGui.QMainWindow, Ui_MainWindow ):
    
    
    def __init__(self, parent=None):
        
        super(MainWindow,self).__init__(parent)
        super(MainWindow,self).setupUi(self)

        self.thread = None#Server(self)
        
        self.BoxSceneItems = dict()
        self.boxesLastFrame = dict()
        self.mode = "stopedRecording"
        
        self.fpsDisplay = QtGui.QLCDNumber(self)
        self.statusBar().addPermanentWidget(self.fpsDisplay)
        
        
        self.graphicsViewIsModifyed = False
        self.clientDialog = ClientDiolog(self)
        self.editDiolog = EditDiolog(self)
        self.connectActions()
        self.curFile = ''
        self.curRecordFile = ''
        self.recordingModifyed = False
        
        self.readSettings()
        
        #rf = open('C:\\Users\\gregmeeresyoung\\git\\NagapiMocap\\nagapi\\mocapScenes\\newTestrecord.raw','r')
        #AsciiFile(rf)
        #rf.close()
    
    def connectTreadSingals(self):
        self.connect(self.thread, QtCore.SIGNAL("subFrame(int, long, long, long, long)"), self.updateSubframe)
        self.connect(self.thread, QtCore.SIGNAL("frameEnd()"), self.updateFrame)
        self.connect(self.thread, QtCore.SIGNAL("stopingServer()"), self.stopingServer)
                
        self.connect(self, QtCore.SIGNAL("recording(QString)"), self.thread.startRecording)
        self.connect(self, QtCore.SIGNAL("stopRecording()"), self.thread.stopRecording)
        self.connect(self, QtCore.SIGNAL("closeThred()"), self.thread.closeThred)
            
    def connectActions(self):
        self.connect(self.actionListenForConnections, QtCore.SIGNAL("triggered(bool)"), self.openServer)
        self.connect(self.actionClassifiedData, QtCore.SIGNAL("triggered(bool)"), self.clasifyData)
        self.connect(self.actionRawData, QtCore.SIGNAL("triggered(bool)"), self.rawData)
        self.connect(self.actionRecordMocap, QtCore.SIGNAL("triggered(bool)"), self.recordMocap)
        
        
        self.connect(self.actionFilterData, QtCore.SIGNAL("triggered(bool)"),self.filterData)
        
        self.connect(self.action_Close, QtCore.SIGNAL("triggered()"), self.close)
        self.connect(self.action_Open, QtCore.SIGNAL("triggered()"), self.open)
        self.connect(self.action_Save, QtCore.SIGNAL("triggered()"), self.save)
        self.connect(self.action_Save_as, QtCore.SIGNAL("triggered()"), self.saveAs)
        self.connect(self.action_New, QtCore.SIGNAL("triggered()"), self.newFile)
        self.connect(self.actionAbout_nagapi_mocap, QtCore.SIGNAL("triggered()"), self.about)
        self.connect(self.actionEditClasificationRegen, QtCore.SIGNAL("triggered()"), self.showEditDialog)
        self.connect(self.actionAddClasificationRegen, QtCore.SIGNAL("triggered()"), self.startAddClasificationRegen)
        self.connect(self.actionDelet_selected, QtCore.SIGNAL("triggered()"),self.graphicsView.deletSelected)
        
        self.connect(self.graphicsView, QtCore.SIGNAL("regenEditEnd()"), self.updateClasifyData)
        self.connect(self.graphicsView, QtCore.SIGNAL("regenEditEnd()"), self.blockEditDiolog)
        self.connect(self.graphicsView, QtCore.SIGNAL("regenEditEnd()"), self.endAddClasificationRegen)
        self.connect(self.graphicsView, QtCore.SIGNAL("updateEditData()"), self.updateEditData)
        
        self.connect(self.editDiolog.spinBox_width, QtCore.SIGNAL("valueChanged(int)"), self.graphicsView.resizeSelectedWidth)
        self.connect(self.editDiolog.spinBox_height, QtCore.SIGNAL("valueChanged(int)"), self.graphicsView.resizeSelectedHight)
        self.connect(self.editDiolog.spinBox_colID, QtCore.SIGNAL("valueChanged(int)"), self.graphicsView.updateColour)
        
        self.connect(self.editDiolog.spinBox_colID, QtCore.SIGNAL("valueChanged(int)"), self.graphicsView.updateColour)
        
        self.connect(self.editDiolog.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*"), self.updatRegenData)
        self.connect(self.editDiolog.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.updatRegenData)
    
    def updateSmartBox(self):
        self.thread.smartFilterBoxSize 
    
    def updateOutputChannel(self):
        sender = self.sender()
        senderName = str(sender.objectName())
        channel = re.match("[\s\S]+_([xywh]$)", senderName).group(1)
        tag = self.graphicsView.regenSelected().getTag()
        self.thread.updateOutputChannel(tag,channel,sender.isChecked())
    
    def updateBufferSize(self):
        sender = self.sender()
        senderName = str(sender.objectName())
        channel = re.match("[\s\S]+_([xywh]$)", senderName).group(1)
        tag = self.graphicsView.regenSelected().getTag()        
        self.thread.updateBufferSize(tag,channel,sender.value())

    def updateLowPassFreq(self):
        sender = self.sender()
        senderName = str(sender.objectName())
        channel = re.match("[\s\S]+_([xywh]$)", senderName).group(1)
        tag = self.graphicsView.regenSelected().getTag()        
        self.thread.updateLowPassFreq(tag,channel,sender.value())
    
    def updateFilterType(self,toggle):
        sender = self.sender()
        senderName = str(sender.objectName())
        channel = re.match("[\s\S]+_([xywh]$)", senderName).group(1)
        filterType = re.match("([\s\S]+)_([xywh]$)", senderName).group(1)
        tag = self.graphicsView.regenSelected().getTag()      
        
        if filterType == 'radioButton_noF':
            self.thread.updateFilterType(tag,channel,Server.nofilter)
        elif filterType == 'radioButton_gAve':
            self.thread.updateFilterType(tag,channel,Server.gouseanFilter)
        elif filterType == 'radioButton_lowPassF':
            self.thread.updateFilterType(tag,channel,Server.lowPassFilter)
    
    def filterData(self,on):
        if on:
            self.actionRawData.setChecked(False)
            self.actionClassifiedData.setChecked(True)
            data = self.graphicsView.getClasificationRegens()
            if self.thread:
                self.thread.clasifyData(data)
                self.thread.filterData()
        else:
            if self.thread:
                self.thread.filterOff()
     
    def updateClasifyData(self):
        if self.graphicsView.regenSelected() and self.actionFilterData.isChecked():
            self.filterData(True)
        elif self.graphicsView.regenSelected() and self.actionClassifiedData.isChecked():
            self.clasifyData(True)
            
    def clasifyData(self,on):
        if on:
            self.actionRawData.setChecked(False)
            data = self.graphicsView.getClasificationRegens()
            if self.thread:
                self.thread.clasifyData(data)
        else:
            self.actionRawData.setChecked(True)
            self.actionFilterData.setChecked(False)
            if self.thread:
                self.thread.rawData()

    def rawData(self,on):
        if on:
            self.actionClassifiedData.setChecked(False)
            self.actionFilterData.setChecked(False)
            self.thread.rawData()
        elif not self.actionClassifiedData.isChecked():
            self.actionRawData.setChecked(True)
            self.thread.rawData()            
          
    def recordMocap(self,startRec):
        if self.thread:
            if startRec:
                self.newRecordingFile()
            else:
                print "stop recording"
                self.emit(QtCore.SIGNAL("stopRecording()"))
                self.saveRecordingAs()
               
    def updateSubframe(self,tag,x,y,w,h):
        #convert from camera spcae to screen space
        screenSpace_x,screenSpace_y = x*2,y*2
        screenSpace_w,screenSpace_h = w*2,h*2      
        
        lcx = screenSpace_x - (screenSpace_w/2)
        lcy = screenSpace_y - (screenSpace_h/2)
        

        if self.BoxSceneItems.has_key(tag):
            self.BoxSceneItems[tag].show()
            
            self.BoxSceneItems[tag].setRect (lcx, lcy, screenSpace_w, screenSpace_h)
            self.BoxSceneItems[tag].lable.setText(str(tag))
        else:
            self.BoxSceneItems[tag] = MocapBox(lcx, lcy, screenSpace_w, screenSpace_h)
            
            self.BoxSceneItems[tag].setRect (lcx, lcy, screenSpace_w, screenSpace_h)
            self.BoxSceneItems[tag].lable.setText(str(tag))
            
            self.graphicsView.addMocapBox(self.BoxSceneItems[tag])       
        
        if self.boxesLastFrame.has_key(tag):
            self.boxesLastFrame.pop(tag, None)

    def updateFrame(self):
        
        for tag,mbox in self.boxesLastFrame.items():
            mbox.hide()

        for  tag,mbox in self.BoxSceneItems.items():
            self.boxesLastFrame[tag] = mbox 


        self.fpsDisplay.display(int(fpsclock.speed())) 

    def openServerOld(self,lisen):
        #currentFile = self.getCurrentFile()
        #display ui for inputing client programs for mocap client and plugin client 
        if lisen:
            if self.clientDialog.exec_():
                             
                if self.clientDialog.radioButton_remote.isChecked():
                    
                    self.thread = Server()
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)     
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass
                    
                    self.connectTreadSingals()
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)
                    
                    lisenPort = int(self.clientDialog.comboBox_lisenPort.itemText(self.clientDialog.comboBox_lisenPort.currentIndex()))
                    mocapClientIP = self.clientDialog.comboBox_mocapIP.itemText(self.clientDialog.comboBox_mocapIP.currentIndex())
                    pluginClientIP = self.clientDialog.comboBox_pluginIP.itemText(self.clientDialog.comboBox_pluginIP.currentIndex())
                    print "starting server"
                    self.thread.render(lisenPort,mocapClientIP,pluginClientIP)
                    self.statusBar().showMessage("Lisinging for clients", 0)
                    
                
                elif self.clientDialog.radioButton_local.isChecked():
                    
                    rawTempFile = self.getTempFile()
                    self.thread = LocalClient(rawTempFile)
                    
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)                    
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass
                    
                    self.connectTreadSingals()
                    
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)
                                      
                    self.thread.render()
                    self.statusBar().showMessage("Running local client", 0)
            
                else:
                    self.thread = LocalPixey()
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)                    
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass

                    self.connectTreadSingals()
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)
                    
                    self.thread.render()
                    self.statusBar().showMessage("Running local client", 0)                    
            else:
                self.actionListenForConnections.setChecked(False)
        else:
            
            self.emit(QtCore.SIGNAL("closeThred()"))#self.thread.closeServer()
 
    def openServer(self,lisen):
        #currentFile = self.getCurrentFile()
        #display ui for inputing client programs for mocap client and plugin client 
        if lisen:
            if self.clientDialog.exec_():
                             
                if self.clientDialog.radioButton_remote.isChecked():
                    
                    self.thread = Server()
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)     
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass
                    
                    self.connectTreadSingals()
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)
                    
                    lisenPort = int(self.clientDialog.comboBox_lisenPort.itemText(self.clientDialog.comboBox_lisenPort.currentIndex()))
                    mocapClientIP = self.clientDialog.comboBox_mocapIP.itemText(self.clientDialog.comboBox_mocapIP.currentIndex())
                    pluginClientIP = self.clientDialog.comboBox_pluginIP.itemText(self.clientDialog.comboBox_pluginIP.currentIndex())
                    print "starting server"
                    self.thread.render(lisenPort,mocapClientIP,pluginClientIP)
                    self.statusBar().showMessage("Lisinging for clients", 0)
                    
                
                elif self.clientDialog.radioButton_local.isChecked():
                    
                    serverThread = None
                    if self.clientDialog.groupBox_2.isChecked():
                        print "creating that servers boyo"
                        serverThread = Server()
                        
                    rawTempFile = self.getTempFile()
                    self.thread = LocalClient(rawTempFile)
                    self.thread.setServer(serverThread)
                    
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)                    
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass
                    
                    self.connectTreadSingals()
                    
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)
                    
                    lisenPort = int(self.clientDialog.comboBox_lisenPort.itemText(self.clientDialog.comboBox_lisenPort.currentIndex()))
                    mocapClientIP = None#self.clientDialog.comboBox_mocapIP.itemText(self.clientDialog.comboBox_mocapIP.currentIndex())
                    pluginClientIP = self.clientDialog.comboBox_pluginIP.itemText(self.clientDialog.comboBox_pluginIP.currentIndex())                  
                    
                    print lisenPort,mocapClientIP,pluginClientIP
                    self.thread.render(lisenPort,mocapClientIP,pluginClientIP)
                    self.statusBar().showMessage("Running local client", 0)
            
                else:
                    
                    serverThread = None
                    if self.clientDialog.groupBox_2.isChecked():
                        print "creating that servers boyo"
                        serverThread = Server()
                        
                    self.thread = LocalPixey()
                    self.thread.setServer(serverThread)
                    
                    for clasifyData in self.graphicsView.getData().values():
                        if self.thread:
                            self.thread.buildFromData(clasifyData)                    
                    
                    if self.actionFilterData.isChecked():
                        self.filterData(True)
                    elif self.actionClassifiedData.isChecked():
                        self.clasifyData(True)
                    else:
                        pass

                    self.connectTreadSingals()
                    if self.actionRecordMocap.isChecked():
                        self.recordMocap(True)

                    lisenPort = int(self.clientDialog.comboBox_lisenPort.itemText(self.clientDialog.comboBox_lisenPort.currentIndex()))
                    mocapClientIP = None#self.clientDialog.comboBox_mocapIP.itemText(self.clientDialog.comboBox_mocapIP.currentIndex())
                    pluginClientIP = self.clientDialog.comboBox_pluginIP.itemText(self.clientDialog.comboBox_pluginIP.currentIndex())                  
                    
                    print lisenPort,mocapClientIP,pluginClientIP                   
                    self.thread.render(lisenPort,mocapClientIP,pluginClientIP )
                    self.statusBar().showMessage("Running local client", 0)                    
            else:
                self.actionListenForConnections.setChecked(False)
        else:
            
            self.emit(QtCore.SIGNAL("closeThred()"))#self.thread.closeServer()    
    
    def stopingServer(self):
        self.actionListenForConnections.setChecked(False)
        QMessageBox.information(self.parent(), " Server",
                "Closing liserning server.")        

    def updatRegenData(self,buttion):
        regen = self.graphicsView.regenSelected()
        if regen:
            if buttion.text () in ("Apply",'OK'):
                data = self.editDiolog.getData()
                regen.setData(data)
                if self.thread:
                    self.thread.buildFromData(data)
                self.statusBar().showMessage("upedated regen %s"%data['name'], 2000)
    
    def blockEditDiolog(self):
        regen = self.graphicsView.regenSelected()
        if not regen:
            self.editDiolog.setDisabled(True)
        else:
            self.editDiolog.setEnabled(True)
            
    def updateEditData(self):
        self.editDiolog.updatData(self.graphicsView.regenSelected().clasifyData)
    
    def startAddClasificationRegen(self):
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape(2)))
        self.graphicsView.editRegen = True
    
    def endAddClasificationRegen(self):
        self.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape(0)))
        self.graphicsView.editRegen = False
        
    def showEditDialog(self):
        regen = self.graphicsView.regenSelected()
        if regen:
            self.editDiolog.updatData(regen.clasifyData)
            self.editDiolog.show()
        
    def closeEvent(self, event):
        # do stuff
        print "cleanup"
        if self.thread:
            self.thread.stopRecording()
            self.thread.exiting = True
        
        if self.maybeSave():
            self.writeSettings()
            event.accept()
        else:
            event.ignore()  

    def newFile(self):
        if self.maybeSave():
            self.graphicsView.clear()
            self.setCurrentFile('')
    
    def newRecordingFile(self):
        print "new recording"
        if self.maybeRecordingSave():
            self.setRecordCurrentFile('mocapRecording.tmp')
            self.emit(QtCore.SIGNAL("recording(QString)"),self.curRecordFile)
            print "start temp file recroding"

    def getTempFile(self):
            fileName = QtGui.QFileDialog.getOpenFileName(self)
            if fileName:
                return fileName
            return None
        
    def open(self):
        if self.maybeSave():
            fileName = QtGui.QFileDialog.getOpenFileName(self)
            if fileName:
                self.loadFile(fileName)

    def save(self):
        if self.curFile:
            return self.saveFile(self.curFile)

        return self.saveAs()
    
    def saveRecording(self):
        if self.curRecordFile:
            return self.saveRecordingFile('')

        return self.saveRecordingAs()        
    
    def saveAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "save setup", "", "setup Files (*.txt)")
        if fileName:
            return self.saveFile(fileName)

        return False

    def saveRecordingAs(self):
        fileName = QtGui.QFileDialog.getSaveFileName(self, "Save Mocap", "", "Mocap Files (*.raw *.mocap *.ma)")
        if fileName:
            return self.saveRecordingFile(fileName)
        return False

    def about(self):
        QtGui.QMessageBox.about(self, "About Application",
                "The <b>Application</b> example demonstrates how to write "
                "modern GUI applications using Qt, with a menu bar, "
                "toolbars, and a status bar.")

    def documentWasModified(self):
        self.setWindowModified(self.graphicsView.isModified())

    def setCurrentFile(self, fileName):
        self.curFile = fileName
        self.graphicsView.setModified(False)
        self.setWindowModified(False)

        if self.curFile:
            shownName = self.strippedName(self.curFile)
        else:
            shownName = 'untitled.mcap'

        self.setWindowTitle("%s[*] - Nagapi Mocap" % shownName)
    
    def getCurrentFile(self):
        return self.curFile

    def setRecordCurrentFile(self, fileName):
        self.curRecordFile = fileName
        #set record file to modifyed ??
        self.recordingModifyed = True
        if self.curRecordFile:
            shownName = self.strippedName(self.curRecordFile)
        else:
            shownName = 'mocapRecording.tmp'
        
        self.statusBar().showMessage("Recording mocap", 2000)
        #self.setWindowTitle("%s[*] - Nagapi Mocap" % shownName)

    def strippedName(self, fullFileName):
        return QtCore.QFileInfo(fullFileName).fileName()

    def loadFile(self, fileName):
        qfile = QtCore.QFile(fileName)
        if not qfile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "Cannot read file %s:\n%s." % (fileName, file.errorString()))
            return

        inf = file(qfile.fileName(), 'r')
        
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        self.graphicsView.clear()
        for data in yaml.load_all(inf):
            for clasifyData in data.values():
                self.graphicsView.buildFromData(clasifyData)
                if self.thread:
                    self.thread.buildFromData(clasifyData) 
        
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName)
        self.statusBar().showMessage("File loaded", 2000)

    def saveFile(self, fileName):
        qfile = QtCore.QFile(fileName)
        if not qfile.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False
        stream = file(qfile.fileName(), 'w')
        QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        
        self.graphicsView.dumpData(stream) 
        stream.close()
        QtGui.QApplication.restoreOverrideCursor()

        self.setCurrentFile(fileName);
        self.statusBar().showMessage("File saved", 2000)
        return True

    def saveRecordingFile(self, fileName):
        file = QtCore.QFile(fileName)
        
        fileName,ext = os.path.splitext(str(file.fileName()))
        
        if not file.open(QtCore.QFile.WriteOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "Cannot write file %s:\n%s." % (fileName, file.errorString()))
            return False
        #fileName = qfile.fileName()
        outf = QtCore.QTextStream(file)
        QtGui.QApplication.restoreOverrideCursor()
        
        tmpfile = QtCore.QFile(self.curRecordFile)
        if not tmpfile.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
            QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "Cannot write file %s:\n%s." % (self.curRecordFile, tmpfile.errorString()))        
        
        if ext == '.raw': 
            outf << tmpfile.readAll()
        if ext == '.mocap':
            print "convert to mocap format filterd and clasifyed"
            outf << tmpfile.readAll()
        if ext == '.ma':
            print "convert ot maya ascii format"
            setupData = self.graphicsView.getData()
            outf << str(AsciiFile(tmpfile,setupData))
           
        tmpfile.close()
        self.recordingModifyed = False
        self.statusBar().showMessage("Mocap saved", 2000)
        return True
          
    def maybeSave(self):
        return True
    
    def maybeRecordingSave(self):
        
        if self.recordingModifyed:#if added new rectangels
            ret = QtGui.QMessageBox.warning(self, "Nagapi Mocap",
                    "The document has been modified.\nDo you want to save "
                    "your changes?",
                    QtGui.QMessageBox.Save | QtGui.QMessageBox.Discard |
                    QtGui.QMessageBox.Cancel)
            if ret == QtGui.QMessageBox.Save:
                return self.saveRecording()
            elif ret == QtGui.QMessageBox.Cancel:
                return False
        return True

    def writeSettings(self):
        print "writ settings"
        settings = QtCore.QSettings("Nagapi", "NagapiMocap")
        settings.beginGroup("ClientDiolog")
        
        settings.beginWriteArray("mocapIPs")
        settings.setValue("currentIndex", self.clientDialog.comboBox_mocapIP.currentIndex())
        size = self.clientDialog.comboBox_mocapIP.count()
        settings.setValue("size",size)
        for index in range(size):
            settings.setArrayIndex(index);
            settings.setValue("text", self.clientDialog.comboBox_mocapIP.itemText(index))
        settings.endArray()
        
        settings.beginWriteArray("pluginIPs")
        settings.setValue("currentIndex", self.clientDialog.comboBox_pluginIP.currentIndex())
        size =self.clientDialog.comboBox_pluginIP.count()
        settings.setValue("size",size)
        for index in range(size):
            settings.setArrayIndex(index);
            settings.setValue("text", self.clientDialog.comboBox_pluginIP.itemText(index))
        settings.endArray()
        
        settings.endGroup()
        
    def readSettings(self):
        settings =  QtCore.QSettings("Nagapi", "NagapiMocap")
        settings.beginGroup("ClientDiolog")
        
        for i in settings.allKeys(): print i,settings.value(i).toString()
        
        self.clientDialog.comboBox_mocapIP.clear()
        size = settings.beginReadArray("mocapIPs")
        currentIndex = settings.value("currentIndex").toString()
        for i in range(size):
            settings.setArrayIndex(i)
            self.clientDialog.comboBox_mocapIP.addItem(settings.value("text").toString())
        
        settings.endArray()

        
        currentIndex = int(currentIndex) if currentIndex  else 0
        self.clientDialog.comboBox_mocapIP.setCurrentIndex(currentIndex)
        
        self.clientDialog.comboBox_pluginIP.clear()
        size = settings.beginReadArray("pluginIPs")
        currentIndex = settings.value("currentIndex").toString()
        for i in range(size):
            settings.setArrayIndex(i)
            self.clientDialog.comboBox_pluginIP.addItem(settings.value("text").toString())
        
        settings.endArray()

        currentIndex = int(currentIndex) if currentIndex else 0
        self.clientDialog.comboBox_pluginIP.setCurrentIndex(currentIndex)
        settings.endGroup()        

    
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_()) 