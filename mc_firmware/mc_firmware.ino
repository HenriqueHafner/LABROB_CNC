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


//Config
int step_min_interv = 5;
int step_max_interv = 100;
int step_curr_interv = 50;

unsigned int serial_bytes_in_buffer = 0;

int trimpot_1 = 512;

bool dir_state[]  = { LOW, LOW, LOW };
bool step_state[] = { LOW, LOW, LOW };
int  dir_pins[]   = { dir_pin_x,  dir_pin_y,  dir_pin_z };
int  step_pins[]  = { step_pin_x, step_pin_y, step_pin_z};
bool led_state = LOW;

String message;
int message_len = 0;
char message_axis;
char message_signal;
String message_steps;

unsigned long steps_todo = 0;
int pin_to_step = step_pin_x;
unsigned long step_last_timestamp = 0;

int get_axisid_from_char(char message_piece) {
  int axis_id;
  if      (message_piece=='x'){ axis_id = 0; }
  else if (message_piece=='y'){ axis_id = 1; }
  else if (message_piece=='z'){ axis_id = 2; }
  return axis_id;}

int get_dir_from_char(char message_piece){
  bool dir;
  if      (message_piece=='+'){ 
  dir = HIGH;
  }
  else if (message_piece=='-'){ dir = LOW; }
  return dir;}

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
  step_state[axis_index] = pin_state;}

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
  step_idle_update();
  serial_bytes_in_buffer = Serial.available();
  if (serial_bytes_in_buffer > 0) {
    message = Serial.readStringUntil('\n');
    message_axis = message[0];
    message_signal = message[1];
    message_len = message.length();
    String message_steps = message.substring(2,message_len);
    long int steps = message_steps.toInt();
    Serial.print(" Axis:");
    Serial.print(message_axis);
    Serial.print(" Dir:");
    Serial.print(message_signal);
    Serial.print(" Total Steps:");
    Serial.print(steps);
    Serial.print("\n");
    move_steps(get_axisid_from_char(message_axis), get_dir_from_char(message_signal), steps);
  }
  }