'''
Created on 29 Sep 2015

@author: gregmeeresyoung
'''
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import sys,os,re
import socket
import select
import Queue
from collections import deque
import ctypes
import struct


from nagapi.nagapi import FpsClock
###
# Initalize fps clock
fpsclock = FpsClock(10)
###
# goloble commands
#
# plugin commands
CMD_NEW_FRAME = 1002
# mocap commnds
MOCAP_CLASSIFY_DATA = 2222
MOCAP_RAW_DATA = 3333
MOCAP_ROGE_DATA = 9999
# server commands
SERVER_RECORD_DATA = 4444


from scipy.ndimage import filters
from scipy.interpolate import UnivariateSpline
from collections import deque
from scipy.signal import gaussian,butter,lfilter

class CircularBuffer(deque):
    def __init__(self, size=0):
        super(CircularBuffer, self).__init__(maxlen=size)
        self._b = gaussian(39, 10)
        self._lb, self._la = butter(4, .1, 'lowpass', analog=False)

    def filterGauss(self):
        return filters.convolve1d(self, self._b/self._b.sum())[-1]
    
    def filterButterworth(self):
        fl = lfilter(self._lb,self._la, self)[-1]
        return long(fl)
    

class MocapBox(QGraphicsItem):

    # Create the bounding rectangle once.
    adjust = 0.5
    #BoundingRect = QRectF(-10, -20, 20, 40)

    def __init__(self,w,h):
        super(MocapBox, self).__init__()
        self.color = QColor(qrand() % 256, qrand() % 256,
                        qrand() % 256)
        self.penWidth = 1.0
        self.w = w
        self.h = h
        #self.BoundingRect = QRectF(-(w/2), -(h/2), w/2, h/2)
        
    def boundingRect(self):
        return QRectF(-((self.w - self.penWidth)/2),
                       -((self.h - self.penWidth)/2),
                       (self.w + self.penWidth)/2,
                       (self.h + self.penWidth)/2)

    def shape(self):
        path = QPainterPath()
        path.addRect(-(self.w/2), -(self.h/2), self.w/2, self.h/2)
        return path;

    def paint(self, painter, option, widget):
        # Body.
        painter.setBrush(self.color)
        painter.drawRect(-(self.w/2), -(self.h/2), self.w/2, self.h/2)
        
    def scaleBox(self,w,h):
        self.w = w
        self.h = h
        
        
class Server(QThread):

    def __init__(self, parent = None):
    
        QThread.__init__(self, parent)
        self.exiting = False
        self.commandFromServer=None
        
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setblocking(0)
        
        # Bind the socket to the port
        server_address = ('', 10000)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        self.tcpServer.bind(server_address)
        
        # Listen for incoming connections
        self.tcpServer.listen(2)
        
        # wait for a connection for give time then close in none found
        self.timeout = 60
        
        # Sockets from which we expect to read
        self.inputs = [ self.tcpServer ]
        self.mocapSendClientIP = ['192.168.0.17']
        
        
        # Sockets to which we expect to write
        self.outputs = [ ]
        self.readCliantIP = ['192.168.0.10']
        
        # Give the connection a queue for data we want to send/ reseve
        self.data_queues = dict()
        self.receve_queues = dict()
        self.pluginCommand = dict()
        
        # set up data streem for commands 
        self.packer_cmd = struct.Struct('I')
        self.cmdBuffer = ctypes.create_string_buffer(self.packer_cmd.size)
        self.amount_expected_cmd = self.packer_cmd.size
        # setup data streem for mocp data
        self.filterBufferSize = 100
        self.maxPoints = 20
        self.pointDataSize = 5        
        self.packer_data = struct.Struct(self.buildPacker(self.maxPoints,self.pointDataSize))
        self.sendDataBuffer = ctypes.create_string_buffer(self.packer_data.size)
        self.amount_expected_mocap = self.packer_data.size
                
        self.filterDataFlag = False
        self.frameDataBuffer = self.buildFrameData(self.maxPoints,self.pointDataSize) 
        self.filterBuffers = {rbID:dict(bx=CircularBuffer(size=self.filterBufferSize),
                                        by=CircularBuffer(size=self.filterBufferSize)) for rbID in xrange(0,self.maxPoints)}
        # file recording
        finc = 0
        fileName = "mocapRecording" 
        self.recordToFile = False
        self.openRecording = False
        for f in os.listdir("./"):
            if re.search(fileName, f):
                finc = finc + 1
        self.rocodingFileName = '%s%d.txt'%(fileName,finc)
        
    def buildPacker(self,numOfpoints,pointLength):
        frameData = ""
        pointData = "I"#'I I I I I'
        for i in xrange(1,pointLength):
            pointData  = pointData + " I"
             
        for i in xrange(0,numOfpoints):
            frameData = frameData +" "+ pointData
    
        return frameData
    
    def buildFrameData(self,numOfpoints,pointDataSize):
        frameData = []
        for pindex in xrange(0,numOfpoints):
            for dindex in xrange(0,pointDataSize):
                frameData.append(MOCAP_ROGE_DATA)
        return frameData
    
    def __del__(self):
        print "deleating thred"
        self.exiting = True
        self.tcpServer.close()
        self.wait()       
         
    def render(self):
        self.start()
    
    def clasifyData(self):
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        self.filterDataFlag = False 
           
    def rawData(self):
        self.commandFromServer = MOCAP_RAW_DATA
        # not point filtering unclasifyed data
        self.filterDataFlag = False
    
    def filterData(self):
        print "filter data"
        #data needs to be clasifyed to filter
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        self.filterDataFlag = True
        
    def startRecording(self):
        print "start recording",self.rocodingFileName
        self.openRecording = open(self.rocodingFileName, "w")
        #self.recordToFile = True
    
    def stopRecording(self):
        print "stop recording",self.rocodingFileName
        if self.openRecording:
            self.openRecording.close()
            self.openRecording = None
        #self.recordToFile = False
       
    def run(self):
        
        while not self.exiting and self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, self.timeout)    
            
            if not (readable or writable or exceptional):
                print >>sys.stderr, '  timed out, onting connected within 60 sec'
                QMessageBox.critical(self, " Server",
                        "Unable to start the server.")
                self.tcpServer.close()
                self.close()
                break
            
            # Handle inputs
            for s in readable:        
                if s is self.tcpServer:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print >>sys.stderr, 'new connection from', client_address
                    connection.setblocking(0)                
                    # sort cnections for imputs and output servers
                    if client_address[0] in self.readCliantIP:
                        
                        # only alow one plugin connection at the mo
                        # if already output remove befor adding new one
                        #append new imput connection 
                        self.outputs.append(connection)
                        # ring buffer might be slow
                        self.data_queues[connection] = deque(maxlen =500)#Queue.Queue(maxsize=1000)#LifoQueue
                        self.pluginCommand[connection] = None
                        self.receve_queues[connection] = (Queue.Queue(),self.packer_cmd,self.amount_expected_cmd)
                        self.inputs.append(connection)
                        
                    elif client_address[0] in self.mocapSendClientIP: 
                        self.inputs.append(connection)
                        self.outputs.append(connection)
                        self.pluginCommand[connection] = None
                        self.receve_queues[connection] = (Queue.Queue(),self.packer_data,self.amount_expected_mocap)
                    
                    else:
                        raise "dont know this server",client_address
                else: 
                    # Look for the response
                    queue,packer,amount_expected  = self.receve_queues[s]
                    try:
                        amount_received,dataBuffer = queue.get_nowait()
                    except Queue.Empty:
                        amount_received,dataBuffer = (0,"")# get from mesage que
                                
                    dataBuffer = dataBuffer + s.recv(amount_expected - amount_received)            
                    amount_received = len(dataBuffer)
                                
                    if amount_expected == amount_received:
        
                        unpacked_data = packer.unpack_from(dataBuffer, 0)
                        
                        ##
                        # get commad form plugin client
                        #
                        if amount_expected == self.amount_expected_cmd: 
                            for key in self.data_queues.keys():
                                self.pluginCommand[s] = unpacked_data[0]
                        ##
                        # get data from mocap client 
                        #                              
                        elif   amount_expected == self.amount_expected_mocap:
                            
                            if self.openRecording:
                                self.openRecording.write(str(unpacked_data) + "\n")
                            ##
                            # look for user input commands 
                            #
                            if self.commandFromServer:
                                self.pluginCommand[s] = self.commandFromServer
                                # reset servercommand
                                self.commandFromServer = None
                            
                            for index in xrange(0,self.maxPoints):
                                dataIndexOffset = 0
                                if index != 0:
                                    dataIndexOffset = index * self.pointDataSize

                                tag = unpacked_data[dataIndexOffset]
                                x = unpacked_data[dataIndexOffset+1]
                                y = unpacked_data[dataIndexOffset+2] 
                                w = unpacked_data[dataIndexOffset+3] 
                                h =unpacked_data[dataIndexOffset+4] 

                                if tag != MOCAP_ROGE_DATA:
                                    
                                    if self.filterDataFlag:
                                        self.filterBuffers[tag]['bx'].append(x)
                                        self.filterBuffers[tag]['by'].append(y)
                                        x = self.filterBuffers[tag]['bx'].filterButterworth()       
                                        y = self.filterBuffers[tag]['by'].filterButterworth()                                        
                                        self.frameDataBuffer[dataIndexOffset] = tag
                                        self.frameDataBuffer[dataIndexOffset+1] = x
                                        self.frameDataBuffer[dataIndexOffset+2] = y
                                        self.frameDataBuffer[dataIndexOffset+3] = w
                                        self.frameDataBuffer[dataIndexOffset+4] = h

                                    self.emit(SIGNAL("subFrame(int, long, long, long, long)"),
                                              tag, x, y,w,h)
                            
                            if self.filterDataFlag:
                                unpacked_data = self.frameDataBuffer
                            self.emit(SIGNAL("frameEnd()"))                            
                            packer.pack_into(self.sendDataBuffer, 0, *unpacked_data)
                            #recordingFile.write(str(unpacked_data)+"\n")
                            for key in self.data_queues.keys():
                                self.data_queues[key].append(self.sendDataBuffer)                                        
    
                    else:
                        # set for next pass
                        queue.put((amount_received,dataBuffer))
    
            # Handle outputs
            for s in writable:
    
                if self.pluginCommand[s] == CMD_NEW_FRAME:
                    try:
            
                        next_msg = self.data_queues[s].pop()
                        
                    except IndexError:
                        # No messages waiting so stop checking for writability.
                        print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
                    else:
                        s.send(next_msg)
                        self.pluginCommand[s] =  None
            
                elif  self.pluginCommand[s] == MOCAP_CLASSIFY_DATA:
                    print "sending clasify comand to mocap cliant"
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_CLASSIFY_DATA) 
                    s.send(self.cmdBuffer)
                    self.pluginCommand[s] = None
                
                elif self.pluginCommand[s] == MOCAP_RAW_DATA:
                    print "sending raw data comand to cliant"
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_RAW_DATA) 
                    s.send(self.cmdBuffer)
                    self.pluginCommand[s] = None
                else:
                    # no commands to exicutep
                    self.pluginCommand[s] = None            
            
            # Handle "exceptional conditions"
            for s in exceptional:
                print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
                # Stop listening for input on the connection
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()
                # close recoding to file
                #recordingFile.close()
                # Remove message queue
                del self.data_queues[s]
                del self.receve_queues[s]
                        
                  

class Window(QWidget):

    def __init__(self, parent = None):
    
        QWidget.__init__(self, parent)
        
        self.thread = Server()
        self.startButton = QPushButton(self.tr("&Start"))
        self.clasifyButton = QPushButton(self.tr("&Clasify"))
        self.filterButtion = QPushButton(self.tr("&Filter")) 
        self.addClasifyBox = QPushButton(self.tr("&AddClasBox"))
        self.rawButton = QPushButton(self.tr("&Raw"))
        self.recordButton = QPushButton(self.tr("&Record"))
        self.mode = "stopedRecording"
        self.fpsDisplay = QLCDNumber(self)
        
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 640, 400)
        self.scene.setItemIndexMethod(QGraphicsScene.NoIndex)        
        self.BoxSceneItems = dict()
        self.boxesLastFrame = dict()
        
        self.viewer = QGraphicsView(self.scene)
        self.viewer.setRenderHint(QPainter.Antialiasing)
        self.viewer.setCacheMode(QGraphicsView.CacheBackground)
        
        
        self.connect(self.thread, SIGNAL("subFrame(int, long, long, long, long)"), self.updateSubframe)
        self.connect(self.thread, SIGNAL("frameEnd()"), self.updateFrame)
        self.connect(self.startButton, SIGNAL("clicked()"), self.openServer)
        self.connect(self.clasifyButton, SIGNAL("clicked()"), self.clasifyData)
        self.connect(self.rawButton, SIGNAL("clicked()"), self.rawData)
        self.connect(self.recordButton, SIGNAL("clicked()"), self.updateUi)
        
        self.connect(self, SIGNAL("recording()"), self.thread.startRecording)
        self.connect(self, SIGNAL("stopRecording()"), self.thread.stopRecording)
        self.connect(self.filterButtion, SIGNAL("clicked()"), self.thread.filterData)
        
        layout = QGridLayout()
        layout.addWidget(self.startButton, 0, 0)
        layout.addWidget(self.clasifyButton, 0, 1)
        layout.addWidget(self.rawButton, 0, 2)
        layout.addWidget(self.filterButtion, 0, 3)
        layout.addWidget(self.recordButton, 0, 4)
        layout.addWidget(self.viewer, 1, 0, 1, 5)
        layout.addWidget(self.fpsDisplay, 2,4)
        
        self.setLayout(layout)
        
        self.setWindowTitle(self.tr("Nagapi server")) 
            
        
    def clasifyData(self):
        self.thread.clasifyData()

    def rawData(self):
        self.thread.rawData()
           
    def updateUi(self):
        if self.mode == "stopedRecording":
            self.recordButton.setText("&Stop rec")
            self.emit(SIGNAL("recording()"))
            self.mode = "recording"
        elif self.mode == "recording":
            self.recordButton.setText("&Record")
            self.emit(SIGNAL("stopRecording()"))
            self.mode = "stopedRecording"
    
    def updateSubframe(self,tag,x,y,w,h):
        
        if self.BoxSceneItems.has_key(tag):
            self.BoxSceneItems[tag].show()
            self.BoxSceneItems[tag].setPos(x*2,y*2) 
            self.BoxSceneItems[tag].scaleBox(w*2,h*2)
        else:
            self.BoxSceneItems[tag] = MocapBox(w*2,h*2)
            self.BoxSceneItems[tag].setPos(x*2,y*2)
            self.BoxSceneItems[tag].scaleBox(w*2,h*2)
            self.scene.addItem(self.BoxSceneItems[tag])       
        
        if self.boxesLastFrame.has_key(tag):
            self.boxesLastFrame.pop(tag, None) 
            
    def updateFrame(self):
        
        for tag,mbox in self.boxesLastFrame.items():
            mbox.hide()

        for  tag,mbox in self.BoxSceneItems.items():
            self.boxesLastFrame[tag] = mbox 

        self.fpsDisplay.display(fpsclock.speed()) 
        
    def openServer(self):
        self.thread.render()
        
    def closeEvent(self, event):
        # do stuff
        print "cleanup"
        self.thread.stopRecording()
        self.thread.exiting = True

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())   