# -*- coding: utf-8 -*-

'''
A simple GUI which evaluates Python expressions
and displays the result.
Communication with the background task is asynchronous
thanks to a QueueListener that sends custom signals

'''

import sys
import time
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtWidgets import QPushButton, QPlainTextEdit
from PyQt5.QtWidgets import QLineEdit, QHBoxLayout, QVBoxLayout

from quickgui.framework.dispatching_gui import DispatchingQtGui, handler


class MotorGui(DispatchingQtGui):

    def __init__(self, qin, qout):
        super().__init__(qin, qout)

        app = QApplication(sys.argv)

        window = QWidget()

        simlabel = QLabel("Simulation:")
        sim_on = QPushButton("On")
        sim_off = QPushButton("Off")
        self.sim_status = QLabel("status")
        row1 = QHBoxLayout()
        row1.addWidget(simlabel)
        row1.addWidget(sim_on)
        row1.addWidget(sim_off)
        row1.addWidget(self.sim_status)

        poslabel = QLabel("Position:")
        self.curpos = QLabel("curpos")
        self.curstatus = QLabel("status")
        row2 = QHBoxLayout()
        row2.addWidget(poslabel)
        row2.addWidget(self.curpos)
        row2.addWidget(self.curstatus)

        movelabel = QLabel("Move to:")
        self.moveedit = QLineEdit('')
        movebutton = QPushButton("Move")
        row3 = QHBoxLayout()
        row3.addWidget(movelabel)
        row3.addWidget(self.moveedit)
        row3.addWidget(movebutton)

        rows = QVBoxLayout()
        rows.addLayout(row1)
        rows.addLayout(row2)
        rows.addLayout(row3)

        self.logwindow = QPlainTextEdit()
        self.logwindow.setReadOnly(True)
        self.logwindow.setMaximumSize(1000, 100)
        rows.addWidget(self.logwindow)
        window.setLayout(rows)

        movebutton.clicked.connect(self.on_button_move)
        self.moveedit.returnPressed.connect(self.on_button_move)

        sim_on.clicked.connect(self.on_button_sim_on)
        sim_off.clicked.connect(self.on_button_sim_off)

        window.show()
        app.exec_()

    def log(self, line):
        t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        self.logwindow.appendPlainText('%s %s' % (t, line))
        self.logwindow.verticalScrollBar().setValue(
                            self.logwindow.verticalScrollBar().maximum())

    def on_button_move(self):
        self.send('MOVE ' + self.moveedit.text())

    def on_button_sim_on(self):
        self.send('SIMUL 1')

    def on_button_sim_off(self):
        self.send('SIMUL 0')

    @handler('MOVE')
    def log_move(self, data):
        if data == 'OK':
            self.log('MOVE command completed')
        else:
            self.log('MOVE command failed: ' + data)

    @handler('SIMUL')
    def log_simul(self, data):
        if data == 'OK':
            self.log('SIMUL command completed')
        else:
            self.log('SIMUL command failed: ' + data)

    @handler('MOVING')
    def refresh_status(self, data):
        if int(data):
            moving = "MOVING"
        else:
            moving = "IDLE"
        self.curstatus.setText(moving)

    @handler('POS')
    def refresh_pos(self, data):
        self.curpos.setText(data)

    @handler('SIMULATED')
    def refresh_simul(self, data):
        if int(data):
            simul = 'On'
        else:
            simul = 'Off'
        self.sim_status.setText(simul)
