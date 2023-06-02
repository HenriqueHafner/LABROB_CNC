# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 18:22:17 2022

@author: henrique hafner
"""
import time
import serial
import threading

class serialasynchandler_core:

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
        self.reciever_buffer_available = 0
        self.message_size_limit_to_write = 63

        self.read_buffer = ''
        self.towrite_buffer = []
        self.msglog_lines = 128
        self.msglogline = ["Null","Null","Null"]
        self.msglog = list(range(self.msglog_lines))
        for i in range(self.msglog_lines):
            self.msglog[i] = self.msglogline.copy()
        self.msglog_ipos = 0  # Position to insert new messages
        self.msglog_mcounter = 1000  # message counter
        self.loop_stopped = True
        self.loop_events_thread = threading.Thread(name='serial_loop_events', target=self.loop_events)
        self.loop_events_thread.start()

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
                time.sleep(0.5)
                self.serial_dump()
                return True
        print('Unable to find a Serial port with ',serial_device,' in hwid')
        return False
    
    # def write_availability(self):
    #     last_msglog = self.msglog[self.msglog_ipos-1]
    #     last_message_label = last_msglog[1]
    #     label_first_char = last_message_label[0]
    #     if label_first_char != 'r':
    #         self.debug_var = label_first_char
    #         return False
    #     last_message_id = last_msglog[0]
    #     if last_message_id == self.reciever_buffer_last_report_id:
    #         self.debug_var = last_message_id
    #         return False
    #     last_message = last_msglog[2]
    #     buffer_command_index = last_message.find("B01")
    #     if buffer_command_index <0 :
    #         self.debug_var = buffer_command_index
    #         return False
    #     buffer_available = last_message[buffer_command_index+4:-1]
    #     if not buffer_available.isnumeric():
    #         self.debug_var = buffer_available
    #         return False
    #     self.reciever_buffer_available = int(buffer_available)
    #     return True

    def write_from_towrite_buffer(self, check_availability=True):
        if len(self.towrite_buffer) == 0 :
            return False
        data = self.towrite_buffer[0]
        message_length = len(data)
        if check_availability:
            if message_length > self.reciever_buffer_available:
                return False
        if type(data) is not bytes:
            data = data.encode()
        if len(data) > self.message_size_limit_to_write:
            failure_message = "failed to write: message too long"
            self.messagelog_insert_data(failure_message, label='e:')
            return False
        try:
            self.serial_interface.write(data) #write data
            self.towrite_buffer.pop(0)
            self.messagelog_insert_data(data, label='w:')
            self.reciever_buffer_available -= message_length
            return True
        except:
            failure_message = "serial_interface failed to write"
            self.messagelog_insert_data(failure_message, label='e:')
            if not self.setup_done:
                setup_error = "serial_interface setup pending"
                self.messagelog_insert_data(setup_error, label='e:')
            print('serial_interface failed to write:',data)
            return False
# machine_core.serial_instance.reciever_buffer_available


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
        self.read_buffer = current_message_buffer # keep the residue in read_buffer
        if messages_found == []:
            return False
        for message in messages_found:
            if message[:3] == "B01":
                try:
                    self.reciever_buffer_available = int(message[4:-1])
                except:
                    None
            self.messagelog_insert_data(message, label = 'r: ')
        return True

    def towrite_buffer_append(self, messages):
        try:
            if type(messages) is not list:
                messages = [messages]
            self.towrite_buffer += messages
            return True
        except:
            print("failed buff messages.")
            print(messages)
            return False

    def messagelog_insert_data(self, message, label:str ='null'):
        self.msglog_mcounter = self.msglog_mcounter + 1
        if self.msglog_mcounter >= 2000:
            self.msglog_mcounter = 1001
        counter = self.msglog_mcounter
        label = label[:5]
        if type(message) is bytes:
            message = message.decode()
        if len(message) >= 65:
            message = message[:55] + '[...]'
        self.msglog[self.msglog_ipos] = [counter, label,message]
        self.msglog_ipos += 1
        if self.msglog_ipos > self.msglog_lines-1:  #preventing out of range index
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
    
    def loop_events(self):
        while True:
            if not self.loop_stopped:
                self.write_from_towrite_buffer()
                self.parse_interface_read_buffer()
                self.parse_messages_from_async_buffer()
    
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

def tester():
    sc = serialasynchandler_core()
    sc.bind_serial_device(serial_device='1A86:7523')
    for i in range(6):
        sc.write_from_towrite_buffer()
        sc.parse_interface_read_buffer()
        sc.parse_messages_from_async_buffer()
        sc.towrite_buffer += [b'teste\n']
    print(sc.msglog[:20])
    return True

# machine_core.serial_instance.debug_var

















