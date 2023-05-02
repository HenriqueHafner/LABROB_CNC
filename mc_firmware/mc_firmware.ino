// Define stepper motor connections:
#define dir_pin_x 2
#define dir_pin_y 6
#define dir_pin_z 10
#define step_pin_x 3
#define step_pin_y 7
#define step_pin_z 11
#define enable_pin 8
#define led_pin 13
#define analog_pot_1 A1

//Global Variables
  //machine
int step_min_interv = 0;
int step_max_interv = 100;
int step_curr_interv = 0;
unsigned int serial_bytes_in_buffer = 0;
int trimpot_1 = 512;

  //movement
bool able_to_step = true;
bool motion_idle = true;
bool step_state[] = { LOW, LOW, LOW };
int  dir_pins[]   = { dir_pin_x,  dir_pin_y,  dir_pin_z };
int  step_pins[]  = { step_pin_x, step_pin_y, step_pin_z};
bool dir_state[]  = { LOW, LOW, LOW };
unsigned int   steps_target[]        = { 0,  0,  0 };
unsigned int   steps_done[]          = { 0,  0,  0 };
unsigned int   steps_remainning[]    = { 0,  0,  0 };
float steps_fraction_residue[] = { 0,  0,  0 };
float steps_tangent_relation[] = { 0,  0,  0 };
int axis_carrier  = 0;
bool should_step[] = { false, false, false };

  //communication
String message;
bool message_corrupted = false;
bool message_processed = false;
bool led_state = LOW;
unsigned long step_last_timestamp = 0;
unsigned long monitor_last_timestamp = 0;

void setup() {
  // Declare pins as output:
  pinMode(enable_pin, OUTPUT);
  pinMode(dir_pin_x, OUTPUT);
  pinMode(step_pin_x, OUTPUT);
  pinMode(dir_pin_y, OUTPUT);
  pinMode(step_pin_y, OUTPUT);
  pinMode(dir_pin_z, OUTPUT);
  pinMode(step_pin_z, OUTPUT);
  pinMode(led_pin, OUTPUT);
  digitalWrite(enable_pin, HIGH);
  // Serial
  Serial.begin(9600);
  delay(2000);
  Serial.println("CNC Controller Interface: Online");
  // Testing
}


void loop() { 
  serial_incoming_message_parser();
  //print_order_state();
  print_machine_status();
  step_handler();
  delay(10);
}

// ##################### Global Methods - Begin #####################

  // communication messages processing 

bool message_decode(String message_i) {
  int i_max =  message_i.length();
  int i = 0;
  set_zero_steps_target();
  while (i <= i_max-2 ) {
    // get axis, dir and steps from a order
    if ( (isAlpha(message_i.charAt(i))) ) {
      int axis = get_axisid_from_char(message_i.charAt(i));
      int dir  = get_dir_from_char(message_i.charAt(i+1));
      int string_steps_start = i+2;
      i = string_steps_start;
      while ( (i+1 <= i_max) && (isDigit(message_i.charAt(i+1))) ) {
        i = i+1;
      }
      int string_steps_end = i;
      unsigned int steps = get_steps_from_string(message_i, string_steps_start, string_steps_end);
      //check message health
      bool message_health_flag = check_inputs(axis, dir, steps);
      if (!message_health_flag) {
        Serial.print("Failed to decode message: ");
        Serial.println(message_i);
        Serial.println(axis);
        Serial.println(dir);
        Serial.println(steps);
        return false;
      } else {
        //set the command from this piece
        set_steps_target(axis, dir, steps);
      }
    }
  i = i + 1; //keep searching for other order in message
  }
  setup_steps_planning();
  return true;
}

bool check_String_is_unsigned_int(String input) {
  bool is_UI_flag = true;
  int input_length = input.length();
  if (input_length <= 0) {
    is_UI_flag = false;
    Serial.print("Input steps length error.");
  }
  if (input_length > 5) {
    is_UI_flag = false;
    Serial.print("Input steps length overflow.");
  }
  if (input_length == 5) {
    String high_3_digits_text = input.substring(0,3);
    int high_3_digits = high_3_digits_text.toInt();
    if (high_3_digits > 654) {
      is_UI_flag = false;
      Serial.print("Input steps value overflow: ");
      Serial.println(high_3_digits);
    }
  }
  for (unsigned int i = 0; i < input_length; i++) {
    if (!isDigit(input[i])) {
      Serial.print("Input steps has non digit char");
      is_UI_flag = false;
    }
  }
  return is_UI_flag;
}

unsigned int String_to_unsigned_int(String input) {
  unsigned int error_value = 0;
  unsigned int sum_value = 0;
  int input_length = input.length();
  if (!check_String_is_unsigned_int(input)){
    return error_value;
  }
  char char_i = '0';
  int  digit_i = 0;
  int decimal_power_i = 0;
  decimal_power_i = max(0,  input_length-1);
  decimal_power_i = min(4, decimal_power_i);

  for (unsigned int i = 0; i < input_length; i++) {
   char_i = input.charAt(i);
   digit_i = char_i-'0';
   sum_value += digit_i*int_pow_10_limited(decimal_power_i);
   decimal_power_i--;
  }
  return sum_value;
}

int int_pow_10_limited(int x) {
    static const int powers[] = {1, 10, 100, 1000, 10000, 100000};
    return powers[x];
}

int get_axisid_from_char(char message_piece) {
  int axis_id;
  if      (message_piece=='X' or message_piece=='x') {
    axis_id = 0; }
  else if (message_piece=='Y' or message_piece=='y') {
    axis_id = 1;}
  else if (message_piece=='Z' or message_piece=='z') {
    axis_id = 2;
  } else {
    Serial.print("Invalid axis in message: ");
    Serial.print(message_piece);
    Serial.print('\n');
    return -1;
    }
  return axis_id;
  }

int get_dir_from_char(char message_piece){
  bool dir;
  if      (message_piece=='+') {
    dir = 1;   
  }
  else if (message_piece=='-') {
    dir = 0;
  } else {
    Serial.print("Invalid +/- direction in message: ");
    Serial.print(message_piece);
    Serial.print('\n');
    dir = -1;   
    }
  return dir;
  }

unsigned int get_steps_from_string(String message_i, int start_i, int end_i) {
  unsigned int steps = 0;
  if (start_i <= end_i) {
    String message_piece = message_i.substring(start_i, end_i+1);
    steps = String_to_unsigned_int(message_piece);
  }
  return steps;
}

 // Motion planning 

void set_steps_target(int axis_id, int dir_i, unsigned int steps_i){
  dir_state[axis_id]  = dir_i;
  digitalWrite(dir_pins[axis_id], dir_i);
  steps_target[axis_id] = steps_i;
}

bool check_inputs(int axis_id, int dir_i, unsigned int steps_i) {
  bool input_ok_flag = true;
  if (axis_id < 0 || axis_id > 2 )  {
    input_ok_flag = false;
  }
  if (dir_i < 0 || dir_i > 1) {
    input_ok_flag = false;
  }
  if (steps_i <= 0) {
    input_ok_flag = false;
  }
  return input_ok_flag;
}

void idle_interval_update(bool debug=false) {
  trimpot_1 = 1025-analogRead(analog_pot_1);
  step_curr_interv = map(trimpot_1,1,1023,step_min_interv,step_max_interv);
  if (debug==true){
    Serial.print("step_curr_interv: ");
    Serial.print(step_curr_interv);
    Serial.print("\n");
    }
}

void setup_steps_planning() {
  set_zero_steps_done();
  set_axis_carrier();
  set_carrier_tangent_relation();
  set_steps_remainning();
}

void set_zero_steps_done() {
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_done[axis_i] = 0;
  }
}

void set_zero_steps_target() {
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_target[axis_i] = 0;
  }
}

void set_axis_carrier() {
  int biggest_steps = 0;
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    if (steps_target[axis_i] > biggest_steps) {
      biggest_steps = steps_target[axis_i];
      axis_carrier  = axis_i;
    }
  }
}

void set_carrier_tangent_relation() {
  float maximum_goal = steps_target[axis_carrier];
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_tangent_relation[axis_i] = steps_target[axis_i]/maximum_goal;
  }
}

void set_steps_remainning() {
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
  steps_remainning[axis_i] = steps_target[axis_i] - steps_done[axis_i];
  }
}

bool step_handler() {
  if ( millis() - step_last_timestamp <= step_curr_interv ) {
    return true;
  }
  motion_idle = true;
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_fraction_residue[axis_i] = (steps_tangent_relation[axis_i])*(1+steps_done[axis_carrier]) - steps_done[axis_i];
    should_step[axis_i] = ( (steps_remainning[axis_i] > 0) && ( steps_fraction_residue[axis_i] >= 1 ) );
    if (should_step[axis_i] && able_to_step) {
      step_axis(axis_i);
      motion_idle = false;
    }
  }
  step_last_timestamp = millis();
  return true;
}

void step_axis(int axis_i) {
  digitalWrite(step_pins[axis_i],!step_state[axis_i]);
  step_state[axis_i] = !step_state[axis_i];
  steps_done[axis_i]++ ;
  steps_remainning[axis_i]-- ;
}

void serial_incoming_message_parser() {
  if (motion_idle != true){
    return;
  }
  serial_bytes_in_buffer = Serial.available();
  if (serial_bytes_in_buffer > 0) {
    message = Serial.readStringUntil('\n');
    serial_bytes_in_buffer = Serial.available();
    Serial.print("B01 ");
    Serial.print(serial_bytes_in_buffer);
    Serial.print('\n');
    bool decode_flag = message_decode(message);
  }
}

void print_order_state() {
  if (millis() - monitor_last_timestamp <= 1000) {
    return;
  }
  monitor_last_timestamp = millis();
  Serial.print("M[");
  for(int axis_i = 0; axis_i < 3; axis_i++) {
    Serial.print("A:");
    Serial.print(axis_i);
    Serial.print(" SG:");
    Serial.print(steps_fraction_residue[axis_i]);
    Serial.print(" SD:");
    Serial.print(steps_done[axis_i]);
    Serial.print('|');
  }
  Serial.print("SCR: ");
  unsigned int max_steps_remainning = max(steps_remainning[0],  steps_remainning[1]);
  max_steps_remainning =     max(max_steps_remainning, steps_remainning[2]);
  Serial.print(max_steps_remainning);
  Serial.print("]\n");
}

void print_machine_status() {
 if (millis() - monitor_last_timestamp <= 1000) {
   return;
 }
 monitor_last_timestamp = millis();
 if (motion_idle){
  Serial.print("Idle   "); 
 } else {
  Serial.print("Moving "); 
 }
  Serial.print("B01 ");
  Serial.println(Serial.available());
}

//##################### Global Methods - End #####################

