
function view_container_create(id_parent_label) {
    try {
        div_main = document.getElementById("dashboard_div");
        div_to_add = document.createElement("DIV");
        div_to_add.id = "div_".concat(id_parent_label);
        // div_to_add.style.width = 502;

    //Title
        title_para = document.createElement("H2");
        pretty_title_text = id_parent_label.replaceAll("_", " ")
        pretty_title_text = pretty_title_text.replace(pretty_title_text[0], pretty_title_text[0].toUpperCase())
        title_text = document.createTextNode(pretty_title_text);
        title_para.appendChild(title_text);    
        div_to_add.appendChild(title_para);     

    //JavaScript Load
        script_injection = document.createElement('script');
        script_injection.setAttribute("type","text/javascript");
        script_filename = "script_".concat(id_parent_label)
        script_filename = script_filename.concat(".js")
        script_injection.setAttribute("src", script_filename);

        div_to_add.appendChild(script_injection);  
        div_main.appendChild(div_to_add);
        return(true)
    }
    catch(catched_error) {
        console.log("Failed creating: ", id_parent_label)
        console.log(catched_error)
        return(false)
    }

}

//Main Routine

//view_container_create("empty_tester")
view_container_create("terminal_gcode")
//view_container_create("monitor_machine")




