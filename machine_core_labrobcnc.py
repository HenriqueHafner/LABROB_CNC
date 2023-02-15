# -*- coding: utf-8 -*-
"""
Created on Mon Feb 13 18:17:34 2023

@author: henrique hafner
"""


class MachineCore:
    
    def __init__(self):
        self.vars_constructor()
        self.setup_serialinterface()
        self.GUI_run()
    
    def vars_constructor(self):
        self.serial_reference = object
        self.GUI_instance_reference = object        
        self.GUI_running = False

    def GUI_run(self):
        import GUI_labrobcnc
        self.GUI_instance_reference = GUI_labrobcnc.GUI()
        self.GUI_instance_reference.set_machine_interface_reference(self.serial_reference)
        self.GUI_instance_reference.run_webserver_thread()
        self.GUI_running = True
        return True
    
    def setup_serialinterface(self):
        import serialasynchandler
        self.serial_reference = serialasynchandler.SerialAsyncHandler()
        self.serial_reference.bind_serial_device(serial_device='1A86:7523')
        return True
    
machine_core = MachineCore()