#include "Arduino.h"

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
int step_min_interv = 5;
int step_max_interv = 100;
int step_curr_interv = 50;
unsigned int serial_bytes_in_buffer = 0;
int trimpot_1 = 512;

  //movement
unsigned int steps_multiplicator = 1;
bool dir_state[]  = { LOW, LOW, LOW };
bool step_state[] = { LOW, LOW, LOW };
int  dir_pins[]   = { dir_pin_x,  dir_pin_y,  dir_pin_z };
int  step_pins[]  = { step_pin_x, step_pin_y, step_pin_z};
bool led_state = LOW;

  //communication
bool gcode_block_sended = false;
char raw_message[257];

int message_len = 0;
char message_steps[10];
char message_axis;
char message_signal;
unsigned int steps_todo = 0;
int pin_to_step = step_pin_x;
unsigned long step_last_timestamp = 0;



void setup() {
  // Declare pins as output:
  pinMode(enable_pin, OUTPUT);
  pinMode(dir_pin_x, OUTPUT);
  pinMode(step_pin_x, OUTPUT);
  pinMode(dir_pin_y, OUTPUT);
  pinMode(step_pin_y, OUTPUT);
  pinMode(led_pin, OUTPUT);
  digitalWrite(enable_pin, HIGH);
  Serial.begin(9600);
  delay(2000);
  Serial.print("CNC Controller Interface: Online");
}


void loop() {
  delay(10);
  // step_idle_update();
  String message = serial_incoming_message_parser();

    // message_axis = message[0];
    // message_signal = message[1];
    // message_len = message.length();
    // message_steps = message.substring(2,message_len);
    
    // axis  = get_axisid_from_char(message_axis)
    // direc = get_dir_from_char(message_signal)
    // steps = get_steps_from_message(message_signal)

    // Serial.print(" Axis:");
    // Serial.print(message_axis);
    // Serial.print(" Dir:");
    // Serial.print(message_signal);
    // Serial.print(" Total Steps:");
    // Serial.print(steps);
    // Serial.print("\n");

    // move_steps(get_axisid_from_char(message_axis), get_dir_from_char(message_signal), );
}

  // ##################### Global Methods - Begin #####################
  
bool isUnsignedInt(String input) {
  for (int i = 0; i < input.length(); i++) {
    if (!isDigit(input[i])) {
      return false;
    }
  }
  return true;
}

int get_axisid_from_char(char message_piece) {
  int axis_id;
  if      (message_piece=='x') {
    axis_id = 0; }
  else if (message_piece=='y') {
    axis_id = 1; }
  else if (message_piece=='z') {
    axis_id = 2;
  } else {
    Serial.println("Failed to find a valid axis in message.");
    axis_id = -1; 
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
    dir = 1;   
    }
  return dir;
  }

unsigned int get_steps_from_char(String message_piece) {
  if (isUnsignedInt(message_piece)) {
    unsigned int steps = message_piece.toInt();
    return steps;
  } else {
    return 0;
  }
  }

bool check_inputs(int input1, int input2, int input3) {
  if (input1 == -1 || input2 == -1 || input3 == -1) {
    return true;
  } else {
    return false;
  }
}
//
//String remove_consecutive_spaces_in_message(String raw_str) {
//  char message_new[strlen(raw_str)];
//  char char_to_check;
//  int j = 0;
//  for (int i = 0; i < strlen(raw_str); i++) {
//    if (raw_str[i] == char_to_check && raw_str[i + 1] == char_to_check) {
//      continue;
//    }
//    message_new[j++] = str1[i];
//  }
//  message_new[j] = '\0';
//  return message_new;
//}

bool message_decode() {
  return true;
}

void step_idle_update(bool debug=true) {
  trimpot_1 = 1025-analogRead(analog_pot_1);
  step_curr_interv = map(trimpot_1,1,1023,step_min_interv,step_max_interv);
  if (debug==true){
    Serial.print("step_curr_interv: ");
    Serial.print(step_curr_interv);
    Serial.print("\n");
    }
}

void move_steps(int axis_index, bool dir,  long int steps_number, bool debug=true) {
  int  pin_dir    = dir_pins[axis_index];
  int  pin_step   = step_pins[axis_index];
  bool pin_state  = step_state[axis_index];
  digitalWrite(pin_dir, dir);
  delayMicroseconds(5);
  Serial.println(dir);
  while(steps_number > 0) {
    pin_state = !pin_state;
    digitalWrite(pin_step, pin_state);
    delayMicroseconds(step_curr_interv);
    steps_number = steps_number-1;
    if (debug==true){
    Serial.print(" Step: ");
    Serial.print(steps_number);
    Serial.print(" Pin: ");
    Serial.print(pin_step);
    Serial.print(" S: ");
    Serial.println(pin_state);
    delay(250);
    }
  }
  step_state[axis_index] = pin_state;
}

String serial_incoming_message_parser() {
  String message;
  String empty_char = "0";
  serial_bytes_in_buffer = Serial.available();
  if (serial_bytes_in_buffer > 0) {
    message = Serial.readStringUntil('\n');
    Serial.println("message recieve");
    return message;
  }
  return empty_char;
}
  
//##################### Global Methods - End #####################
