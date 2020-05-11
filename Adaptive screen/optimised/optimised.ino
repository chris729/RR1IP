// Import the libraries
#include "Wire.h"
#include "Adafruit_AS726x.h"
#include "Adafruit_MCP4725.h"
     
// Define constants
#define TCAADDR 0x70
#define DAC_RESOLUTION 8
#define DAC_MAX 3000
#define MIN_LIGHT 350
#define SCALE 1.2
#define CONSTANT 100
#define TOP 0
#define ANGLE 1
#define INT_TIME 50

//create the object for the sensors and DAC
Adafruit_AS726x sensor;
Adafruit_MCP4725 dac;

// function which selects the sensor through the multiplexer
void tcaselect(uint8_t i) {
  if (i > 7) return;
  Wire.beginTransmission(TCAADDR);
  Wire.write(1 << i);
  Wire.endTransmission();  
}
     
// Arduino setup, runs once when power on
void setup()
{
  // begins serial communication for testing, and wire for I2C
  while (!Serial);
  delay(200);
  Wire.begin();
  Serial.begin(9600);

  // Connect to first sensor
  Serial.println("Connecting to TOP sensor");
  tcaselect(TOP);
  Serial.println("Setting up TOP sensor");
  if(!sensor.begin()){
    Serial.println("Check your wiring for sensor");
    while(1);
  }
  Serial.println("TOP sensor connected");
  
  // Turn indication LED off and tell the sensor to start 
  sensor.indicateLED(false);
  sensor.setConversionType(MODE_0);
  sensor.setIntegrationTime(INT_TIME);
  
  // Connect to second sensor
  Serial.println("Connecting to ANGLE sensor");
  tcaselect(ANGLE);
  Serial.println("Setting up ANGLE sensor");
  if(!sensor.begin()){
    Serial.println("Check your wiring for sensor");
    while(1);
  }
  Serial.println("ANGLE sensor connected");
  
  // Turn indication LED off and tell the sensor to start 
  sensor.indicateLED(false);
  sensor.setConversionType(MODE_0);
  sensor.setIntegrationTime(INT_TIME);
  
  // begin DAC
  dac.begin(0x62);
  Serial.println("setup done");

  cli(); // turn off interupts
  TCCR1A = 0;// set entire TCCR1A register to 0
  TCCR1B = 0;// same for TCCR1B
  TCNT1  = 0;//initialize counter value to 0
  // set compare match register for 14.3hz (int time of 50) increments
  OCR1A = 818; // = ( 12 *10^6) / ( 14.3 *1024) - 1 (must be <65536)
  // turn on CTC mode
  TCCR1B |= (1 << WGM12);
  // Set CS10 and CS12 bits for 1024 prescaler
  TCCR1B |= (1 << CS12) | (1 << CS10);  
  // enable timer compare interrupt
  TIMSK1 |= (1 << OCIE1A);
  sei();//allow interrupts
}

uint16_t angle_light = 0;
uint16_t top_light = 0;
uint16_t prev_top_light = 0;
uint16_t prev_angle_light = 0;
uint16_t weighted_light = 0;
uint16_t vout = 0;
bool flag = 0;
char sen_flag = 1;

ISR(TIMER1_COMPA_vect){ //timer1 interrupt 9.8Hz 
  flag = !flag;
  if(flag)  sen_flag = 1;
  if(!flag) sen_flag = 2; 
}

void loop() {
  // if timer says top sensor (sen_flag = 1) is ready read it
  if(sen_flag == 1){
    tcaselect(TOP);
    top_light = sensor.readYellow();
    sen_flag = 0;
  }
  // if timer says angle sensor (sen_flag = 2) is ready read it
  if(sen_flag == 2){
    tcaselect(ANGLE);
    angle_light = sensor.readYellow();
    sen_flag = 0;
  }

  // if either the angle light or the top light changes, update the
  //  weighted light and vout. Only bother printing anything if changes happen
  
  if((angle_light != prev_angle_light) || (top_light != prev_top_light)){
    Serial.print("TOP Sensor: ");
    Serial.println(top_light);
    Serial.print("ANGLE Sensor: ");
    Serial.println(angle_light);
    
    // Now calculate vout if light values change, 
    // can tune ratio values 20/80 for now
    weighted_light = 0.2*top_light + 0.8*angle_light;
    vout = SCALE*weighted_light + CONSTANT;
  
    if (vout > DAC_MAX) vout = DAC_MAX;
    else if (vout < MIN_LIGHT) vout = MIN_LIGHT;

    Serial.print("Vout:");
    Serial.println(vout);
  
    // finally output DAC voltage
    dac.setVoltage(vout, false);
    prev_angle_light = angle_light;
    prev_top_light = top_light;
  }
  
}
