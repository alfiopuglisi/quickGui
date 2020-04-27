'''
Text based UI
'''

import sys
import threading

def read_input(qout):
    while True:
       qout.put(sys.stdin.readline())


def ui(qin, qout):

    t = threading.Thread(target=read_input, args=(qout,))
    t.start()

    while True:
       print(qin.get())


