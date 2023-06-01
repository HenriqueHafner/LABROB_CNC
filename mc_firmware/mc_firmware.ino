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
bool step_state[] = { LOW, LOW, LOW };
int  dir_pins[]   = { dir_pin_x,  dir_pin_y,  dir_pin_z };
int  step_pins[]  = { step_pin_x, step_pin_y, step_pin_z};
bool dir_state[]  = { LOW, LOW, LOW };
int steps_goal[]               = { 0,  0,  0 };
int steps_done[]               = { 0,  0,  0 };
int steps_remainning[]         = { 0,  0,  0 };
float steps_tangent_relation[] = { 0,  0,  0 };
float steps_goal_distance[]    = { 0,  0,  0 };
int axis_carrier  = 0;
bool should_step[] = { false, false, false};

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
  digitalWrite(enable_pin, LOW);
  // Serial
  Serial.begin(9600);
  delay(2000);
  Serial.println("CNC Controller Interface: Online");
  // Testing
}


void loop() { 
  serial_incoming_message_parser();
  print_order_state();
  step_handler();
  delay(0);
}

  // ##################### Global Methods - Begin #####################
  
bool isUnsignedInt(String input) {
  for (unsigned int i = 0; i < input.length(); i++) {
    if (!isDigit(input[i])) {
      return false;
    }
  }
  return true;
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

int get_steps_from_string(String message_i, int start_i, int end_i) {
  if (start_i <= end_i) {
    String message_piece = message_i.substring(start_i, end_i+1);
    int steps;
    if (isUnsignedInt(message_piece)) {
      steps = message_piece.toInt();
      if (steps>0) {
        return steps;
      } else {
      Serial.println("Steps order overflow");
      }
    }
  }
  return -1;
}


void set_steps_to_do(int axis_id, int dir_i, int steps_i){
  digitalWrite(dir_pin_x, dir_i);
  dir_state[axis_id]  = dir_i;
  steps_goal[axis_id] = steps_i;
}

bool check_inputs(int input1, int input2, int input3) {
  if ((input1 == -1) || (input2 == -1) || (input3 == -1) ) {
    return true;
  } else {
    return false;
  }
}

bool message_decode(String message_i) {
  int i_max =  message_i.length();
  int i = 0;
  int axis  = -1;
  int dir   = -1;
  int string_steps_start = -1;
  int string_steps_end = -1;
  int steps = -1;
  while (i <= i_max-2 ) {
    // get axis, dir and steps from a order
    if ( (isAlpha(message_i.charAt(i))) ) {
      axis = get_axisid_from_char(message_i.charAt(i));
      dir  = get_dir_from_char(message_i.charAt(i+1));
      i = i+2;
      string_steps_start = i;
      while ( (i <  i_max) && (isDigit(message_i.charAt(i+1))) ) {
        i = i+1;
      }
      string_steps_end = i;
    steps = get_steps_from_string(message_i, string_steps_start, string_steps_end);
    }
    //check message health
    bool message_corrupted_flag = check_inputs(axis, dir, steps);
    if (message_corrupted_flag) {
      Serial.print("Failed to decode message: ");
      Serial.println(message_i);
      Serial.println(axis);
      Serial.println(dir);
      Serial.println(steps);
      return false;
    } else {
      set_steps_to_do(axis, dir, steps);
      axis  = -1;
      dir   = -1;
      string_steps_start = -1;
      string_steps_end = -1;
      steps = -1;
    }
  i = i + 1; //keep searching for other order in message
  }
  setup_steps_planning();
  return true;
}

void indle_interval_update(bool debug=false) {
  trimpot_1 = 1025-analogRead(analog_pot_1);
  step_curr_interv = map(trimpot_1,1,1023,step_min_interv,step_max_interv);
  if (debug==true){
    Serial.print("step_curr_interv: ");
    Serial.print(step_curr_interv);
    Serial.print("\n");
    }
}

void setup_steps_planning() {
  set_inital_values();
  set_axis_carrier();
  set_carrier_tangent_relation();
  set_steps_remainning();
}

void set_inital_values() {
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_done[axis_i] = 0;
  }
}

void set_axis_carrier() {
  int biggest_steps = 0;
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    if (steps_goal[axis_i] > biggest_steps) {
      biggest_steps = steps_goal[axis_i];
      axis_carrier  = axis_i;
    }
  }
}

void set_carrier_tangent_relation() {
  float maximum_goal = steps_goal[axis_carrier];
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_tangent_relation[axis_i] = steps_goal[axis_i]/maximum_goal;
  }
}

void set_steps_remainning() {
  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
  steps_remainning[axis_i] = steps_goal[axis_i] - steps_done[axis_i];
  }
}

bool step_handler() {
  if ( millis() - step_last_timestamp <= step_curr_interv ) {
    return true;
  }

  for ( int axis_i = 0 ; axis_i<3 ; axis_i++) {
    steps_goal_distance[axis_i] = (steps_tangent_relation[axis_i])*(1+steps_done[axis_carrier]) - steps_done[axis_i];
    should_step[axis_i] = ( (steps_remainning[axis_i] > 0) && ( steps_goal_distance[axis_i] >= 1 ) );
    if (should_step[axis_i] && able_to_step) {
      step_axis(axis_i);
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

bool serial_incoming_message_parser() {
  String message;
  String idle = "Idle";
  serial_bytes_in_buffer = Serial.available();
  if (serial_bytes_in_buffer > 0) {
    message = Serial.readStringUntil('\n');

    serial_bytes_in_buffer = Serial.available();
    Serial.print("B01 ");
    Serial.print(serial_bytes_in_buffer);
    Serial.print('\n');
    bool decode_flag = message_decode(message);
    return decode_flag;
  }
  return false;
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
    Serial.print("SG:");
    Serial.print(steps_goal_distance[axis_i]);
    Serial.print("SD:");
    Serial.print(steps_done[axis_i]);
    Serial.print('|');
  }
  Serial.print("]\n");
}

//##################### Global Methods - End #####################
