# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:17:34 2023

@author: henrique hafner
"""

class MachineCore:
    
    def __init__(self):
        self.vars_constructor()
        self.setup_serialinterface()
        self.setup_gcode_handler()
        self.GUI_run()
    
    def vars_constructor(self):
        self.serial_instance = object
        self.GUI_instance = object
        self.gcode_handler_instance = object
        self.GUI_running = False

    def setup_gcode_handler(self):
        import gcode_handler
        self.gcode_handler_instance = gcode_handler.gcode_handler_core()

    def GUI_run(self):
        import GUI_labrobcnc
        self.GUI_instance = GUI_labrobcnc.GUI()
        self.GUI_instance.set_core_reference(self)
        self.GUI_instance.run_eel_webserver()
        # self.GUI_instance.run_webserver_thread()
        self.GUI_running = True
        return True
    
    def setup_serialinterface(self):
        import serialasynchandler
        self.serial_instance = serialasynchandler.serialasynchandler_core()
        self.serial_instance.bind_serial_device(serial_device='USB')
        self.serial_instance.loop_stopped = False
        return True

    def get_messagelog_window(self):
        return self.serial_instance.get_messagelog_window()
    
    def gcode_parse(self, gcode_text):
        machine_commands = self.gcode_handler_instance.translate_gcode(gcode_text)
        print(machine_commands)
        self.serial_instance.towrite_buffer_append(machine_commands)
        return True

machine_core = MachineCore()