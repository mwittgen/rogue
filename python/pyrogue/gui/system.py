#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : System display for rogue GUI
#-----------------------------------------------------------------------------
# File       : pyrogue/gui/variables.py
# Author     : Ryan Herbst, rherbst@slac.stanford.edu
# Created    : 2016-10-03
# Last update: 2016-10-03
#-----------------------------------------------------------------------------
# Description:
# Module for functions and classes related to variable display in the rogue GUI
#-----------------------------------------------------------------------------
# This file is part of the rogue software platform. It is subject to 
# the license terms in the LICENSE.txt file found in the top-level directory 
# of this distribution and at: 
#    https://confluence.slac.stanford.edu/display/ppareg/LICENSE.html. 
# No part of the rogue software platform, including this file, may be 
# copied, modified, propagated, or distributed except according to the terms 
# contained in the LICENSE.txt file.
#-----------------------------------------------------------------------------
from PyQt4.QtCore   import *
from PyQt4.QtGui    import *
from PyQt4.QtWebKit import *

import pyrogue

class DataLink(QObject):

    def __init__(self,layout,writer):
        QObject.__init__(self)
        self.writer = writer
        self.block = False

        gb = QGroupBox('Data File Control (%s)' % (writer.name))
        layout.addWidget(gb)

        vb = QVBoxLayout()
        gb.setLayout(vb)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        vb.addLayout(fl)

        self.writer.dataFile._addListener(self)
        self.dataFile = QLineEdit()
        self.dataFile.setText(self.writer.dataFile.get())
        self.dataFile.textEdited.connect(self.dataFileChanged)
        self.connect(self,SIGNAL('updateDataFile'),self.dataFile.setText)

        fl.addRow('Data File:',self.dataFile)

        hb = QHBoxLayout()
        vb.addLayout(hb)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        hb.addLayout(fl)

        self.writer.open._addListener(self)
        self.openState = QComboBox()
        self.openState.addItem('False')
        self.openState.addItem('True')
        self.openState.setCurrentIndex(0)
        self.openState.activated.connect(self.openStateChanged)
        self.connect(self,SIGNAL('updateOpenState'),self.openState.setCurrentIndex)

        fl.addRow('File Open:',self.openState)

        self.writer.bufferSize._addListener(self)
        self.bufferSize = QLineEdit()
        self.bufferSize.setText(str(self.writer.bufferSize.get()))
        self.bufferSize.textEdited.connect(self.bufferSizeChanged)
        self.connect(self,SIGNAL('updateBufferSize'),self.bufferSize.setText)

        fl.addRow('Buffer Size:',self.bufferSize)

        self.writer.fileSize._addListener(self)
        self.totSize = QLineEdit()
        self.totSize.setText(str(self.writer.fileSize.get()))
        self.totSize.setReadOnly(True)
        self.connect(self,SIGNAL('updateTotSize'),self.totSize.setText)

        fl.addRow('Total File Size:',self.totSize)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        hb.addLayout(fl)

        pb1 = QPushButton('Browse')
        pb1.clicked.connect(self._browse)

        pb2 = QPushButton('Auto Name')
        pb2.clicked.connect(self._genName)
        fl.addRow(pb1,pb2)

        self.writer.maxSize._addListener(self)
        self.maxSize = QLineEdit()
        self.maxSize.setText(str(self.writer.maxSize.get()))
        self.maxSize.textEdited.connect(self.maxSizeChanged)
        self.connect(self,SIGNAL('updateMaxSize'),self.maxSize.setText)

        fl.addRow('Max Size:',self.maxSize)

        self.writer.frameCount._addListener(self)
        self.frameCount = QLineEdit()
        self.frameCount.setText(str(self.writer.frameCount.get()))
        self.frameCount.setReadOnly(True)
        self.connect(self,SIGNAL('updateFileSize'),self.frameCount.setText)

        fl.addRow('Frame Count:',self.frameCount)

    def _browse(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter('Data Files (*.dat)')

        if dlg.exec_():
           dataFile = str(dlg.selectedFiles()[0])
           self.writer.dataFile.set(dataFile)
        pass
    
    def _genName(self):
        self.writer.autoName()
        pass

    def newValue(self,var):
        if self.block: return

        if var.name == 'dataFile':
            self.emit(SIGNAL("updateDataFile"),str(var.get()))

        elif var.name == 'open':
            self.emit(SIGNAL("updateOpenState"),self.openState.findText(str(var.get())))

        elif var.name == 'bufferSize':
            self.emit(SIGNAL("updateBufferSize"),str(var.get()))

        elif var.name == 'maxSize':
            self.emit(SIGNAL("updateMaxSize"),str(var.get()))

        elif var.name == 'fileSize':
            self.emit(SIGNAL("updateFileSize"),str(var.get()))

        elif var.name == 'frameCount':
            self.emit(SIGNAL("updateFrameCount"),str(var.get()))

    def dataFileChanged(self,value):
        self.block = True
        self.writer.dataFile.set(str(self.dataFile.text()))
        self.block = False

    def openStateChanged(self,value):
        self.block = True
        self.writer.open.set(self.openState.itemText(value) == 'True')
        self.block = False

    def bufferSizeChanged(self,value):
        self.block = True
        try:
            self.writer.bufferSize.set(int(str(value)))
        except Exception:
            pass
        self.block = False

    def maxSizeChanged(self,value):
        self.block = True
        try:
            self.writer.maxSize.set(int(str(value)))
        except Exception:
            pass
        self.block = False


class ControlLink(QObject):

    def __init__(self,layout,control):
        QObject.__init__(self)
        self.control = control
        self.block = False

        gb = QGroupBox('Run Control (%s)' % (control.name))
        layout.addWidget(gb)

        vb = QVBoxLayout()
        gb.setLayout(vb)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        vb.addLayout(fl)

        self.control.runRate._addListener(self)
        self.runRate = QComboBox()
        self.runRate.activated.connect(self.runRateChanged)
        self.connect(self,SIGNAL('updateRate'),self.runRate.setCurrentIndex)
        for key in sorted(self.control.runRate.enum):
            self.runRate.addItem(self.control.runRate.enum[key])
        self.runRate.setCurrentIndex(self.runRate.findText(str(self.control.runRate.get())))

        fl.addRow('Run Rate:',self.runRate)

        hb = QHBoxLayout()
        vb.addLayout(hb)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        hb.addLayout(fl)

        self.control.runState._addListener(self)
        self.runState = QComboBox()
        self.runState.activated.connect(self.runStateChanged)
        self.connect(self,SIGNAL('updateState'),self.runState.setCurrentIndex)
        for key in sorted(self.control.runState.enum):
            self.runState.addItem(self.control.runState.enum[key])
        self.runState.setCurrentIndex(self.runState.findText(str(self.control.runState.get())))

        fl.addRow('Run State:',self.runState)

        fl = QFormLayout()
        fl.setRowWrapPolicy(QFormLayout.DontWrapRows)
        fl.setFormAlignment(Qt.AlignHCenter | Qt.AlignTop)
        fl.setLabelAlignment(Qt.AlignRight)
        hb.addLayout(fl)

        self.control.runCount._addListener(self)
        self.runCount = QLineEdit()
        self.runCount.setText(str(self.control.runCount.get()))
        self.runCount.setReadOnly(True)
        self.connect(self,SIGNAL('updateCount'),self.runCount.setText)

        fl.addRow('Run Count:',self.runCount)

    def newValue(self,var):
        if self.block: return

        if var.name == 'runState':
            self.emit(SIGNAL("updateState"),self.runState.findText(str(var.get())))

        elif var.name == 'runRate':
            self.emit(SIGNAL("updateRate"),self.runRate.findText(str(var.get())))

        elif var.name == 'runCount':
            self.emit(SIGNAL("updateCount"),str(var.get()))

    def runStateChanged(self,value):
        self.block = True
        self.control.runState.set(str(self.runState.itemText(value)))
        self.block = False

    def runRateChanged(self,value):
        self.block = True
        self.control.runRate.set(str(self.runRate.itemText(value)))
        self.block = False


class SystemWidget(QWidget):
    def __init__(self, root, parent=None):
        super(SystemWidget, self).__init__(parent)

        self.holders = []
        self.root = root

        tl = QVBoxLayout()
        self.setLayout(tl)

        ###################
        # Group Box
        ###################
        gb = QGroupBox('Reset And Configuration')
        tl.addWidget(gb)

        vb = QVBoxLayout()
        gb.setLayout(vb)

        hb = QHBoxLayout()
        vb.addLayout(hb)

        pb = QPushButton('Hard Reset')
        pb.clicked.connect(self.hardReset)
        hb.addWidget(pb)

        pb = QPushButton('Soft Reset')
        pb.clicked.connect(self.softReset)
        hb.addWidget(pb)

        pb = QPushButton('Count Reset')
        pb.clicked.connect(self.countReset)
        hb.addWidget(pb)

        hb = QHBoxLayout()
        vb.addLayout(hb)

        pb = QPushButton('Load Settings')
        pb.clicked.connect(self.loadSettings)
        hb.addWidget(pb)

        pb = QPushButton('Save Settings')
        pb.clicked.connect(self.saveSettings)
        hb.addWidget(pb)

        ###################
        # Data Controllers
        ###################
        for key,val in root._nodes.iteritems():
            if isinstance(val,pyrogue.DataWriter):
                self.holders.append(DataLink(tl,val))

        ###################
        # Run Controllers
        ###################
        for key,val in root._nodes.iteritems():
            if isinstance(val,pyrogue.RunControl):
                self.holders.append(ControlLink(tl,val))

        ###################
        # System Log
        ###################
        gb = QGroupBox('System Log')
        tl.addWidget(gb)

        vb = QVBoxLayout()
        gb.setLayout(vb)

        self.systemLog = QTextEdit()
        self.systemLog.setReadOnly(True)
        vb.addWidget(self.systemLog)

        self.root.systemLog._addListener(self)
        self.connect(self,SIGNAL('updateLog'),self.systemLog.setText)
        
        pb = QPushButton('Clear Log')
        pb.clicked.connect(self.resetLog)
        vb.addWidget(pb)

    def resetLog(self):
        self.root.clearLog()

    def newValue(self,var):
        if var.name == 'systemLog':
            self.emit(SIGNAL("updateLog"),var.get())

    def hardReset(self):
        self.root.hardReset()

    def softReset(self):
        self.root.softReset()

    def countReset(self):
        self.root.countReset()

    def loadSettings(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter('Config Files (*.yml)')

        if dlg.exec_():
           loadFile = str(dlg.selectedFiles()[0])
           self.root.readConfig(loadFile)

    def saveSettings(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter('Config Files (*.yml)')

        if dlg.exec_():
           saveFile = str(dlg.selectedFiles()[0])
           self.root.writeConfig(saveFile)

