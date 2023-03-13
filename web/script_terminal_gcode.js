class terminal_gcode {
    constructor() {
        this.id_parent_label = "terminal_gcode";
        this.div_main = document.getElementById("div_".concat(this.id_parent_label));
        this.setup_html_message_console();
        this.setup_html_inputfield();  
    }

    setup_html_message_console() {
        this.canvas = document.createElement("CANVAS");
        this.canvas.id = "canvas_".concat(this.id_parent_label);
        this.canvas.width  = 500;
        this.canvas.height = 410;
        this.ctx = this.canvas.getContext("2d");
        this.div_main.appendChild(this.canvas);
        this.message_console_timestamp = Date.now()
        this.message_data = Array(20)
        setInterval(function() { obj_terminal_gcode.update_messages_window(obj_terminal_gcode) }, 200);
    }

    setup_html_inputfield() {
        this.input_field_html = document.createElement("Object");
        this.input_field_html.id = "console_input".concat(this.id_parent_label);
        this.input_field_html.setAttribute("type", "text/html");
        this.input_field_html.setAttribute("data", "lined_input_boilerplate.html");
        this.input_field_html.style.width = 505;
        this.input_field_html.style.height = 515;
        this.input_field_html.style.alignItems = "center";
        this.input_field_html.style.backgroundColor = "white";
        this.div_main.appendChild(this.input_field_html);        
        this.setup_interface_buttons();
    }

    get_inputfield_data() {
        var input_field = this.input_field_html.contentDocument.getElementById("lined_input")
        var str_gcode_message = input_field.value
        input_field.value = ""
        return str_gcode_message
    }

    async ell_python_exposed_fun_call(python_call) {
        let return_data = await globalThis.eel.arbitrary_call(python_call)();
        return return_data
    }

    async setup_interface_buttons() {
        let interface_data = await this.ell_python_exposed_fun_call("buttons_teminal_gcode()");
        var div_buttons = document.createElement("DIV");
        div_buttons.id = "buttons_".concat(this.id_parent_label);
        var obj_scope = this;
       
        for (var button_data_index in interface_data) {
            var label = interface_data[button_data_index][0];
            var call  = interface_data[button_data_index][1];
            var button = document.createElement("BUTTON");
            button.call_text = call
            button.type = "button";
            button.innerHTML = label;
            button.id = label;
            button.onclick = function() {obj_scope.ell_python_exposed_fun_call(this.call_text)};
            div_buttons.appendChild(button);
        }
        this.div_main.appendChild(div_buttons);
    }

    async update_messages_window(instance) {
        // Whiping the draw area
        instance.ctx.fillStyle = '#ebeeff';
        instance.ctx.fillRect(0, 0,instance.canvas.width,instance.canvas.height);
        // Drawing data
        instance.ctx.fillStyle = '#000000';
        instance.ctx.font = '16px Confortaa';
        var linecount = 1;
        for (var i in instance.message_data) {
            instance.ctx.fillText(instance.message_data[i],10,linecount*20);
            linecount ++;
        }
        instance.ctx.stroke();
        if (Array.isArray(instance.message_data)) {
            // Renew promise of data, async
            instance.message_data = await eel.get_last_messages_window()();
            instance.message_data = instance.message_data.slice(0,20)
            var mw_frequency = Date.now() - instance.message_console_timestamp
            instance.message_console_timestamp = Date.now()
        }
    }

}


var obj_terminal_gcode = new terminal_gcode();
function get_inputfield_data() {
    var message = obj_terminal_gcode.get_inputfield_data()
    return message
};
eel.expose(get_inputfield_data);






























