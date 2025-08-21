class terminal_gcode {
    constructor() {
        this.id_parent_label = "terminal_gcode";
        this.div_main = document.getElementById("div_".concat(this.id_parent_label));
        this.setup_html_message_console();
        this.setup_html_inputfield();

        this.create_canvas();
        // this.create_textarea();
        this.create_button();

    }

    setup_html_message_console() {
        this.canvas = document.createElement("CANVAS");
        this.canvas.id = "canvas_".concat(this.id_parent_label);
        this.canvas.width  = 505;
        this.canvas.height = 515;
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

    create_canvas() {
        this.canvas_lines = document.createElement("canvas");
        this.canvas_lines.id = "canvas_lines_" + this.id_parent_label;
        this.canvas_lines.width = 505;
        this.canvas_lines.height = 515;
        // this.canvas_lines.style.border = "1px solid black";
        this.canvas_lines.style.backgroundColor = "#ebeeff'";
        this.ctx_lines = this.canvas_lines.getContext("2d");
        this.div_main.appendChild(this.canvas_lines);
    }

    create_textarea() {
        this.textarea = document.createElement("textarea");
        this.textarea.id = "textarea_" + this.id_parent_label;
        this.textarea.rows = 8;
        this.textarea.cols = 50;
        this.textarea.value = "G00 X0 Y0\nG01 X50 Y0\nG01 X50 Y50\nG01 X0 Y50\nG01 X0 Y0";
        this.div_main.appendChild(this.textarea);
    }

    create_button() {
        this.button = document.createElement("button");
        this.button.innerText = "Desenhar GCODE";
        this.button.style.display = "block";  // força a quebra de linha
        this.button.style.marginTop = "10px"; // opcional, espaçamento
        this.button.style.margin = "10px auto"
        this.button.onclick = () => this.draw_gcode();
        this.div_main.appendChild(this.button);
    }

    draw_gcode() {
        this.ctx_lines.setTransform(1, 0, 0, 1, 0, 0); // reset transform
        this.ctx_lines.clearRect(0, 0, this.canvas_lines.width, this.canvas_lines.height);

        let input_text = this.input_field_html.contentDocument.getElementById("lined_input");
        let str_gcode_message = input_text.value;
        let linhas = str_gcode_message.split("\n");

        let xAtual = 0, yAtual = 0;
        let xNovo = 0, yNovo = 0;

        // // Primeiro: determinar os limites máximos de deslocamento
        // let minX = 0, maxX = 0, minY = 0, maxY = 0;

        // for (let i = 0; i < linhas.length; i++) {
        //     let linha = linhas[i].trim();
        //     if (linha === "") continue;
        //     if (linha.startsWith("G00") || linha.startsWith("G01")) {
        //         let xIndex = linha.indexOf("X");
        //         let yIndex = linha.indexOf("Y");

        //         if (xIndex !== -1) {
        //             let xStr = linha.substring(xIndex + 1).split(" ")[0];
        //             xNovo += parseFloat(xStr);
        //         }

        //         if (yIndex !== -1) {
        //             let yStr = linha.substring(yIndex + 1).split(" ")[0];
        //             yNovo += parseFloat(yStr);
        //         }

        //         if (!isNaN(xNovo)) {
        //             minX = Math.min(minX, xNovo);
        //             maxX = Math.max(maxX, xNovo);
        //         }
        //         if (!isNaN(yNovo)) {
        //             minY = Math.min(minY, yNovo);
        //             maxY = Math.max(maxY, yNovo);
        //         }
        //     }
        // }

        // // Dimensões do conteúdo
        // let contentWidth = maxX - minX;
        // let contentHeight = maxY - minY;

        // let content_x_center = (maxX + minX)/2;
        // let content_y_center = (maxY + minY)/2;

        // // Fator de escala baseado na menor razão entre canvas e conteúdo
        // let scaleX = Math.abs(contentWidth / this.canvas_lines.width);
        // let scaleY = Math.abs(contentHeight / this.canvas_lines.height);
        // let scale = 0.9*Math.min(scaleX, scaleY);
        // // scale = 10;

        // Centraliza o conteúdo no canvas e aplica a escala
        this.ctx_lines.translate(this.canvas_lines.width/2, this.canvas_lines.width/2);
        this.ctx_lines.scale(1, 1);

        // Segundo loop: desenhar
        xAtual = 0;
        yAtual = 0;
        xNovo = 0;
        yNovo = 0;

        for (let i = 0; i < linhas.length; i++) {
            let linha = linhas[i].trim();
            if (linha === "") continue;
            if (linha.startsWith("G00") || linha.startsWith("G01")) {
                let xIndex = linha.indexOf("X");
                let yIndex = linha.indexOf("Y");

                if (xIndex !== -1) {
                    let xStr = linha.substring(xIndex + 1).split(" ")[0];
                    xNovo = xAtual + parseFloat(xStr);
                }

                if (yIndex !== -1) {
                    let yStr = linha.substring(yIndex + 1).split(" ")[0];
                    yNovo = yAtual + parseFloat(yStr);
                }

                this.ctx_lines.beginPath();
                this.ctx_lines.moveTo(xAtual, yAtual); // eixo Y invertido
                this.ctx_lines.lineTo(xNovo, yNovo);
                this.ctx_lines.strokeStyle = linha.startsWith("G00") ? "red" : "blue";
                this.ctx_lines.stroke();

                xAtual = xNovo;
                yAtual = yNovo;
            }
        }

    }
}

var obj_terminal_gcode = new terminal_gcode();
function get_inputfield_data() {
    var message = obj_terminal_gcode.get_inputfield_data()
    return message
};
eel.expose(get_inputfield_data);






























