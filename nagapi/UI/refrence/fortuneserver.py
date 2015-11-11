#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


import random

from PyQt4 import QtCore, QtGui
import socket
import select
import Queue
from collections import deque
import ctypes
import struct

from nagapi import FpsClock

CMD_NEW_FRAME = 1002 

###
# Initalize fps clock
fpsclock = FpsClock(10)

class MocapBox(QtGui.QGraphicsItem):

    # Create the bounding rectangle once.
    adjust = 0.5
    BoundingRect = QtCore.QRectF(-10, -20, 20, 40)

    def __init__(self):
        super(MocapBox, self).__init__()
        self.color = QtGui.QColor(QtCore.qrand() % 256, QtCore.qrand() % 256,
                        QtCore.qrand() % 256)
    def boundingRect(self):
        return MocapBox.BoundingRect

    def shape(self):
        path = QtGui.QPainterPath()
        path.addRect(-10, -20, 20, 40)
        return path;

    def paint(self, painter, option, widget):
        # Body.
        painter.setBrush(self.color)
        painter.drawRect(-10, -20, 20, 40)
        

class Server(QtGui.QDialog):
    def __init__(self, parent=None):
        super(Server, self).__init__(parent)

        statusLabel = QtGui.QLabel()
        quitButton = QtGui.QPushButton("Quit")
        quitButton.setAutoDefault(False)
        
        self.scene = QtGui.QGraphicsScene()
        self.scene.setSceneRect(640,400,0,0)
        self.scene.setItemIndexMethod(QtGui.QGraphicsScene.NoIndex)
        
        view = QtGui.QGraphicsView(self.scene)
        view.setRenderHint(QtGui.QPainter.Antialiasing)
        view.setBackgroundBrush(QtGui.QBrush(QtGui.QPixmap(':/images/cheese.jpg')))
        view.setCacheMode(QtGui.QGraphicsView.CacheBackground)
        view.setViewportUpdateMode(QtGui.QGraphicsView.BoundingRectViewportUpdate)
        #view.setDragMode(QtGui.QGraphicsView.ScrollHandDrag)
        view.setWindowTitle("Nagapi face Mocap")
        view.resize(640,400)
      
        
        
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
        self.maxPoints = 20
        self.pointDataSize = 5        
        self.packer_data = struct.Struct(self.buildPacker(self.maxPoints))
        self.sendDataBuffer = ctypes.create_string_buffer(self.packer_data.size)
        self.amount_expected_mocap = self.packer_data.size

        
        # In the C++ version of this example, this class is also derived from
        # QObject in order to receive timer events.  PyQt does not support
        # deriving from more than one wrapped class so we just create an
        # explicit timer instead.
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(1000 / 500)
        
        self.BoxSceneItems = dict()
        
        quitButton.clicked.connect(self.close)
        buttonLayout = QtGui.QHBoxLayout()
        buttonLayout.addStretch(1)
        buttonLayout.addWidget(quitButton)
        buttonLayout.addStretch(1)

        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(statusLabel)
        mainLayout.addWidget(view)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

        self.setWindowTitle("Fortune Server")
        self.resize(640,400)

    def timerEvent(self):
        readable, writable, exceptional = select.select(self.inputs, self.outputs, self.inputs, self.timeout)    
        
        if not (readable or writable or exceptional):
            print >>sys.stderr, '  timed out, onting connected within 60 sec'
            QtGui.QMessageBox.critical(self, " Server",
                    "Unable to start the server.")
            self.tcpServer.close()
            self.close()
            return
        
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
                         
                        tagListForFrame = []
                        for index in xrange(0,self.maxPoints):
                            dataIndexOffset = 0
                            if index != 0:
                                dataIndexOffset = index * self.pointDataSize
                            
                            cmd = unpacked_data[dataIndexOffset]
                            tag = unpacked_data[dataIndexOffset+1]
                            x = unpacked_data[dataIndexOffset+2] 
                            y = unpacked_data[dataIndexOffset+3] 
                            frame =unpacked_data[dataIndexOffset+4] 
                            
                            if tag != 9999:
                                if self.BoxSceneItems.has_key(tag):
                                    self.BoxSceneItems[tag].setPos(x,y) 
                                else:
                                    self.BoxSceneItems[tag] = MocapBox()
                                    self.BoxSceneItems[tag].setPos(x,y)
                                    self.scene.addItem(self.BoxSceneItems[tag])
                                    tagListForFrame.append(tag)
                        
                        
                        #packer.pack_into(self.sendDataBuffer, 0, *unpacked_data)
                        #recordingFile.write(str(unpacked_data)+"\n")
                        #for key in self.data_queues.keys():
                        #    self.data_queues[key].append(self.sendDataBuffer) 
                        #fpsclock.printfps()                                         

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
            
            
    def buildPacker(self,numOfpoints,pointData='I I I I I'):
        frameData = ""
        for i in xrange(0,numOfpoints):
            frameData = frameData +" "+ pointData
    
        return frameData
    
    def buildFrameData(self,numOfpoints,pointDataSize):
        frameData = []
        for pindex in xrange(0,numOfpoints):
            for dindex in xrange(0,pointDataSize):
                frameData.append(9999)
        return frameData

          

if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    
    server = Server()
    random.seed(None)
    sys.exit(server.exec_())
    
    
