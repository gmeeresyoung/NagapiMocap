'''
Created on 11 Nov 2015

@author: gregmeeresyoung
'''
from PyQt4 import QtCore
from PyQt4 import QtGui 
from MocapClientDialog_ui import Ui_Dialog

import sys

class ClientDiolog(QtGui.QDialog, Ui_Dialog ):
    
    
    def __init__(self, parent=None):
        
        super(ClientDiolog,self).__init__(parent)
        super(ClientDiolog,self).setupUi(self)    