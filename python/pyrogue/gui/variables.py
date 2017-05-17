#!/usr/bin/env python
#-----------------------------------------------------------------------------
# Title      : Variable display for rogue GUI
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

#import parse
import pyrogue


class VariableLink(QObject):
    """Bridge between the pyrogue tree and the display element"""

    def __init__(self,parent,variable):
        QObject.__init__(self)
        self.variable = variable
        self.block = False

        item = QTreeWidgetItem(parent)
        parent.addChild(item)
        item.setText(0,variable.name)
        item.setText(1,variable.mode)
        item.setText(2,variable.typeStr) # Fix this. Should show base and size

        if variable.units:
           item.setText(4,str(variable.units))

        if variable.disp == 'enum' and variable.enum is not None and variable.mode=='RW':
            #print('VariableLink: variable: {} , enum: {}'.format(variable, variable.enum))
            self.widget = QComboBox()
            self.widget.activated.connect(self.guiChanged)
            self.connect(self,SIGNAL('updateGui'),self.widget.setCurrentIndex)

            for i in variable.enum:
                self.widget.addItem(variable.enum[i])

        elif variable.disp == 'range':
            self.widget = QSpinBox();
            self.widget.setMinimum(variable.minimum)
            self.widget.setMaximum(variable.maximum)
            self.widget.valueChanged.connect(self.guiChanged)
            self.connect(self,SIGNAL('updateGui'),self.widget.setValue)

        else:
            self.widget = QLineEdit()
            self.widget.returnPressed.connect(self.returnPressed)
            self.connect(self,SIGNAL('updateGui'),self.widget.setText)

        if variable.mode == 'RO':
            self.widget.setReadOnly(True)

        item.treeWidget().setItemWidget(item,3,self.widget)
        variable.addListener(self.newValue)
        
        if isinstance(self.widget, QComboBox):
            self.newValue(None,self.widget.findText(variable.getDisp(read=False)))
        else:
            self.newValue(None,variable.getDisp(read=False))
            
    def newValue(self, var, value):
        #print('{} newValue ( {} {} )'.format(self.variable, type(value), value))
        if self.block: return
        self.emit(SIGNAL("updateGui"), value)

    def returnPressed(self):
        self.guiChanged(self.widget.text())

    def guiChanged(self, value):
        #print('{} guiChanged( {}({}) )'.format(self.variable, type(value), value))
        self.block = True

        if self.variable.disp == 'enum':
            # For enums, value will be index of selected item
            # Need to call itemText to convert to string
            self.variable.setDisp(self.widget.itemText(value))

        else:
            # For non enums, value will be string entered in box
            self.variable.setDisp(value)

        self.block = False


class VariableWidget(QWidget):
    def __init__(self, group, parent=None):
        super(VariableWidget, self).__init__(parent)

        self.roots = []

        vb = QVBoxLayout()
        self.setLayout(vb)
        self.tree = QTreeWidget()
        vb.addWidget(self.tree)

        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(['Variable','Mode','Base','Value','Units'])

        self.top = QTreeWidgetItem(self.tree)
        self.top.setText(0,group)
        self.tree.addTopLevelItem(self.top)
        self.top.setExpanded(True)

        hb = QHBoxLayout()
        vb.addLayout(hb)

        pb = QPushButton('Read')
        pb.pressed.connect(self.readPressed)
        hb.addWidget(pb)

    def addTree(self,root):
        self.roots.append(root)

        r = QTreeWidgetItem(self.top)
        r.setText(0,root.name)
        r.setExpanded(True)
        self.addTreeItems(r,root)

        for i in range(0,4):
            self.tree.resizeColumnToContents(i)

    def readPressed(self):
        for root in self.roots:
            root.readAll()

    def addTreeItems(self,tree,d):

        # First create variables
        #for key,val in d.variables.iteritems():
        for key,val in d.variables.items():
            if not val.hidden and val.mode != 'CMD':
                var = VariableLink(tree,val)

        # Then create devices
        #for key,val in d.devices.iteritems():
        for key,val in d.devices.items():
            if not val.hidden:
                w = QTreeWidgetItem(tree)
                w.setText(0,val.name)
                w.setExpanded(val.expand)
                self.addTreeItems(w,val)

