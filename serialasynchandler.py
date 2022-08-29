# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 18:22:17 2019

@author: henrique.ferreira
"""
import time
import serial
import serial.tools.list_ports as list_ports

class serial_async_handler():

    def __init__(self):
        self.vars_constructor()

    def vars_constructor(self):
        #serial communication attributes
        self.setup_done = False
        self.bind_status = False
        self.serial_interface = False  # var will be further overwrited with serial comunmicator instance
        self.ControllerPortName = ''  # Port Name 

        self.serial_buffed_data = b''
        self.serial_towrite_data = []

        self.datatable = [[[b'Empty',b'Empty']]*self.datatable_len]
        self.datatable_len = 128
        self.datatable_ipos = 0  # Position to insert new messages
        self.datatable_mcounter = 0  # message counter       

    def bind_serial_device(self, serial_device:str):
        SerialPorts = list_ports.comports()
        for sp in SerialPorts:
            hwid = sp.hwid
            if hwid.find(serial_device) > 0:
                self.ControllerPortName = sp.name
                print('Found Serial port for Controler with ', hwid, ' hwid')
                self.serial_interface = serial.Serial(port=self.ControllerPortName, timeout=1)
                print('Port: ',self.ControllerPortName, 'connected.')
                settings_dict = self.serial_interface.getSettingsDict()
                print(settings_dict)
                self.serial_interface.apply_settings(settings_dict)
                return True
        print('Unable to find a Serial port with ',serial_device,' in hwid')
        return False

    def write_from_towrite_data(self):
        if len(self.serial_towrite_data) == 0 :
            return False
        data = self.serial_towrite_data.pop(0)
        if data != bytes:
            print('Data is not bytes.')
            return False
        try:
            data = self.serial_towrite_data.pop(0)
            self.serial_interface.write(data) #write data
            self.datatable_insert_data(data, label=b'w:')
            return True
        except:
            print('serial_interface failed to write:',data)
            return False

    def parse_read_buffer(self): 
        readbuffer_size = self.serial_interface.in_waiting  # keep reading buffer until have less than this.
        if readbuffer_size <= 0:
            return False
        else:
            data_piece = self.serial_interface.read(readbuffer_size)
            self.serial_buffed_data.append(data_piece)
        return True

    def datatable_insert_data(self, separator:bytes=b'\n', label:bytes=b''):
        label = label[:5]
        ipos = self.datatable_ipos
        mcounter = self.datatable_mcounter
        data = self.serial_buffed_data
        data = data.split(separator)
        if data[-1] == b'':
            self.serial_buffed_data = []
        for message_i in data:
            self.datatable[ipos] = [mcounter,label,message_i]
            ipos += 1
            mcounter += 1
            if ipos >= self.datatable_len:  #preventing out of range index
                ipos = 0
        self.datatable_ipos = ipos
        self.datatable_mcounter = mcounter
        return True
      
    # def monitor_serial_update(self,return_data=True,size=20):
    #     '''fill monitor_data with formated data from datatable to show in 
    #     serial monitor.
    #     Parameters:
    #     ----------
    #     return_data : bool, optional
    #         True to return data, False to just update.
    #     Returns:
    #     -------
    #     monitor_data_l : list
    #         return updated monitor_data_l
    #     True : bool
    #         storing updated data in serial_async_handler.monitor_data
    #     '''
    #     # self.incomming_data_handler()
    #     recent_messages = self.get_datatable_section(size)
    #     monitor_data_l = []
    #     for message in recent_messages:
    #         nessage_str = message[1]+message[2]
    #         if len(nessage_str) >= 80:
    #             nessage_str = nessage_str[0:75]
    #             nessage_str += ('[...]')
    #         monitor_data_l.append(nessage_str)
    #         if len(monitor_data_l) >= size:
    #             break
    #     self.monitor_data = monitor_data_l
    #     if return_data == True:
    #         return monitor_data_l
    #     else:
    #         return True

    # def get_datatable_section(self, size):
    #     if size > self.datatable_len:
    #         size = self.datatable_len - 1
    #     msg_pos = self.datatable_ipos - 1
    #     datatable_l = []
    #     for i in range(size):
    #         datatable_l.append(self.datatable[msg_pos])
    #         msg_pos += -1
    #     return datatable_l
    
    # def monitor_serial_get_data(self,requested_size):
    #     if self.waiting_feedback == 0:
    #         self.incomming_data_handler()
    #     self.monitor_serial_update(size=requested_size)
    #     return self.monitor_data

    def serial_dump(self):
        self.serial_interface.reset_input_buffer()
        return True
    
    def serial_close(self):
        try:
            time.sleep(0.5)
            self.serial_interface.close()
            time.sleep(0.5)
            self.__init__()
            print('Serial connection closed.')
            return True
        except:
            print('Failed to close serial connection.')
            return False

sc = serial_async_handler()
sc.bind_serial_device(serial_device='1A86:7523')



















