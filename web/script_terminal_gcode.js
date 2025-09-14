class terminal_gcode {
    constructor() {
        this.id_parent_label = "terminal_gcode";
        this.div_main = document.getElementById("div_".concat(this.id_parent_label));
        this.setup_html_message_console();
        this.setup_html_inputfield();

        this.create_canvas();
        this.create_button();
    }

    setup_html_message_console() {
        this.message_container = document.createElement("div");
        this.message_container.id = "message_container_".concat(this.id_parent_label);
        this.message_container.style.width = "505px";
        this.message_container.style.height = "515px";
        this.message_container.style.backgroundColor = "#ebeeff";
        this.message_container.style.overflowY = "auto";
        this.message_container.style.padding = "10px";
        this.message_container.style.fontFamily = "'Comfortaa', sans-serif";
        this.message_container.style.fontSize = "16px";
        this.message_container.style.color = "#000000";
        this.message_container.style.display = "inline-block";
        this.message_container.style.textAlign = "left";
        this.div_main.appendChild(this.message_container);
        this.message_console_timestamp = Date.now();
        this.message_data = Array(20).fill("");
        setInterval(() => { this.update_messages_window(this); }, 200);
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
        var input_field = this.input_field_html.contentDocument.getElementById("lined_input");
        var str_gcode_message = input_field.value;
        input_field.value = "";
        return str_gcode_message;
    }

    async ell_python_exposed_fun_call(python_call) {
        let return_data = await globalThis.eel.arbitrary_call(python_call)();
        return return_data;
    }

    async setup_interface_buttons() {
        let interface_data = await this.ell_python_exposed_fun_call("buttons_teminal_gcode()");
        var div_buttons = document.createElement("DIV");
        div_buttons.id = "buttons_".concat(this.id_parent_label);
        var obj_scope = this;
       
        for (var button_data_index in interface_data) {
            var label = interface_data[button_data_index][0];
            var call = interface_data[button_data_index][1];
            var button = document.createElement("BUTTON");
            button.call_text = call;
            button.type = "button";
            button.innerHTML = label;
            button.id = label;
            button.onclick = function() { obj_scope.ell_python_exposed_fun_call(this.call_text); };
            div_buttons.appendChild(button);
        }
        this.div_main.appendChild(div_buttons);
    }

    async update_messages_window(instance) {
        if (Array.isArray(instance.message_data)) {
            instance.message_data = await eel.get_last_messages_window()();
            instance.message_data = instance.message_data.slice(0, 20);
            var mw_frequency = Date.now() - instance.message_console_timestamp;
            instance.message_console_timestamp = Date.now();
        }
        let html_content = "";
        for (let i = 0; i < instance.message_data.length; i++) {
            const message = instance.message_data[i] || "";
            html_content += message;
            if (i < instance.message_data.length - 1) {
                html_content += "<br>";
            }
        }
        instance.message_container.innerHTML = html_content;
    }

    create_canvas() {
        this.canvas_lines = document.createElement("canvas");
        this.canvas_lines.id = "canvas_lines_" + this.id_parent_label;
        this.canvas_lines.width = 505;
        this.canvas_lines.height = 515;
        this.canvas_lines.style.backgroundColor = "#ebeeff";
        this.ctx_lines = this.canvas_lines.getContext("2d");
        this.div_main.appendChild(this.canvas_lines);
    }

    create_button() {
        this.button = document.createElement("button");
        this.button.innerText = "Desenhar GCODE";
        this.button.style.display = "block";
        this.button.style.marginTop = "10px";
        this.button.style.margin = "10px auto";
        this.button.onclick = () => this.draw_gcode();
        this.div_main.appendChild(this.button);
    }

    parse_gcode_line(line) {
        // Step 1: Trim leading and trailing whitespace from the line
        line = line.trim();

        // Step 2: Convert the line to uppercase to make parsing case-insensitive
        let upperLine = line.toUpperCase();

        // Step 3: Check if the line starts with 'G00' or 'G01' (G must be first)
        let command = null;
        if (upperLine.startsWith('G00')) {
            command = 'G00';
            upperLine = upperLine.substring(3).trim();
        } else if (upperLine.startsWith('G01')) {
            command = 'G01';
            upperLine = upperLine.substring(3).trim();
        } else {
            // Invalid G command - ignore line
            return null;
        }

        // Step 3.5: Define variables for anchor indices and string values
        let xIndex = upperLine.indexOf('X');
        let yIndex = upperLine.indexOf('Y');
        let x_string_value = '';
        let y_string_value = '';

        // Step 4: Extract raw x_string_value using xIndex
        if (xIndex !== -1) {
            // Determine the end of the X value substring
            let xEnd;
            if (yIndex !== -1 && yIndex > xIndex) {
                // Y anchor exists and comes after X, so end at yIndex
                xEnd = yIndex;
            } else {
                // No Y anchor or Y before X, so end at the string length
                xEnd = upperLine.length;
            }
            // Extract the substring after 'X' up to xEnd
            x_string_value = upperLine.substring(xIndex + 1, xEnd);
        }

        // Step 5: Extract raw y_string_value using yIndex
        if (yIndex !== -1) {
            // Determine the end of the Y value substring
            let yEnd;
            if (xIndex !== -1 && xIndex > yIndex) {
                // X anchor exists and comes after Y, so end at xIndex
                yEnd = xIndex;
            } else {
                // No X anchor or X before Y, so end at the string length
                yEnd = upperLine.length;
            }
            // Extract the substring after 'Y' up to yEnd
            y_string_value = upperLine.substring(yIndex + 1, yEnd);
        }

        // Step 6: Filter x_string_value to allow only valid characters
        if (x_string_value) {
            let filteredX = '';
            for (let char of x_string_value) {
                if (['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'].includes(char)) {
                    filteredX += char;
                }
            }
            x_string_value = filteredX; // Redefine with filtered value
        }

        // Step 7: Filter y_string_value to allow only valid characters
        if (y_string_value) {
            let filteredY = '';
            for (let char of y_string_value) {
                if (['-', '+', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.'].includes(char)) {
                    filteredY += char;
                }
            }
            y_string_value = filteredY; // Redefine with filtered value
        }

        // Step 8: Define dx and dy with default values
        let dx = 0.0; // Default if X absent or invalid
        let dy = 0.0; // Default if Y absent or invalid

        // Step 9: Parse x_string_value to float for dx
        if (x_string_value) {
            let parsedX = parseFloat(x_string_value);
            if (isNaN(parsedX)) {
                // Invalid X value - ignore the entire line
                return null;
            }
            dx = parsedX;
        }

        // Step 10: Parse y_string_value to float for dy
        if (y_string_value) {
            let parsedY = parseFloat(y_string_value);
            if (isNaN(parsedY)) {
                // Invalid Y value - ignore the entire line
                return null;
            }
            dy = parsedY;
        }

        // Step 11: Return the parsed command and deltas
        return {
            command: command,
            dx: dx,
            dy: dy
        };
    }

    draw_axes() {
        // Save the current context state to restore later
        this.ctx_lines.save();

        // Set style for axes: thin gray lines
        this.ctx_lines.strokeStyle = "gray";
        this.ctx_lines.lineWidth = 0.5;

        // Draw X-axis (horizontal line through center)
        this.ctx_lines.beginPath();
        this.ctx_lines.moveTo(-this.canvas_lines.width / 2, 0);
        this.ctx_lines.lineTo(this.canvas_lines.width / 2, 0);
        this.ctx_lines.stroke();

        // Draw Y-axis (vertical line through center)
        this.ctx_lines.beginPath();
        this.ctx_lines.moveTo(0, -this.canvas_lines.height / 2);
        this.ctx_lines.lineTo(0, this.canvas_lines.height / 2);
        this.ctx_lines.stroke();

        // Set font for tick labels
        this.ctx_lines.font = "10px sans-serif";
        this.ctx_lines.fillStyle = "gray";
        this.ctx_lines.textAlign = "center";
        this.ctx_lines.textBaseline = "middle";

        // Draw ticks and labels for X-axis (every 50 mm)
        const tickSize = 5; // Length of tick marks
        const xStart = Math.ceil(-this.canvas_lines.width / 2 / 50) * 50;
        const xEnd = Math.floor(this.canvas_lines.width / 2 / 50) * 50;
        for (let x = xStart; x <= xEnd; x += 50) {
            if (x === 0) continue; // Skip origin to avoid overlap
            // Draw tick
            this.ctx_lines.beginPath();
            this.ctx_lines.moveTo(x, -tickSize);
            this.ctx_lines.lineTo(x, tickSize);
            this.ctx_lines.stroke();
            // Draw label below the axis
            this.ctx_lines.fillText(x.toString(), x, tickSize + 10);
        }

        // Draw ticks and labels for Y-axis (every 50 mm)
        const yStart = Math.ceil(-this.canvas_lines.height / 2 / 50) * 50;
        const yEnd = Math.floor(this.canvas_lines.height / 2 / 50) * 50;
        for (let y = yStart; y <= yEnd; y += 50) {
            if (y === 0) continue; // Skip origin
            // Draw tick
            this.ctx_lines.beginPath();
            this.ctx_lines.moveTo(-tickSize, y);
            this.ctx_lines.lineTo(tickSize, y);
            this.ctx_lines.stroke();
            // Draw label to the left of the axis
            this.ctx_lines.fillText(y.toString(), -tickSize - 10, y);
        }

        // Restore the context state
        this.ctx_lines.restore();
    }

    draw_gcode() {
        // Step 1: Reset the transformation matrix to identity
        this.ctx_lines.setTransform(1, 0, 0, 1, 0, 0);

        // Step 2: Clear the entire canvas area
        this.ctx_lines.clearRect(0, 0, this.canvas_lines.width, this.canvas_lines.height);

        // Step 3: Translate to the center of the canvas for centered drawing
        this.ctx_lines.translate(this.canvas_lines.width / 2, this.canvas_lines.height / 2);

        // Step 4: Apply scale (currently 1:1, but can be adjusted later)
        this.ctx_lines.scale(1, 1);

        // Step 5: Draw the X and Y axes with ticks
        this.draw_axes();

        // Step 6: Get the input text from the field
        let input_text = this.input_field_html.contentDocument.getElementById("lined_input");
        let str_gcode_message = input_text.value;

        // Step 7: Split the input into individual lines
        let linhas = str_gcode_message.split("\n");

        // Step 8: Initialize current position
        let xAtual = 0;
        let yAtual = 0;
        let xNovo = 0;
        let yNovo = 0;

        // Step 9: Process each line using parse_gcode_line
        for (let i = 0; i < linhas.length; i++) {
            let linha = linhas[i];

            // Parse the line using the robust parser
            let parsed = this.parse_gcode_line(linha);

            // If parsing failed or invalid, skip to the next line
            if (parsed === null) {
                continue;
            }

            // Calculate new position based on deltas (assuming relative as in original)
            xNovo = xAtual + parsed.dx;
            yNovo = yAtual + parsed.dy;

            // Set line style based on command
            this.ctx_lines.strokeStyle = parsed.command === "G00" ? "red" : "blue";

            // Draw the line from current to new position
            this.ctx_lines.beginPath();
            this.ctx_lines.moveTo(xAtual, yAtual);
            this.ctx_lines.lineTo(xNovo, yNovo);
            this.ctx_lines.stroke();

            // Update current position for the next line
            xAtual = xNovo;
            yAtual = yNovo;
        }
    }
}

var obj_terminal_gcode = new terminal_gcode();
function get_inputfield_data() {
    var message = obj_terminal_gcode.get_inputfield_data();
    return message;
}
eel.expose(get_inputfield_data);