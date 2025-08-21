#gui backend
# -*- coding: utf-8 -*-
""" Created on Wed Nov 26 01:21:33 2020 @author: henriquehafner@poli.ufrj.br """

import threading

class GUI():
    
    def __init__(self):
        self.machine_core_reference = object()
        self.eel = object()
    
    def setup_websocket(self):
        import eel as eel_module
        self.eel = eel_module
        self.eel.expose(self.arbitrary_call)
        self.eel.expose(self.get_last_messages_window)
        
    def run_eel_webserver(self):
        self.setup_websocket()
        self.eel.init('web')
        print('EtrO App webserver starting..')
        self.eel.start('cncmachinedashboard.html',port=80)
        print('EtrO App webserver Closed..')
        return None
    
    def run_webserver_thread(self):
        self.webserver_thread = threading.Thread(name='webserver_tread', target=self.run_eel_webserver)
        self.webserver_thread.start()
    
    def set_core_reference(self, target_object):
        self.machine_core_reference = target_object
    
    def buttons_teminal_gcode(self):
        buttons_data = [
            ["Enviar Linhas para controlador", "str_gcode_parse_gui()"],
            ["Testar comunicação", "test_call()"],
            ]
        return buttons_data
    
    def get_last_messages_window(self):
        messages_window_raw = self.machine_core_reference.get_messagelog_window()
        messages_window = list(range(20))
        for i in range(20):
            messages_window[i] = str(messages_window_raw[i][0])[1:] + ' ' + messages_window_raw[i][1] + messages_window_raw[i][2]
        return messages_window

    def str_gcode_parse_gui(self):
        gcode_text = self.eel.get_inputfield_data()()
        print("parsing string:", gcode_text)
        status_flag = self.machine_core_reference.gcode_parse(gcode_text)
        return status_flag

    def test_call(self):
        print("JavasScript asked for a handshake, proceeding to handshake.")
        return "Python accepted handshake."

    def arbitrary_call(self, call_message):
        try:
            call_message = "self."+call_message
            eval_return = eval(call_message)
            return eval_return
        except Exception as e:
            print("Failed to call: ", call_message)
            print(e)
            error_return = int(-1)
            return error_return

# GUI_instance = GUI()
# GUI_instance.run_eel_webserver()