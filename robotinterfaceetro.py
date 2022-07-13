#robot interface
# -*- coding: utf-8 -*-
""" Created on Wed Nov 11 05:22:13 2020 @author: henriquehafner@poli.ufrj.br """

import threading
import time
import etrogui
import machineinterface
import serialasynchandler

machine_interface = machineinterface.machine_interface()
serialcom = serialasynchandler.serial_async_handler()
gui = etrogui.gui()

def wait_setup(target_object):
    waiting_since = time.time()
    obj_name_raw=str(target_object)
    obj_name=obj_name_raw[1:obj_name_raw.rfind(" object")]
    try :
        target_object.setup_done
        None
    except:
        print("Failed to find a setup_done propertie from: ",obj_name)
        return False
    while target_object.setup_done == False:
        time.sleep(0.5)
        if time.time()-waiting_since > 10:
            print("timeout while waiting setup from: ",obj_name)
            print("setup_done =  ",target_object.obj_name)
            return False
    if target_object.setup_done == True:
        print("Setup done for: ",obj_name)
        return True
    else:
        return False

def THREAD_1_script():  
    serialcom.run()
def THREAD_2_script():
    machine_interface.serial_handler_set_instance(serialcom)
    machine_interface.run()
def THREAD_3_script():
    gui.set_machine_interface(machine_interface)
    gui.run_webserver()

###Exposed methods###
@etrogui.eel.expose
def update_terminal_gcode():
    try:
        data = gui.update_terminal_gcode()
    except:
        data = ['Failed to get data.']
    return data
@etrogui.eel.expose
def call_terminal_gcode(call_mesage):
    data = gui.call_terminal_gcode(call_mesage)
    return data
@etrogui.eel.expose
def update_monitor_serial():
    try:
        data = gui.update_monitor_serial()
    except:
        data = ['Failed to get data.']
    return data
@etrogui.eel.expose
def update_monitor_machine():
    try:
        data = gui.update_monitor_machine()
    except:
        data = ['Failed to get data.']
    return data


THREAD_1 = threading.Thread(name='Serial Comunicator', target=THREAD_1_script)
THREAD_2 = threading.Thread(name='Machine Interface', target=THREAD_2_script)
THREAD_3 = threading.Thread(name='GUI Handler', target=THREAD_3_script)

THREAD_1.start()
wait_setup(serialcom)
THREAD_2.start()
wait_setup(machine_interface)
THREAD_3.start()
