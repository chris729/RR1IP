/**************************************************************************/
/*!
    @file     sinewave.pde
    @author   Adafruit Industries
    @license  BSD (see license.txt)

    This example will generate a sine wave with the MCP4725 DAC.

    This is an example sketch for the Adafruit MCP4725 breakout board
    ----> http://www.adafruit.com/products/935

    Adafruit invests time and resources providing this open source code,
    please support Adafruit and open-source hardware by purchasing
    products from Adafruit!
*/
/**************************************************************************/
#include <Wire.h>
#include <Adafruit_MCP4725.h>
#include "Adafruit_AS726x.h"

//create the object
Adafruit_AS726x ams;

//buffer to hold raw values
uint16_t sensorValues[AS726x_NUM_CHANNELS];

Adafruit_MCP4725 dac;

// Set this value to 9, 8, 7, 6 or 5 to adjust the resolution
#define DAC_RESOLUTION    (8)
#define LIGHT_TARGET_LOW  150
#define LIGHT_TARGET_HIGH  200
#define LIGHT_STEP  40
//#define LIGHT_LOW_LIMIT 0x800

/* Note: If flash space is tight a quarter sine wave is enough
   to generate full sine and cos waves, but some additional
   calculation will be required at each step after the first
   quarter wave.                                              */
uint16_t dac_voltage[10] = {0x7FF, 0x87F, 0x8FF, 0x9FF, 0xAFF, 0xBFF, 0xCFF, 0xDFF, 0xEFF, 0xFFF};
uint16_t light_target[10] = {1*LIGHT_STEP, 2*LIGHT_STEP, 3*LIGHT_STEP, 4*LIGHT_STEP, 5*LIGHT_STEP, 6*LIGHT_STEP, 7*LIGHT_STEP, 8*LIGHT_STEP, 9*LIGHT_STEP, 10*LIGHT_STEP};
uint8_t dac_voltage_index = 0;
   
  
void setup(void) {
  Serial.begin(9600);
  while(!Serial);
  Serial.println("Setup MCP4725");

  // For Adafruit MCP4725A1 the address is 0x62 (default) or 0x63 (ADDR pin tied to VCC)
  // For MCP4725A0 the address is 0x60 or 0x61
  // For MCP4725A2 the address is 0x64 or 0x65
  dac.begin(0x62);

  Serial.println("Setup AS7262");
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  
  //begin and make sure we can talk to the sensor
  if(!ams.begin()){
    Serial.println("could not connect to sensor! Please check your wiring.");
    while(1);
  }
  dac_voltage_index = 0;
}

void loop(void) {
  
 //read the device temperature
  uint8_t temp = ams.readTemperature();
  uint8_t i = 0;

  
  ams.drvOn(); //uncomment this if you want to use the driver LED for readings
  ams.startMeasurement(); //begin a measurement
  
  //wait till data is available
  bool rdy = false;
  while(!rdy){
    
    delay(5);
    rdy = ams.dataReady();
  }
 ams.drvOff(); //uncomment this if you want to use the driver LED for readings

  //read the values!
  ams.readRawValues(sensorValues);
  //ams.readCalibratedValues(calibratedValues);

  Serial.print("Temp: "); Serial.print(temp);
  Serial.print(" Violet: "); Serial.print(sensorValues[AS726x_VIOLET]);
  Serial.print(" Blue: "); Serial.print(sensorValues[AS726x_BLUE]);
  Serial.print(" Green: "); Serial.print(sensorValues[AS726x_GREEN]);
  Serial.print(" Yellow: "); Serial.print(sensorValues[AS726x_YELLOW]);
  Serial.print(" Orange: "); Serial.print(sensorValues[AS726x_ORANGE]);
  Serial.print(" Red: "); Serial.print(sensorValues[AS726x_RED]);
  Serial.println();
  Serial.println();

  if (sensorValues[AS726x_YELLOW] > light_target[0]){
    for (i = 0; i < 9; i++){
      if ((sensorValues[AS726x_YELLOW] > light_target[i]) && (sensorValues[AS726x_YELLOW] < light_target[i+1])){
        break;
      }
    }
  }
//  if (sensorValues[AS726x_YELLOW] < LIGHT_TARGET_LOW){
//    if (dac_voltage_index < 9){
//      dac_voltage_index++;
//    }
//  }else if(sensorValues[AS726x_YELLOW] > LIGHT_TARGET_HIGH){
//    if (dac_voltage_index > 0){
//      dac_voltage_index--;
//    }
//  }
  Serial.print(" dac_voltage: ");Serial.print(9-i);
  Serial.println();
  delay(50);
  double vout = 1*pow(10,-6)*pow(sensorValues[AS726x_YELLOW],3) - 0.0074*pow(sensorValues[AS726x_YELLOW],2) + 14.546*sensorValues[AS726x_YELLOW]-7000;
  if (vout > 4000) {
    vout = 4000;
  }
  else if (vout < 1000){
    vout = 1000;
  }
  dac.setVoltage(int(vout), false);
//  dac.setVoltage(dac_voltage[1], false);
  
}
