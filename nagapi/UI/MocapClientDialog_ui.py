# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\gregmeeresyoung\git\NagapiMocap\nagapi\designer\MocapClientDialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName(_fromUtf8("Dialog"))
        Dialog.resize(406, 226)
        self.verticalLayout_3 = QtGui.QVBoxLayout(Dialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.radioButton_local = QtGui.QRadioButton(Dialog)
        self.radioButton_local.setChecked(True)
        self.radioButton_local.setObjectName(_fromUtf8("radioButton_local"))
        self.horizontalLayout_2.addWidget(self.radioButton_local)
        self.radioButton_usbCam = QtGui.QRadioButton(Dialog)
        self.radioButton_usbCam.setObjectName(_fromUtf8("radioButton_usbCam"))
        self.horizontalLayout_2.addWidget(self.radioButton_usbCam)
        self.radioButton_remote = QtGui.QRadioButton(Dialog)
        self.radioButton_remote.setObjectName(_fromUtf8("radioButton_remote"))
        self.horizontalLayout_2.addWidget(self.radioButton_remote)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.groupBox = QtGui.QGroupBox(Dialog)
        self.groupBox.setEnabled(False)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.comboBox_mocapIP = QtGui.QComboBox(self.groupBox)
        self.comboBox_mocapIP.setEditable(True)
        self.comboBox_mocapIP.setObjectName(_fromUtf8("comboBox_mocapIP"))
        self.comboBox_mocapIP.addItem(_fromUtf8(""))
        self.comboBox_mocapIP.addItem(_fromUtf8(""))
        self.comboBox_mocapIP.addItem(_fromUtf8(""))
        self.verticalLayout.addWidget(self.comboBox_mocapIP)
        self.verticalLayout_3.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(Dialog)
        self.groupBox_2.setCheckable(True)
        self.groupBox_2.setChecked(False)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.comboBox_pluginIP = QtGui.QComboBox(self.groupBox_2)
        self.comboBox_pluginIP.setEditable(True)
        self.comboBox_pluginIP.setObjectName(_fromUtf8("comboBox_pluginIP"))
        self.comboBox_pluginIP.addItem(_fromUtf8(""))
        self.comboBox_pluginIP.setItemText(0, _fromUtf8(""))
        self.comboBox_pluginIP.addItem(_fromUtf8(""))
        self.verticalLayout_2.addWidget(self.comboBox_pluginIP)
        self.verticalLayout_3.addWidget(self.groupBox_2)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.label = QtGui.QLabel(Dialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout.addWidget(self.label)
        self.comboBox_lisenPort = QtGui.QComboBox(Dialog)
        self.comboBox_lisenPort.setInputMethodHints(QtCore.Qt.ImhDigitsOnly)
        self.comboBox_lisenPort.setObjectName(_fromUtf8("comboBox_lisenPort"))
        self.comboBox_lisenPort.addItem(_fromUtf8(""))
        self.horizontalLayout.addWidget(self.comboBox_lisenPort)
        self.verticalLayout_3.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout_3.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), Dialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), Dialog.reject)
        QtCore.QObject.connect(self.radioButton_remote, QtCore.SIGNAL(_fromUtf8("toggled(bool)")), self.groupBox.setEnabled)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(_translate("Dialog", "Dialog", None))
        self.radioButton_local.setText(_translate("Dialog", "local File", None))
        self.radioButton_usbCam.setText(_translate("Dialog", "USB Camera", None))
        self.radioButton_remote.setText(_translate("Dialog", "Remote Client", None))
        self.groupBox.setTitle(_translate("Dialog", "Motion capture client IP", None))
        self.comboBox_mocapIP.setItemText(0, _translate("Dialog", "localHost", None))
        self.comboBox_mocapIP.setItemText(1, _translate("Dialog", "192.168.0.17", None))
        self.comboBox_mocapIP.setItemText(2, _translate("Dialog", "192.168.0.16", None))
        self.groupBox_2.setTitle(_translate("Dialog", "PlugIn client IP", None))
        self.comboBox_pluginIP.setItemText(1, _translate("Dialog", "192.168.0.10", None))
        self.label.setText(_translate("Dialog", "Lisen port", None))
        self.comboBox_lisenPort.setItemText(0, _translate("Dialog", "10000", None))

