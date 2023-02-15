# -*- coding: utf-8 -*-
""" Created on Tue Oct 22 18:22:17 2019 @author: henriquehafner@poli.ufrj.br """
import time
import glob
import os
import marlin_gcode_toolbox

class machine_interface():

    def __init__(self):
        #machine controller attributes
        self.serial_handler = object
        self.machine_interface_mode = -1  # 0 is idle state , -1 is no binded device
        self.setup_done = False
        self.keeplooping = False
        self.command_write_queue = []
        self.feedback_timestamp = 0
        self.monitor_timestamp = 0
        self.datatable = []
        self.monitor_serial_data =[]
        self.flag_timer = -1
        self.flag_monitoring = True
        self.wait_reach = False
        
        #comand_file attributes, gcode
        self.gcode_data = [[';LAYER:9'], 0, 'Null', 0]  # [Gcode File, file line pos,file name, end of file line index]
        self.gcode_data_name = 'Null'
        self.gcode_data_version = 'Null'
        self.gcode_data_adress = 'Null'
        self.gcode_dir = 'Null'
        self.gcode_list = ['Null']
        self.gcode_flag = False
        self.gcode_feedbackneeded_list = [
            'G0','G1','G00','G01','M105','M109','M190','M400','G28',
            'M104','M140'
            ]
        self.gcode_notfeedback_list = [
            ]
        self.gcode_log_failedfeedback = []

    def serial_handler_set_instance(self,serial_handler_l):
        self.serial_handler = serial_handler_l

    def monitor_machine_update(self,return_data=True):
        if time.time() - self.monitor_timestamp > 5 and \
        self.machine_interface_mode == 1:
            self.monitor_timestamp = time.time()
            write_cue = self.command_write_queue
            if len(write_cue) == 0:
                self.command_custom_insert('stats')
            elif len(write_cue) == 1 and write_cue[0][:4] != 'M105':
                self.command_custom_insert('stats')

        datatable_l = self.datatable_update(size=20,return_only=True)
        datatable_l.reverse()
        monitor_data_app_l = []
        
        temp_status = ['Failed to find a response in datatable']
        for message in datatable_l:
            if message[1][1] == 'r' and message[2].rfind('T:') > -1:
                temp_status = message[2][3:]
                break
        monitor_data_app_l.append(temp_status)

        monitor_data_app_l.append('file: '+self.gcode_data_name+
                                  ' version: '+self.gcode_data_version)
        monitor_data_app_l.append('Machine mode: '+str(self.machine_interface_mode))
        monitor_data_app_l.append('Command queued to write.')
        
        for command in self.command_write_queue[0:5]:
            monitor_data_app_l.append(command)
        len_queued = len(self.command_write_queue)
        if len_queued > 5:
            monitor_data_app_l += ['[...] More:',str(len_queued-5)]
        self.monitor_data = monitor_data_app_l
        if return_data == True:
            return self.monitor_data
        else:
            return None
        return ['none','none']

    def monitor_serial_update(self):
        return self.monitor_serial_data

    def serialhandler_parse_monitor_data(self):
        self.monitor_serial_data = self.serial_handler.monitor_serial_get_data(21)
        return True
    
#  Gcode methods
    def gcode_message_conditioner(self,message):
        acceptable_command = ['G', 'M'] #Check if message is a valid command
        is_valid_command = False
        for i in acceptable_command:
            if message[:1] == i:
                is_valid_command = True
                break
        if is_valid_command == False:
            print('invalid command: ',message)
            return False      
        if message[-1] != '\n': #Force a line break at end
            message = message+'\n'
        message = bytes(message,'utf-8') #encode to bytes
        return message

    def gcode_set_data(self):
        with open(self.gcode_data_adress) as f:
            gcode_data_l = f.read()
        gcode_data_l = gcode_data_l.split('\n')
        target_file_index = self.gcode_data_adress.rindex('\\') #finding star position of file name string.
        gcode_data_name_l = self.gcode_data_adress[target_file_index+1:] #extracting the file_name from path
        self.gcode_data_name = gcode_data_name_l
        self.gcode_data[0] = gcode_data_l
        self.gcode_data[1] = 0
        self.gcode_data[2] = gcode_data_name_l
        self.gcode_data[3] = len(gcode_data_l)-1 # subtractin 1 to start in line 0 index 0
        return True

    def gcode_data_handler(self,arg_def='GetNewest',gcode_datas_dir_l='None'):#pick a gcode file
        if gcode_datas_dir_l == 'None':
            gcode_datas_dir_l = os.getcwd()
        gcode_data_name_l = 'Null'
        if arg_def == 'GetNewest':
            gcode_datas_list_l = glob.glob(os.path.join(gcode_datas_dir_l,
                                                        '*.gcode'))
            if len(gcode_datas_list_l) > 0:
                gcode_datas_list_l.sort(key=os.path.getctime,reverse=True)
                target_file_index = gcode_datas_list_l[0].rindex('\\') #finding star position of file name string.
                gcode_data_name_l = gcode_datas_list_l[0][target_file_index+1:] #extracting the file_name from path
            else:
                print("No .gcode file found in ",gcode_datas_dir_l)
                return False
        else:
            print('Unexpected arg_def argument.')
            return False
        gcode_data_adress_l = os.path.join(gcode_datas_dir_l,
                                              gcode_data_name_l)
        if os.path.exists(gcode_data_adress_l):
            self.gcode_data_adress = gcode_data_adress_l
            self.gcode_data_name = gcode_data_name_l
            self.gcode_data_version = os.path.getctime(self.gcode_data_adress)
            self.gcode_data_version = time.ctime(self.gcode_data_version)[4:16]
            self.gcode_dir = gcode_datas_dir_l
            self.gcode_list = gcode_datas_list_l
            self.gcode_set_data()
            print('GCODE Loaded: ',self.gcode_data_adress)
            return True
        else:
            print('Unable to find file: ',gcode_data_adress_l)
            return False
        return False

    def machine_writer_handler(self):
        if self.feedback_waiting() is True:  #check if  should w8 for feedback
            return False
        command = None
        mstats = self.machine_interface_mode
        
        if mstats == 0:  #idle, state.
            print('Forbidden to write from idle state, mstats = ',mstats)
            return False
        elif len(self.command_write_queue) == 0 and mstats == 1:  # manual operation waiting, state.
            None
            return True
        elif len(self.command_write_queue) == 0 and mstats >= 2:  # feed command from stream, state.
            command = self.gcode_stream()
            print(command)
            if command == False:  # unable to stream a command
                self.machine_interface_mode = 1
                print('No command to stream, machine_interface_mode set to 1')
                return False
            else:
                self.command_write_queue.append(command)
                return True
        elif len(self.command_write_queue) >= 1 and mstats >= 1:  # write command from queue, state.
            command = self.command_write_queue[0]
            writing_flag = self.write_command_serial(command)
            if writing_flag is True:
                self.command_write_queue.pop(0)
                return True
        else:
            print('failed to write','machine_interface_mode:',self.machine_interface_mode
                  ,'command_write_queue :',self.command_write_queue)
            return False

    def feedback_waiting(self):
        if self.serial_handler.waiting_feedback > 0:
            fb_flag = self.serial_handler.feedback_get_status()
            if fb_flag is False:
                waiting_time = time.time()-self.feedback_timestamp
                if self.serial_handler.waiting_feedback == 1:
                    if waiting_time < 120:
                        return True
                elif self.serial_handler.waiting_feedback == 2:
                    if waiting_time < 120:
                        return True
                else:
                    print('Feedback waiting failed.')
                    self.serial_handler.waiting_feedback = 0
                    return True
            else:
                self.serial_handler.waiting_feedback = 0
                return False
        else:
            return False
                
    def set_feedback_needs(self,message:str):  # Specific to 3D printer
        '''
        Set:
        self.serial_handler.waiting_feedback = 0
            Recoganized command, no need of feedback.
        self.serial_handler.waiting_feedback = 1
            Recoganized command, needs feedback.
       self.serial_handler.waiting_feedback = 2
            Unrecoganized command, needs feedback.
        Parameters
        ----------
        message : str
            message to extract command and analize feedback needs.
        '''
        gcode = self.message_exctract_gcode(message)
        for i in self.gcode_notfeedback_list:
            if i == gcode:
                self.serial_handler.waiting_feedback = 0
                return None
        for i in self.gcode_feedbackneeded_list:
            if i == gcode:
                self.serial_handler.waiting_feedback = 1
                self.feedback_timestamp = time.time()
                return None
        self.serial_handler.waiting_feedback = 2
        self.feedback_timestamp = time.time()
        return None

    def log_failedfeedback(self,message:int):  # Deprecable
        ''' log gcode message in instance propertie
        '''
        gcode = self.message_exctract_gcode(message)
        for i in self.gcode_log_failedfeedback:
            if i == gcode:
                return None
        self.gcode_log_failedfeedback.append(gcode)
        print('Logged feedback fail for:',gcode)
        
    def message_exctract_gcode(self,message:int):
        ''' recoganize and return gcode until first space character
        '''
        gcode = ''
        for char in message:
            if char == ' ':
                break
            gcode += char
        return gcode
        
    def write_command_serial(self,command:str):
        command_conditioned = self.command_conditioner(command)
        if isinstance(command_conditioned,bytes):
            write_flag = self.serial_handler.write_serial(command_conditioned)
            if write_flag is True:
                self.set_feedback_needs(command)
                return True  # sucessful writed
            else:
                return False  # unsuccessful writed
        elif command_conditioned is False:
            return True  # ignoring commands conditioned to False
        else:
            print('unexpectated command_conditioned.',command_conditioned)
        return True
    
    def command_conditioner(self,command:str):  # 3D printer especifics
        if len(command) == 0:
            return False
        acceptable_command = ['G', 'M'] #Check if message is a valid command
        is_valid_command = False
        for i in acceptable_command:
            if command[0] == i:
                is_valid_command = True
                break
        if is_valid_command == False:
            print('invalid command: ',command)
            return False 
        if command.rfind(';') > 0:
            command = command.split(';')[0]
        if command[-1] == ' ':
            command = command[:-1]
        if command[-1] != '\n': #Force a line break at end
            command = command+'\n'
        command = bytes(command,'utf-8') #encode to bytes
        return command

    def gcode_stream(self):
        """ return the current line of gcode and increment line position.
            return False if line position exceeds gcode_data line number
        """
        if self.gcode_data[1] > self.gcode_data[3]-1:  #Checking if achieved end of gcode file.
            print("End of gcode file")
            return False
        gc_line_pos = self.gcode_data[1]
        gc_linebwrite = self.gcode_data[0][gc_line_pos]
        self.gcode_data[1] +=1
        return gc_linebwrite

    def gcode_move_lastlinepos(self,line:int,relative:bool=True):
        '''shift or set position line.
        Parameters
        ----------
        line : int
            desired shift in line position or new absolute line position.
        relative : bool, optional
            Pass False if the line is not a relative shift from atual line.
            The default is True.
        Returns
        -------
        bool
            True if the line can be set. False if line is 
            greater than last line or smaller than zero.

        '''
        curr_line = self.gcode_data[1]
        if relative:
            target_line = curr_line+line
        else:
            target_line = line
        if target_line < 0:
            print('requested target_line was negative.')
            return False
        if target_line > self.gcode_data[3]:  # check if target line exceeds file
            print('requested target_line is greater than last line.')
            return False
        self.gcode_data[1] = target_line
        return True
        
    def event_check(self):
        if not self.flag_monitoring:
            return None
        
        curr_line = self.gcode_data[1]
        next_mesage = self.gcode_data[0][curr_line]

        if next_mesage[:5] == ';TYPE':
            if next_mesage[:11] == ';TYPE:SKIRT':
                self.wait_reach = True
            else:
                self.wait_reach = False
        if self.wait_reach == True:
            if len(self.command_write_queue) == 1 and\
            self.command_write_queue[0][:1] == 'G':
                self.command_custom_insert('wait')

        # if next_mesage[:-1] == (';LAYER:') \
        #     and int(next_mesage[-1]) <= 4:
        #     if self.machine_interface_mode >= 2:
        #         self.machine_interface_mode = 1
        #         if self.flag_timer == -1:
        #             self.flag_timer = time.time()
        #             self.command_custom_insert('move_c2')
        #         print('layer cooling idle started.')
        #     if self.flag_timer != -1 and time.time() - self.flag_timer > 60:
        #         self.flag_timer = -1
        #         self.machine_interface_mode = 2
        #         print('layer cooling idle time ended.')

        return False

    def command_custom_insert(self,function):
        for i in marlin_gcode_toolbox.function_table:
            if function == i[0]:
                commands = i[1:]
                self.command_write_queue += commands
                return True
        return False

    def set_interface_mode(self,state:int):
        self.machine_interface_mode = state
    
    def terminal_gcode_caller(self,call_message):
        if call_message == 'setup':
            commands = ['WriteBuffer','StreamGcode','ReloadGecode']
            for func in marlin_gcode_toolbox.function_table:
                commands.append(func[0])
            return commands
        elif call_message == 'WriteBuffer':
            self.machine_interface_mode = 1
        elif call_message == 'StreamGcode':
            self.machine_interface_mode = 2
        elif call_message == 'ReloadGecode':
            self.gcode_data_handler('GetNewest',self.gcode_dir)
        elif isinstance(call_message,str):
            self.command_custom_insert(call_message)

# Operation methods   
    def run(self):
        if self.gcode_flag is False:
            for path_l in marlin_gcode_toolbox.gcode_filepath:
                self.gcode_flag = self.gcode_data_handler('GetNewest',path_l)
                if self.gcode_flag  == True:
                    break
        if self.serial_handler.bind_status == True:
            self.machine_interface_mode = 1
        self.setup_done = True
        if self.keeplooping != True:
            self.keeplooping = True
            print('Machine Interface in main loop.')
            self.main_loop()

    def main_loop(self):
        while self.keeplooping == True:
            time_begin_loop = time.time()
            self.iterate()
            while time.time()-time_begin_loop < 0.001:
                time.sleep(0.001)
        print('Machine Interface main loop terminated.')

    def iterate(self):
        try:
            if self.machine_interface_mode >= 0:
                self.serialhandler_parse_monitor_data()
                self.event_check()
            if self.machine_interface_mode >= 1:
                self.machine_writer_handler()
        except Exception as error_message:
            print(error_message)
            self.keeplooping = False



            

















