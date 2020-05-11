// Import the libraries
#include "Wire.h"
#include "Adafruit_MCP4725.h"
     
// Define constants
#define DAC_RESOLUTION 8
#define DAC_MAX 4000
#define MIN_LIGHT 10
#define SCALE 8
#define CONSTANT 3500

Adafruit_MCP4725 dac;
     
void setup()
{
  analogReference(EXTERNAL);
  // begins serial communication for testing, and wire for I2C using fast mode 
  while (!Serial);
  Serial.begin(9600);
  delay(200);
  Wire.begin();
  // begin DAC
  dac.begin(0x62);  
  Serial.println("setup done");
}

int vout = 0;
int light;

void loop() {
    light = analogRead(A0);


    //Serial.print("light:");
    //Serial.println(light);
    
    vout = (6*light - 1200)*0.5;
      // keep vout inside our bounds
    if (vout > DAC_MAX) vout = DAC_MAX;
    else if (vout < MIN_LIGHT) vout = MIN_LIGHT;

    //Serial.print("vout:");
    //Serial.println(vout);
    
  
    // finally output DAC voltage
    dac.setVoltage(vout, false);
    //delay(100);

}
