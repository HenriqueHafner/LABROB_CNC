# -*- coding: utf-8 -*-
"""
Created on Fri Nov  4 16:48:52 2022

@author: robotlab
"""

from serial import *

serial_read_tester = [b'G00 X1\nG00 X10\nG00 X10\nG00 X',
                      b'50 Y10\n G00 X0 Y0',
                      b'\n']
read_index = 0

def write(*wargs,**kwargs):
    return True

def read(*wargs,**kwargs):
    global read_index
    bytes_to_write = serial_read_tester[read_index]
    read_index += 1
    if not read_index < len(serial_read_tester):
        read_index = 0
    return bytes_to_write

def inWaiting(*wargs,**kwargs):
    return len(serial_read_tester[read_index])
