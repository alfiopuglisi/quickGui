'''
A simple GUI which evaluates Python expressions
and displays the result.
Communication with the background task is asynchronous
thanks to a QueueListener that sends custom signals

'''

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QGridLayout, QLineEdit

from dispatching_gui import DispatchingGui, cmd


class ExampleDispatch(DispatchingGui):

   def __init__(self, qin, qout):
       super().__init__(qin, qout)

       app = QApplication(sys.argv)

       window = QWidget()
       layout = QGridLayout()

       self.cmd = QLineEdit()
       layout.addWidget(QLabel('Cmd'), 0, 0)
       layout.addWidget(self.cmd, 0, 1)

       button = QPushButton("Execute")
       layout.addWidget(button, 1, 0)

       layout.addWidget(QLabel('Result'), 2, 0)

       self.result = QLabel()
       layout.addWidget(self.result, 2, 1)
       window.setLayout(layout)

       button.clicked.connect(self.on_click)
       self.cmd.returnPressed.connect(self.on_click)

       window.show()
       app.exec_()

   # Async action / response

   def on_click(self):
       self.send(self.cmd.text())

   @cmd('RESULT')
   def on_result(self, data):
       self.result.setText(str(data))

