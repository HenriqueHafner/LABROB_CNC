# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 18:22:17 2022

@author: henrique hafner
"""

class gcode_parser:

    def __init__(self):
        self.commands = "GMTgmt"
        self.axes = "xyzXYZ"
        self.axis_id =    {'X':0, 'x':0, 'Y':1, 'y':1,'Z':2, 'z':2}
        self.axis_label = {0:'X', 1:'Y', 2:'Z'}
        self.signal_label = {False:'+', True:'-'}
        self.mm_per_steps = [0.2, 0.2, 0.2]

    def get_lines(self, gcode):
        lines_formated = []
        gcode = gcode.replace('\n',';')
        lines = gcode.split(';')
        for line in lines:
            command, residue = self.get_command(line)
            if len(command) <= 0:
                continue
            params = self.get_params(residue)
            lines_formated.append([command, params])
        return lines_formated
    
    def get_command(self, line):
        command = []
        message_residue = ''
        if ( len(line) >= 3 ) and ( self.commands.find(line[0]) > -1 ):
            command_leter = line[0].upper()
            command_number_end_index = line.find(' ')
            command_number_str = line[1:command_number_end_index]
            number = self.numberize(command_number_str)
            if number.is_integer():
                number = int(number)
            command = [command_leter, number]
            message_residue = line[command_number_end_index:]
        return command, message_residue
            
    def get_params(self, params_str):
        params = []
        params_entries = params_str.split(' ')
        for entry in params_entries:
            if not entry:
                continue
            if self.axes.find(entry[0]) > -1:
               axis = entry[0].upper()
               value = self.numberize(entry[1:])
               if value:
                   params.append([axis,value])
        return params

    def G0_command(self, formated_gcode_line):
        steps = [0,0,0]
        directions = [0,0,0]
        ok_flag = False
        try:
            if formated_gcode_line[0] == ['G',0]:
                for axis_motion_order in formated_gcode_line[1]:
                    axis = self.axis_id[axis_motion_order[0]]
                    coord = axis_motion_order[1]
                    step = self.coord_to_steps(coord, self.mm_per_steps[axis])
                    direction = (coord < 0)
                    steps[axis] = step
                    directions[axis] = direction
                    ok_flag = True
        except:
            ok_flag = False
        return [ok_flag, directions, steps]
            

    def numberize(self, number_str):
        try:
            number = float(number_str)
            return number
        except:
            return False
        
    def coord_to_steps(self, coord, mm_per_steps):
        steps = divmod(coord/mm_per_steps, 1)[0]
        steps = abs(int(steps))
        return steps

    def translate_to_motioncontroller(self, command):
        if not command[0]:
            return False
        message = ""
        steps = command[2]
        directions = command[1]
        for axis in range(len(steps)):
            if steps[axis] == 0:
                continue
            direction = directions[axis]
            signal = self.signal_label[direction]
            axis_label = self.axis_label[axis]
            step_str = str(steps[axis])
            message_piece = signal+axis_label+step_str
            message += message_piece
        message = message + '\n'
        return message
    
    def translate_gcode(self, gcode_str):
        lines = self.get_lines(gcode_str)
        commands = []
        messages = []
        for cond_line in lines:
            command = self.G0_command(cond_line)
            commands.append(command)
            message = self.translate_to_motioncontroller(command)
            if message:
                messages.append(message)

# #tester
gcode_example = "G00 Y+200 Z-400;G00 Y+200 Z-400\nG02 Y+200 Z-400\n;G00 Y+200 Z-400;"
parser = gcode_parser()



# parser.translate_to_motioncontroller()

# motion_commands = [ [True, [0, False, True], [0, 1000, 2000]] ]

