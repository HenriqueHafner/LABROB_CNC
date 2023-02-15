# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 18:22:17 2022

@author: henrique hafner
"""
import time
import serial

class SerialAsyncHandler:

    def __init__(self):
        self.vars_constructor()

    def vars_constructor(self):
        #serial communication attributes
        self.serial_module = serial
        self.setup_done = False
        self.bind_status = False
        self.serial_interface = object  # var will be further overwrited with serial comunmicator instance
        self.ControllerPortName = ''  # Port Name
        self.comunicator_state = 0
        self.settings_dict = dict()

        self.read_buffer = ''
        self.towrite_buffer = []
        self.msglog_lines = 128
        self.msglogline = ["",""]
        self.msglog = list(range(self.msglog_lines))
        for i in range(self.msglog_lines):
            self.msglog[i] = self.msglogline.copy()
        self.msglog_ipos = 0  # Position to insert new messages
        self.msglog_mcounter = 0  # message counter       

    def bind_serial_device(self, serial_device:str):
        from serial.tools import list_ports
        serial_ports = list_ports.comports()
        for sp in serial_ports:
            hwid = sp.hwid
            if hwid.find(serial_device) > 0:
                self.ControllerPortName = sp.name
                print('Found Serial port for Controler with ', hwid, ' hwid')
                self.serial_interface = self.serial_module.Serial(port=self.ControllerPortName, timeout=1)
                print('Port: ',self.ControllerPortName, 'connected.')
                self.settings_dict = self.serial_interface.getSettingsDict()
                print(self.settings_dict)
                self.setup_done = True
                self.bind_status = True
                return True
        print('Unable to find a Serial port with ',serial_device,' in hwid')
        return False
    
    def write_from_towrite_buffer(self):
        if len(self.towrite_buffer) == 0 :
            return False
        data = self.towrite_buffer.pop(0)
        if type(data) is not bytes:
            data = data.encode()
        try:
            self.serial_interface.write(data) #write data
            self.messagelog_insert_data(data, label='w:')
            return True
        except:
            failure_message = "serial_interface failed to write"
            self.messagelog_insert_data(failure_message, label='e:')
            if not self.setup_done:
                setup_error = "serial_interface setup pending"
                self.messagelog_insert_data(setup_error, label='e:')
            print('serial_interface failed to write:',data)
            return False

    def parse_interface_read_buffer(self):
        counter_bytes_to_read = self.serial_interface.inWaiting()
        if counter_bytes_to_read > 0:
            try:
                bytes_read = self.serial_interface.read()
            except:
                failure_message = "serial_interface failed to read"
                self.messagelog_insert_data(failure_message, label='e:')
                if not self.setup_done:
                    setup_error = "serial_interface setup pending"
                    self.messagelog_insert_data(setup_error, label='e:')
                print('serial_interface failed to read')
                return False
            self.read_buffer += bytes.decode(bytes_read)
        return True

    def parse_messages_from_async_buffer(self, message_separator = '\n'):
        current_message_buffer = ''
        messages_found = []
        for char in self.read_buffer:
            current_message_buffer += char
            if char == message_separator:
                messages_found += [current_message_buffer]
                current_message_buffer = ''
        self.read_buffer = current_message_buffer
        for message in messages_found:
            self.messagelog_insert_data(message, label = 'r: ')
        return True

    def messagelog_insert_data(self, message, label:str ='null'):
        label = label[:5]
        if type(message) is bytes:
            message = message.decode()
        if len(message) >= 65:
            message = message[:59] + '[...]'
        self.msglog[self.msglog_ipos] = [label,message]
        self.msglog_ipos += 1
        self.msglog_mcounter += 1
        if self.msglog_ipos >= self.msglog_len:  #preventing out of range index
            self.msglog_ipos = 0
        return True
    
    def get_messagelog_window(self,window_lines_size=20):
        window_lines_size = min(window_lines_size, self.msglog_lines)
        star_index = self.msglog_ipos
        end_index = star_index-window_lines_size
        if end_index >= 0 :
                messagelog_window = self.msglog[end_index:star_index]
        if end_index <  0 :        
                messagelog_window = self.msglog[end_index:] + self.msglog[:star_index]
        return messagelog_window
    
    def serial_dump(self):
        try:
            self.serial_interface.reset_input_buffer()
            return True
        except:
            return False
    
    def serial_close(self):
        try:
            time.sleep(0.5)
            self.serial_interface.close()
            time.sleep(0.5)
            self.vars_constructor()
            print('Serial connection closed.')
            return True
        except:
            print('Failed to close serial connection.')
            return False

###
# Tester
###

# test with ghost
def tester_1():
    import serialTester
    sc = SerialAsyncHandler()
    sc.serial_interface = serialTester
    sc.setup_done = True
    sc.bind_status = True
    for i in range(6):
        sc.write_from_towrite_buffer()
        sc.parse_interface_read_buffer()
        sc.parse_messages_from_async_buffer()
        sc.towrite_buffer += [b'teste\n']
    print(sc.msglog[:20])
    return True

# test with real serial inerface
#sc = serial_async_handler()
# sc.bind_serial_device(serial_device='1A86:7523')


















