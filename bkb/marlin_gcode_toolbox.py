#marlin_gcode_toolbox
# -*- coding: utf-8 -*-
"""
Created on Wed Jun 23 13:36:17 2021

@author: localadmin
"""

from os.path import join,sep
print('test')
gcode_filepath = [join('C:',sep,'GCODE-files'),join('G:',sep)]

function_table = [
['home_xy','G28 X Y\n'],['home_z','G28 Z\n','G0 Z0.2\n'],
['pos_get','M114 \n'],
['endstops_d','M211 S0\n'],['endstops_e','M211 S1\n'],
['calibrate-z','G92 Z0.05','G0 Z0\n','G92 Z0.2\n'],
['calibrate+z','G92 Z-0.05','G0 Z0\n','G92 Z0.2\n'],
['move1_-z','G91\n','G0 Z-1','G90\n'],
['move1_+z','G91\n','G0 Z1','G90\n'],
['move_orign','G0 X0 Y0\n','G1 Z0\n'],
['move+e','G91\n','G1 E1','G90\n'],
['move_c0','G0 X10 Y30 Z10\n','G0 X85 Y70\n','G0 Z0.1\n'],
['move_c1','G0 X10 Y30\n'],
['move_c2','G0 X85 Y160\n'],
['move_c3','G0 X160 Y30\n'],
['stepper_d','M84\n'],['stats','M105\n'],
['warm_n','M104 S235\n'],['warm_b','M140 S90\n'],
['cool_n','M104 S0\n'],['cool_b','M140 S0\n'],
['wait','M400'],
['fan_on','M106 S255'],
['fan_off','M106 S0'],
]
