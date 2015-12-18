'''
Created on 7 Oct 2015

@author: gregmeeresyoung
'''
import sys,os,re
import socket
import select
import Queue
from collections import deque
import ctypes
import struct
import time
from pprint import pprint
from PyQt4.QtCore import QThread,SIGNAL,QFile
from PyQt4.QtGui import QMessageBox,QFileDialog

from MocapFilters import CircularBuffer
from MocapUtils import *
import MocapClasify

import ctypes
from ctypes import c_uint,Structure
import struct

from nagapi import FpsClock
###
# Initalize fps clock
fpsclock = FpsClock(10)

class Blocks (Structure):
    _fields_ = [ ("type", c_uint),
                 ("signature", c_uint),
                 ("x", c_uint),
                 ("y", c_uint),
                 ("width", c_uint),
                 ("height", c_uint),
                 ("angle", c_uint) ]
  
  
class MocapTread( QThread ):
    nofilter,lowPassFilter,gouseanFilter = range(0,3)
    
    def __init__(self, parent = None):
        QThread.__init__(self, parent)
        
        self.exiting = False
        self.commandFromServer=None
        # Give the connection a queue for data we want to send/ reseve
        self.data_queues = dict()
        self.receve_queues = dict()
        self.clientCommands = dict()
        
        # set up data streem for commands 
        self.packer_cmd = struct.Struct('4s')#struct.Struct('I')
        self.cmdBuffer = ctypes.create_string_buffer(self.packer_cmd.size)
        self.amount_expected_cmd = self.packer_cmd.size
        # setup data streem for mocp data
        self.filterBufferSize = 100
        self.maxPoints = MAX_NUM_POINTS
        self.pointDataSize = POINT_DATA_SIZE        
        self.packer_data = struct.Struct(self.buildPacker(self.maxPoints,self.pointDataSize))
        self.sendDataBuffer = ctypes.create_string_buffer(self.packer_data.size)
        self.amount_expected_mocap = self.packer_data.size
        
        self._clasfyRegens = None
        self.setClasifydata = False
        
        self.smartFilterBoxSize = 40
        self.filterDataFlag = False
        self.frameDataBuffer = self.buildFrameData(self.maxPoints,self.pointDataSize) 
        
        self.filterBuffers = {rbID:dict(x=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                            filterType=Server.lowPassFilter,
                                            lowPassFreq = .15),
                                        y=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .15),
                                        w=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .15),
                                        h=dict(buffer=CircularBuffer(size=self.filterBufferSize),
                                             filterType=Server.lowPassFilter,
                                             lowPassFreq = .15),
                                        activeChannels=dict(x=True,
                                                          y=True,
                                                          w=False,
                                                          h=False)) for rbID in xrange(0,self.maxPoints+1)}
        
        # file recording
        self.openRecording = False
    
    def buildFromData(self,data):
        
        tag = data['tag']
        channel = 'x'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'y'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'w'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['%sChannel'%channel]['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['%sChannel'%channel]['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        channel = 'h'
        self.updateOutputChannel(tag,channel, data['filter']['%sChannel'%channel]['output'] )
        newSize = data['filter']['%sChannel'%channel]['filterbufferSize']
        self.updateBufferSize(tag,channel,newSize)

        newFreq = data['filter']['%sChannel'%channel]['freq']
        self.updateLowPassFreq(tag,channel,newFreq)
        
        if data['filter']['xChannel']['noFilter']:
            filterType = Server.nofilter
        elif data['filter']['xChannel']['lowPassFilter']:
            filterType = Server.lowPassFilter
        else:
            filterType = Server.nofilter
        self.updateFilterType(tag,channel,filterType)
        
        smartBoxSize = data['smartClasificaion']['boxSize']
        self.updateSmartBox(smartBoxSize)
    
    def buildPacker(self,numOfpoints,pointLength):
        frameData = ""
        pointData = "f"#'I I I I I'
        for i in xrange(1,pointLength):
            pointData  = pointData + " f"
             
        for i in xrange(0,numOfpoints):
            frameData = frameData +" "+ pointData
    
        return frameData
    
    def buildFrameData(self,numOfpoints,pointDataSize):
        frameData = []
        for pindex in xrange(0,numOfpoints):
            for dindex in xrange(0,pointDataSize):
                frameData.append(MOCAP_ROGE_DATA)
        return frameData

    def updateSmartBox(self, smartBoxSize):
        self.smartFilterBoxSize = smartBoxSize
    
    def updateBufferSize(self,tag,channel,newSize):
        #print tag,channel,newSize,self.filterBuffers[tag][channel]['buffer'] 
        self.filterBuffers[tag][channel]['buffer'] = CircularBuffer(size=newSize)
    
    def updateFilterType(self,tag,channel,filterType):
        #print tag,channel,filterType,self.filterBuffers[tag][channel]['filterType'] 
        self.filterBuffers[tag][channel]['filterType'] = filterType

    def updateLowPassFreq(self,tag,channel,newFreq):
        #print tag,channel,newFreq,self.filterBuffers[tag][channel]['lowPassFreq']
        self.filterBuffers[tag][channel]['lowPassFreq'] = newFreq
        self.filterBuffers[tag][channel]['buffer'].updateFilterFrequecy(newFreq)

    def updateOutputChannel(self,tag,channel,on):
        #print tag,channel,on,self.filterBuffers[tag]['activeChannels'][channel] 
        self.filterBuffers[tag]['activeChannels'][channel] = on
       
    def clasifyData(self,data):
        print "clasifyData"
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        #self._clasfyRegens = MocapClasify.ClasifyRadiusNeighbors(data,self.maxPoints,self.smartFilterBoxSize)#
        #self._clasfyRegens = MocapClasify.Clasify(data,self.maxPoints,self.smartFilterBoxSize)
        self._clasfyRegens = MocapClasify.ClasifyMinDist(data,self.maxPoints,self.smartFilterBoxSize)
        self.setClasifydata = True
        self.filterDataFlag = False 
           
    def rawData(self):
        print "raw data"
        self.commandFromServer = MOCAP_RAW_DATA
        # not point filtering unclasifyed data
        self.setClasifydata = False
        self.filterDataFlag = False
    
    def filterData(self):
        print "filter data"
        #data needs to be clasifyed to filter
        self.commandFromServer = MOCAP_CLASSIFY_DATA
        self.setClasifydata = True
        self.filterDataFlag = True
    
    def filterOff(self):
        self.filterDataFlag = False        
       
    def startRecording(self,curRecordFile):
        self.openRecording = open(curRecordFile, "w")
    
    def stopRecording(self):
        if self.openRecording:
            self.openRecording.close()
            self.openRecording = None

    def applyFiltering(self,tag,x,y,w,h):
        
        if self.filterBuffers[tag]['activeChannels']['x']:
            
            self.filterBuffers[tag]['x']['buffer'].append(x)
            
            if self.filterBuffers[tag]['x']['filterType'] ==  Server.lowPassFilter:
                x = self.filterBuffers[tag]['x']['buffer'].filterButterworth()  
            elif self.filterBuffers[tag]['x']['filterType'] ==  Server.gouseanFilter:
                x = self.filterBuffers[tag]['x']['buffer'].filterGauss() 
            else:
                # no filter
                pass

        if self.filterBuffers[tag]['activeChannels']['y']:
            self.filterBuffers[tag]['y']['buffer'].append(y)
            if self.filterBuffers[tag]['y']['filterType'] ==  Server.lowPassFilter:
                y = self.filterBuffers[tag]['y']['buffer'].filterButterworth()  
            elif self.filterBuffers[tag]['y']['filterType'] ==  Server.gouseanFilter:
                y = self.filterBuffers[tag]['y']['buffer'].filterGauss() 
            else:
                # no filter
                pass
            
        if self.filterBuffers[tag]['activeChannels']['w']:
            self.filterBuffers[tag]['w']['buffer'].append(w)
            if self.filterBuffers[tag]['w']['filterType'] ==  Server.lowPassFilter:
                w = self.filterBuffers[tag]['w']['buffer'].filterButterworth()  
            
            elif self.filterBuffers[tag]['w']['filterType'] ==  Server.gouseanFilter:
                w = self.filterBuffers[tag]['w']['buffer'].filterGauss()                                        
            else:
                # no filter
                pass
            
        if self.filterBuffers[tag]['activeChannels']['h']:
            self.filterBuffers[tag]['h']['buffer'].append(h)
            if self.filterBuffers[tag]['h']['filterType'] ==  Server.lowPassFilter:
                h = self.filterBuffers[tag]['h']['buffer'].filterButterworth()  
            elif self.filterBuffers[tag]['h']['filterType'] ==  Server.gouseanFilter:
                h = self.filterBuffers[tag]['h']['buffer'].filterGauss()                                             
            else:
                # no filter
                pass
            
        return (x,y,w,h)

class LocalPixey( MocapTread ):
    
    def __init__(self, parent = None):
        
        MocapTread.__init__(self, parent)
        self.exiting = False
        self.blocks = None
        
    def __del__(self):
        print "deleting thred"
        self.exiting = True
        self.wait()         
    
    def render(self,lisenPort,mocapClientIP,pluginClientIP):
        
        from pixy import BlockArray,pixy_init
        if self._serverThred:
            self._serverThred.render(lisenPort,mocapClientIP,pluginClientIP)
                  
        ###
        # Initialize Pixy Interpreter thread #
        pixy_init()
        self.blocks = BlockArray(100)
        self.start()

    def closeThred(self):
        if self._serverThred:
            self._serverThred.closeThred()
        self.exiting = True            
        #self.exit()
        self.wait()
          
    def run(self):
        from pixy import pixy_get_blocks
        maxPoints = MAX_NUM_POINTS
        pointDataSize = POINT_DATA_SIZE
        CMD_PASS = 1001
        CMD_NEW_FRAME = 1002
        frame = 0
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        while not self.exiting:
            numOfPointForFrame = pixy_get_blocks(100, self.blocks)
            frame = frame + 1
            if numOfPointForFrame > 0:
                numOfPointForFrame = numOfPointForFrame if numOfPointForFrame < maxPoints else maxPoints
                for index in xrange (0, numOfPointForFrame):
                    
                    dataIndexOffset = 0
                    if index != 0:
                        dataIndexOffset = index * pointDataSize
                        
                    # command to identify all point for frame have bee sent 
                    cmd = CMD_PASS if index < ( numOfPointForFrame -1 ) else CMD_NEW_FRAME
                    tag = int(index)#blocks[index].signature
                    coltag = int(self.blocks[index].signature)
                    
                    # flip for ui
                    y = self.blocks[index].x
                    x = self.blocks[index].y
                    h = self.blocks[index].width
                    w = self.blocks[index].height            

                    if self.setClasifydata:
                        # setup nural pos tages done once to enable consistant traking
                        # of named points , once done smart clasification is used
                        '''
                        self._clasfyRegens.regenClasify(tag,coltag,x,y, w,h,dataIndexOffset)
                    
                        '''
                        tag = self._clasfyRegens.regenClasify(tag,coltag,x,y)
                     
                    if int(tag) != MOCAP_ROGE_DATA:
                        
                        if self.filterDataFlag:
                            x,y,w,h = self.applyFiltering(tag, x, y, w, h)
                        ##
                        # emit point data to update the UI draw  
                        #
                        self.emit(SIGNAL("subFrame(int, long, long, long, long)"),
                                  tag, x, y,w,h)     
                    
                        self.frameDataBuffer[dataIndexOffset] = tag
                        self.frameDataBuffer[dataIndexOffset+1] = coltag
                        self.frameDataBuffer[dataIndexOffset+2] = x
                        self.frameDataBuffer[dataIndexOffset+3] = y
                        self.frameDataBuffer[dataIndexOffset+4] = w
                        self.frameDataBuffer[dataIndexOffset+5] = h
                    else:
                        self.frameDataBuffer[dataIndexOffset] = 9999
                        self.frameDataBuffer[dataIndexOffset+1] = 9999
                        self.frameDataBuffer[dataIndexOffset+2] = 9999
                        self.frameDataBuffer[dataIndexOffset+3] = 9999
                        self.frameDataBuffer[dataIndexOffset+4] = 9999
                        self.frameDataBuffer[dataIndexOffset+5] = 9999    
                    
                    if  cmd == CMD_NEW_FRAME:
                        break  
                
                if self.setClasifydata:

                    self._clasfyRegens.updateBoxesForNextFrame()

                self.emit(SIGNAL("frameEnd()"))   
                
                if self.openRecording:
                    self.openRecording.write(str(self.frameDataBuffer) + "\n")         

                if self._serverThred:
                    self.packer_data.pack_into(self.sendDataBuffer, 0, *self.frameDataBuffer)
                    for key in self._serverThred.data_queues.keys():
                        self._serverThred.data_queues[key].append(self.sendDataBuffer)                   
                

                fpsclock.sleep()    

    def setServer(self,serverThread):
        self._serverThred = serverThread
                
class LocalClient( MocapTread ):
    
    def __init__(self, rawTempFile,  parent = None):
        MocapTread.__init__(self, parent)
        self.exiting = False
        self.curRecordFile = rawTempFile#'C:\\Users\\gregmeeresyoung\\Desktop\\mocapRecording.tmp'
        self._serverThred = None
        
    def __del__(self):
        print "deleting thred"
        self.exiting = True
        self.wait()         
    
    def render(self,lisenPort,mocapclientIP,pluginClientIP):
        
        if self._serverThred:
            self._serverThred.render(lisenPort,mocapclientIP,pluginClientIP)
                     
        self._tmpfile = QFile(self.curRecordFile)
        
        
        if not self._tmpfile.open(QFile.ReadOnly | QFile.Text):
            QMessageBox.warning(self, "Nagapi Mocap",
                    "Cannot write file %s:\n%s." % (self.curRecordFile, self._tmpfile.errorString()))
        else:
            self.start()

    def closeThred(self):
        if self._serverThred:
            self._serverThred.closeThred()
            
        self._tmpfile.close()
        self.exiting = True            
        #self.exit()
        self.wait()
          
    def run(self):
        maxPoints = MAX_NUM_POINTS
        pointDataSize = POINT_DATA_SIZE
        # Note: This is never called directly. It is called by Qt once the
        # thread environment has been set up.
        while not self.exiting:
            while not self._tmpfile.atEnd() and not self.exiting:
                line = str(self._tmpfile.readLine())
                line = line.replace("[",'')
                line = line.replace("]",'')
                unpacked_data = line.split(', ')
                
                for index in xrange(0,maxPoints):
                    
                    dataIndexOffset = 0
                    if index != 0:
                        dataIndexOffset = index * pointDataSize
    
                    tag = int(unpacked_data[dataIndexOffset])
                    #if tag == MOCAP_ROGE_DATA and index < maxPoints:
                    #    print "balls",index
                    coltag = int(unpacked_data[dataIndexOffset+1])
                    
                    x = long(unpacked_data[dataIndexOffset+2])
                    y = long(unpacked_data[dataIndexOffset+3])
                    w = long(unpacked_data[dataIndexOffset+4])
                    h = long(unpacked_data[dataIndexOffset+5])
                    
                    if self.setClasifydata:
                        # setup nural pos tages done once to enable consistant traking
                        # of named points , once done smart clasification is used
                        
                        tag = self._clasfyRegens.regenClasify(tag,coltag,x,y)

                    if int(tag) != MOCAP_ROGE_DATA:
                        
                        if self.filterDataFlag:
                            x,y,w,h = self.applyFiltering(tag, x, y, w, h)
                        ##
                        # emit point data to update the UI draw  
                        #
                        self.emit(SIGNAL("subFrame(int, long, long, long, long)"),
                                  tag, x, y,w,h)                         
                    
                        self.frameDataBuffer[dataIndexOffset] =     float(tag)
                        self.frameDataBuffer[dataIndexOffset+1] = float(coltag)
                        self.frameDataBuffer[dataIndexOffset+2] = float(x)
                        self.frameDataBuffer[dataIndexOffset+3] = float(y)
                        self.frameDataBuffer[dataIndexOffset+4] =   float( w)
                        self.frameDataBuffer[dataIndexOffset+5] =   float( h)
                        # loop throught maybe points and try and clasify

                    else:
                        self.frameDataBuffer[dataIndexOffset] = 9999
                        self.frameDataBuffer[dataIndexOffset+1] = 9999
                        self.frameDataBuffer[dataIndexOffset+2] = 9999
                        self.frameDataBuffer[dataIndexOffset+3] = 9999
                        self.frameDataBuffer[dataIndexOffset+4] = 9999
                        self.frameDataBuffer[dataIndexOffset+5] = 9999                   
                
                if self.setClasifydata:
                    
                    self._clasfyRegens.updateBoxesForNextFrame()
      
                self.emit(SIGNAL("frameEnd()"))
                
                if self.openRecording:
                    self.openRecording.write(str(self.frameDataBuffer) + "\n")
                
                if self._serverThred:
                    self.frameDataBuffer= self.frameDataBuffer
                    self.packer_data.pack_into(self.sendDataBuffer, 0, *self.frameDataBuffer)
                    for key in self._serverThred.data_queues.keys():
                        self._serverThred.data_queues[key].append(self.sendDataBuffer)  
                
                fpsclock.sleep()   
                
            
            self._tmpfile.seek(0)

    def setServer(self,serverThread):
        self._serverThred = serverThread

class Server(MocapTread):

    nofilter,lowPassFilter,gouseanFilter = range(0,3)
    
    def __init__(self, parent = None):
    
        MocapTread.__init__(self, parent)
        
        self.tcpServer = None 
        
    def render(self,lisenPort,mocapclientIP,pluginClientIP):
        self.exiting = False
        self.tcpServer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpServer.setblocking(0)    
            
        # Bind the socket to the port
        server_address = ('', lisenPort)
        print >>sys.stderr, 'starting up on %s port %s' % server_address
        self.tcpServer.bind(server_address)
        
        # Listen for incoming connections
        self.tcpServer.listen(2)        

        # wait for a connection for give time then close in none found
        self.timeout = 160
        
        # Sockets from which we expect to read
        self.inputs = [ self.tcpServer ]
        
        if mocapclientIP:
            self.mocapSendClientIP = [ mocapclientIP ]
        else:
            self.mocapSendClientIP = [  ]                
        
        # Sockets to which we expect to write
        self.outputs = [ ]
        if pluginClientIP:
            self.readCliantIP = [ pluginClientIP ]
        else:
            self.readCliantIP = [  ]

        self.start()

    def closeMocapClient(self):
        self.commandFromServer = CMD_SERVER_CLOSING
                
    def closeThred(self):
        self.commandFromServer = CMD_SERVER_CLOSING
        self.exiting = True
        if self.tcpServer:
            self.tcpServer.close()              
        #self.exit()
        self.wait()
        self.emit(SIGNAL("stopingServer()"))
    
    def __del__(self):
        print "deleating thred"
        self.exiting = True
        if self.tcpServer:
            self.tcpServer.close()
        self.wait()       
       
    def run(self):
        
        while not self.exiting and self.inputs:
            readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, self.timeout)    
            if not (readable or writable or exceptional) or self.exiting:
                # setting readable to [] is a hack to get the server to close down without an error 
                readable = []
                self.exiting = True
                self.commandFromServer = CMD_SERVER_CLOSING
                print "connection timeout"
            
            # Handle inputs
            for s in readable:        
                if s is self.tcpServer:
                    # A "readable" server socket is ready to accept a connection
                    connection, client_address = s.accept()
                    print >>sys.stderr, 'new connection from', client_address
                    connection.setblocking(0)                
                    # sort cnections for imputs and output servers
                    if client_address[0] in self.readCliantIP or client_address[0] in self.mocapSendClientIP:
                        if client_address[0] in self.readCliantIP:
                            
                            # only alow one plugin connection at the mo
                            # if already output remove befor adding new one
                            #append new input connection 
                            self.outputs.append(connection)
                            # ring buffer might be slow
                            self.data_queues[connection] = deque(maxlen =500)#Queue.Queue(maxsize=1000)#LifoQueue
                            self.clientCommands[connection] = None
                            self.receve_queues[connection] = (Queue.Queue(),self.packer_cmd,self.amount_expected_cmd)
                            self.inputs.append(connection)
                            
                        if client_address[0] in self.mocapSendClientIP: 
                            self.inputs.append(connection)
                            self.outputs.append(connection)
                            self.clientCommands[connection] = None
                            self.receve_queues[connection] = (Queue.Queue(),self.packer_data,self.amount_expected_mocap)
                    else:
                        print connection, client_address
                        raise "dont know this server"
                else: 
                    # Look for the response
                    queue,packer,amount_expected  = self.receve_queues[s]
                    try:
                        amount_received,dataBuffer = queue.get_nowait()
                    except Queue.Empty:
                        amount_received,dataBuffer = (0,"")# get from mesage que
                    
                    try:
                        dataBuffer = dataBuffer + s.recv(amount_expected - amount_received)
                    except Exception, e:
                        print type(e)  # Should give you the exception type
                        exceptional.append(s)
                        continue
                                                 
                    amount_received = len(dataBuffer)
                                
                    if amount_expected == amount_received:
        
                        unpacked_data = packer.unpack_from(dataBuffer, 0)
                        ##
                        # get commads form connected clients, Identify it is a command using data lenth
                        #
                       
                        if amount_expected == self.amount_expected_cmd: 
                            #for key in self.data_queues.keys():
                            self.clientCommands[s] = int(unpacked_data[0])
                        ##
                        # get data from mocap client 
                        #                              
                        elif   amount_expected == self.amount_expected_mocap:
                            
                            ##
                            # look for user input commands from server
                            #
                            if self.commandFromServer:
                                self.clientCommands[s] = self.commandFromServer
                                # reset servercommand
                                self.commandFromServer = None
                            ##
                            # loop throught point on frame
                            #
                             
                            for index in xrange(0,self.maxPoints):
                                
                                dataIndexOffset = 0
                                if index != 0:
                                    dataIndexOffset = index * self.pointDataSize
                                
                                tag = int(unpacked_data[dataIndexOffset])
                                coltag = int(unpacked_data[dataIndexOffset+1])
                                ##
                                #I have fliped the data to work with the UI portrat layout. this need to be controled by the ui 
                                #
                                y = unpacked_data[dataIndexOffset+2]
                                x = unpacked_data[dataIndexOffset+3] 
                                h = unpacked_data[dataIndexOffset+4] 
                                w = unpacked_data[dataIndexOffset+5] 

                                if self.setClasifydata:
                                    # setup nural pos tages done once to enable consistant traking
                                    # of named points , once done smart clasification is used
                                    tag = self._clasfyRegens.regenClasify(tag,coltag,x,y)
                                   
                                
                                # filtering the data
                                if tag != MOCAP_ROGE_DATA:
                                      
                                    if self.filterDataFlag:
                                        x,y,w,h = self.applyFiltering(tag, x, y, w, h)
                                    
                                    ##
                                    # emit point data to updat the UI draw  
                                    #
                                   
                                    self.emit(SIGNAL("subFrame(int, long, long, long, long)"),
                                              tag, x, y,w,h)                                       
                                
                                    self.frameDataBuffer[dataIndexOffset] = tag
                                    self.frameDataBuffer[dataIndexOffset+1] = coltag
                                    self.frameDataBuffer[dataIndexOffset+2] = x
                                    self.frameDataBuffer[dataIndexOffset+3] = y
                                    self.frameDataBuffer[dataIndexOffset+4] = w
                                    self.frameDataBuffer[dataIndexOffset+5] = h
                                else:
                                    self.frameDataBuffer[dataIndexOffset] = 9999
                                    self.frameDataBuffer[dataIndexOffset+1] = 9999
                                    self.frameDataBuffer[dataIndexOffset+2] = 9999
                                    self.frameDataBuffer[dataIndexOffset+3] = 9999
                                    self.frameDataBuffer[dataIndexOffset+4] = 9999
                                    self.frameDataBuffer[dataIndexOffset+5] = 9999                                   
                                    

                            if self.setClasifydata:
                                self._clasfyRegens.updateBoxesForNextFrame()                              
                                   
                            self.emit(SIGNAL("frameEnd()"))                            
                            
                            packer.pack_into(self.sendDataBuffer, 0, *self.frameDataBuffer)
                            
                            if self.openRecording:
                                self.openRecording.write(str(self.frameDataBuffer) + "\n")
                                
                            # put data in que for all cliant servers reding mocap data
                            for key in self.data_queues.keys():
                                
                                self.data_queues[key].append(self.sendDataBuffer)                                        
    
                    else:
                        # set for next pass
                        queue.put((amount_received,dataBuffer))
    
            # Handle outputs
            for s in writable:
                
                if self.clientCommands[s] == CMD_NEW_FRAME:
                    try:
            
                        next_msg = self.data_queues[s][-1]#self.data_queues[s].pop()
                        
                    except IndexError:
                        # No messages waiting so stop checking for writability.
                        print >>sys.stderr, 'output queue for', s.getpeername(), 'is empty'
                    else:
                        
                        s.send(next_msg)
                        self.clientCommands[s] =  None
            
                elif  self.clientCommands[s] == MOCAP_CLASSIFY_DATA:
                    pass

                    print "sending clasify comand to mocap cliant"
                    '''
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_CLASSIFY_DATA) 
                    s.send(self.cmdBuffer)
                    '''
                    self.clientCommands[s] = None
                    
                elif self.clientCommands[s] == MOCAP_RAW_DATA:
                    print "sending raw data comand to cliant"
                    '''
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, MOCAP_RAW_DATA) 
                    s.send(self.cmdBuffer)
                    self.clientCommands[s] = None
                    '''
                elif self.clientCommands[s] == CMD_SERVER_CLOSING:
                    print "sending raw data comand to cliant"
                    ''''
                    self.packer_cmd.pack_into(self.cmdBuffer, 0, CMD_SERVER_CLOSING) 
                    s.send(self.cmdBuffer)
                    self.clientCommands[s] = None
                    '''
                else:
                    # no commands to exicutep
                    self.clientCommands[s] = None            
            
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
        
        #self.closeThred()
        #self.tcpServer.close()                
        #self.exit()
        #self.emit(SIGNAL("stopingServer()"))
     
if __name__ == '__main__':
    pass