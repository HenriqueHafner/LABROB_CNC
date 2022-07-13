// Define stepper motor connections:
#define dir_pin_x 2
#define step_pin_x 3
#define dir_pin_y 6
#define step_pin_y 7
#define enable_pin 8
#define led_pin 13
#define analog_pot_1 A1 


bool dir_state_x = HIGH;
bool step_state_x = LOW;
bool dir_state_y = HIGH;
bool step_state_y = LOW;
bool led_state = LOW;

unsigned long steps_todo = 0;
int pin_to_step = step_pin_x;
unsigned long step_last_timestamp = 0;

int step_min_interv = 35;
int step_max_interv = 100;
int step_curr_interv = (step_max_interv-step_min_interv)/2;
unsigned int serial_bytes_in_buffer = 0;

int trimpot_1 = 100;
byte command_1[4];
byte command_2[4];
String message;
char message_axis = "x";
char message_signal = "+";
String message_steps;


void setup() {
  // Declare pins as output:
  pinMode(enable_pin, OUTPUT);
  pinMode(dir_pin_x, OUTPUT);
  pinMode(step_pin_x, OUTPUT);
  pinMode(dir_pin_y, OUTPUT);
  pinMode(step_pin_y, OUTPUT);
  pinMode(led_pin, OUTPUT);
  digitalWrite(dir_pin_x, dir_state_x);
  digitalWrite(step_pin_x, step_state_x);
  digitalWrite(dir_pin_y, dir_state_y);
  digitalWrite(step_pin_y, step_state_y);
  digitalWrite(enable_pin, HIGH);
  Serial.begin(9600);
  delay(2000);
}

void loop() {
delay(10);
serial_bytes_in_buffer = Serial.available();
if (serial_bytes_in_buffer > 0) {
message = Serial.readStringUntil("\n");
message_axis = message[0];
message_signal = message[1];
message_steps = message.substring(2,-1);
long int steps = message_steps.toInt(); 
}
/*
if (serial_bytes_in_buffer >= 4 ){
  Serial.readBytes(command_1,min(serial_bytes_in_buffer,4));
  delay(1000);}
*/
trimpot_1 = 1025-analogRead(A1);
step_curr_interv = map(trimpot_1,1,1023,step_min_interv,step_max_interv);

//executing steps
steps_todo = 0;
while(steps_todo > 0) {
  step_state_x = !step_state_x;
  digitalWrite(step_pin_x, step_state_x);
  delayMicroseconds(step_curr_interv);
  steps_todo = steps_todo-1;
}

}
