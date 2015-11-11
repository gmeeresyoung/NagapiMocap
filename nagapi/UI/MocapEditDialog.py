'''
Created on 5 Oct 2015

@author: gregmeeresyoung
'''
from PyQt4 import QtCore
from PyQt4 import QtGui 
from MocapEditDialog_ui import Ui_Dialog

import sys

class EditDiolog(QtGui.QDialog, Ui_Dialog ):
    
    def __init__(self, parent=None):
        
        super(EditDiolog,self).__init__(parent)
        super(EditDiolog,self).setupUi(self)
        
        self.data = dict(name='',
                         tag=0,
                                filter=dict(xChannel = dict(output=True,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150),
                                            yChannel = dict(output=True,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150),
                                            wChannel = dict(output=False,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150),
                                            hChannel = dict(output=False,
                                                            noFilter=True,
                                                            lowPassFilter=False,
                                                            gasianAv=False,
                                                            freq=0.03,
                                                            filterbufferSize = 150),
                                            ),
                    smartClasificaion =  dict(smartClasification=False,
                                              boxSize=40),
                    custemRege = dict(custemRegen=True,
                                      colourID=0,
                                      width=15,
                                      height=15,
                                      topLeftX=0,
                                      topLeftY=0,
                                      bottomRightX=0,
                                      bottomRightY=0),
                    output = dict(x=True,
                                  y=True,
                                  w=False,
                                  h=False))
            
        self.getData()
        
    
    def getData(self):
        self.data['name'] = str(self.lineEdit_name.text())
        self.data['tag'] = self.spinBox_tag.value()
        
        self.data['smartClasificaion']['smartClasification'] = self.groupBox_SmartClas.isChecked()
        self.data['smartClasificaion']['boxSize'] = self.spinBox_smartBoxSize.value()
        
        self.data['custemRege']['custemRegen'] = self.groupBox_CustemR.isChecked()
        self.data['custemRege']['colourID'] = self.spinBox_colID.value()
        self.data['custemRege']['width'] = self.spinBox_width.value()
        self.data['custemRege']['height'] = self.spinBox_height.value()
        
        self.data['filter']['xChannel']['output'] = self.groupBox_x.isChecked()
        self.data['filter']['xChannel']['noFilter'] = self.radioButton_noF_x.isChecked()
        self.data['filter']['xChannel']['lowPassFilter'] = self.radioButton_lowPassF_x.isChecked()
        self.data['filter']['xChannel']['gasianAv'] = self.radioButton_gAve_x.isChecked()
        self.data['filter']['xChannel']['freq'] = self.doubleSpinBox_feq_x.value()
        self.data['filter']['xChannel']['filterbufferSize'] = self.spinBox_filterBuffSize_x.value()
        
        self.data['filter']['yChannel']['output'] = self.groupBox_y.isChecked()
        self.data['filter']['yChannel']['noFilter'] = self.radioButton_noF_y.isChecked()
        self.data['filter']['yChannel']['lowPassFilter'] = self.radioButton_lowPassF_y.isChecked()
        self.data['filter']['yChannel']['gasianAv'] = self.radioButton_gAve_y.isChecked()
        self.data['filter']['yChannel']['freq'] = self.doubleSpinBox_feq_y.value()
        self.data['filter']['yChannel']['filterbufferSize'] = self.spinBox_filterBuffSize_y.value()
                
        self.data['filter']['wChannel']['output'] = self.groupBox_w.isChecked()
        self.data['filter']['wChannel']['noFilter'] = self.radioButton_noF_w.isChecked()
        self.data['filter']['wChannel']['lowPassFilter'] = self.radioButton_lowPassF_w.isChecked()
        self.data['filter']['wChannel']['gasianAv'] = self.radioButton_gAve_w.isChecked()
        self.data['filter']['wChannel']['freq'] = self.doubleSpinBox_feq_w.value()
        self.data['filter']['wChannel']['filterbufferSize'] = self.spinBox_filterBuffSize_w.value()
        
        self.data['filter']['hChannel']['output'] = self.groupBox_h.isChecked()
        self.data['filter']['hChannel']['noFilter'] = self.radioButton_noF_h.isChecked()
        self.data['filter']['hChannel']['lowPassFilter'] = self.radioButton_lowPassF_h.isChecked()
        self.data['filter']['hChannel']['gasianAv'] = self.radioButton_gAve_h.isChecked()
        self.data['filter']['hChannel']['freq'] = self.doubleSpinBox_feq_h.value()
        self.data['filter']['hChannel']['filterbufferSize'] = self.spinBox_filterBuffSize_h.value()
        
        return self.data

    def updatData(self,data):
        self.lineEdit_name.setText(data['name'])
        self.spinBox_tag.setValue(data['tag'])
        
        self.groupBox_SmartClas.setChecked(data['smartClasificaion']['smartClasification'])
        self.spinBox_smartBoxSize.setValue(data['smartClasificaion']['boxSize'])
        
        self.groupBox_CustemR.setChecked(data['custemRege']['custemRegen'])
        self.spinBox_colID.setValue(data['custemRege']['colourID'])
        self.spinBox_width.setValue(data['custemRege']['width'])
        self.spinBox_height.setValue(data['custemRege']['height'])
        
        self.groupBox_x.setChecked(data['filter']['xChannel']['output'])
        self.radioButton_noF_x.setChecked(data['filter']['xChannel']['noFilter'])
        self.radioButton_lowPassF_x.setChecked(data['filter']['xChannel']['lowPassFilter'])
        self.radioButton_gAve_x.setChecked(data['filter']['xChannel']['gasianAv'])
        self.doubleSpinBox_feq_x.setValue(data['filter']['xChannel']['freq'])
        self.spinBox_filterBuffSize_x.setValue(data['filter']['xChannel']['filterbufferSize'])

        self.groupBox_y.setChecked(data['filter']['yChannel']['output'])
        self.radioButton_noF_y.setChecked(data['filter']['yChannel']['noFilter'])
        self.radioButton_lowPassF_y.setChecked(data['filter']['yChannel']['lowPassFilter'])
        self.radioButton_gAve_y.setChecked(data['filter']['yChannel']['gasianAv'])
        self.doubleSpinBox_feq_y.setValue(data['filter']['yChannel']['freq'])
        self.spinBox_filterBuffSize_y.setValue(data['filter']['yChannel']['filterbufferSize'])

        self.groupBox_w.setChecked(data['filter']['wChannel']['output'])
        self.radioButton_noF_w.setChecked(data['filter']['wChannel']['noFilter'])
        self.radioButton_lowPassF_w.setChecked(data['filter']['wChannel']['lowPassFilter'])
        self.radioButton_gAve_w.setChecked(data['filter']['wChannel']['gasianAv'])
        self.doubleSpinBox_feq_w.setValue(data['filter']['wChannel']['freq'])
        self.spinBox_filterBuffSize_w.setValue(data['filter']['wChannel']['filterbufferSize'])
        
        self.groupBox_h.setChecked(data['filter']['hChannel']['output'])
        self.radioButton_noF_h.setChecked(data['filter']['hChannel']['noFilter'])
        self.radioButton_lowPassF_h.setChecked(data['filter']['hChannel']['lowPassFilter'])
        self.radioButton_gAve_h.setChecked(data['filter']['hChannel']['gasianAv'])       
        self.doubleSpinBox_feq_h.setValue(data['filter']['hChannel']['freq'])
        self.spinBox_filterBuffSize_h.setValue(data['filter']['hChannel']['filterbufferSize'])
                 
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    dialog = EditDiolog()
    sys.exit(dialog.exec_())
