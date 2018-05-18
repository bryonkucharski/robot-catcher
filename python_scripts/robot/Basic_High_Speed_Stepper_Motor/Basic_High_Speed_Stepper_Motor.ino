#include <AccelStepper.h>

//this is for no microstepping
//information:
//it takes 200 steps to get 1 revolution 
//GT2 belt = 2mm peak to peak
//20 tooth sprocket * 2mm peak to peak = 40mm per revolution
//some QUIK MAFS
//to travel 1000mm it would take 1000mm/40mm = 25 revolutions
//200 steps * 25 = 

AccelStepper stepper(1,9,8); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

//pin 1 for default

//WIRING
//pin 8 for DIR -
//pin 9 for PUL-
//PUL + and DIR + go to 5v on arduino
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A0

unsigned long time;
double seconds;
bool flag;
double mmToRevolutions;
double mmToSteps;
double mm;
int incomingByte = 0;
#define mmPerRevolution 40
#define stepsPerRevolution 206
#define stepperMovement 334
int counter;
int gridStepPosition = 0;
int gridPosition = 0;

//right 77
//334.75 == steps needed for 65 mm

void setup()
{  
   //starts the serial
   Serial.begin(9600);
   time = 0;
   seconds = 0;
   mmToSteps = 0;
   counter = 0;
   /* math isnt needed right now
   mm = movement;
   mmToRevolutions = mm / mmPerRevolution;
   //206 steps per revolution
   mmToSteps = mmToRevolutions * stepsPerRevolution;
  */
   //Negative mmToSteps : Towards end
   //Positive mmToStep : Towards Stepper Motor
   //stepper.moveTo(mmToSteps);
   stepper.setMaxSpeed(2000);
   stepper.setAcceleration(10000);
   pinMode(A0, INPUT);
}

void loop()
{  
  if(counter == 0)
    {
      gridStepPosition = 1500;
      stepper.moveTo(gridStepPosition);
      counter++;
    }
    
  if(Serial.available()){
    incomingByte = Serial.read();

    //resetting and homing the robot to get true Zero position
 

    //position 1
    if(incomingByte == 16){
      gridStepPosition = 0;
      stepper.moveTo(gridStepPosition);
    }
    //position 2
    else if(incomingByte == 17){
       //gridStepPosition = gridStepPosition - stepperMovement;
       gridStepPosition = -334;
       //time = millis();
       stepper.moveTo(gridStepPosition);
     }
     //position 3
     else if(incomingByte == 18){
       gridStepPosition = -668;
       stepper.moveTo(gridStepPosition);
     }
     //position 4
     else if(incomingByte == 19){
       //big value to reset from limit switch
       gridStepPosition = -1002;
       stepper.moveTo(gridStepPosition);
     }
     //position 5
     else if(incomingByte == 20){
        gridStepPosition = -1336;
        stepper.moveTo(gridStepPosition);
     }
     else
     {
        incomingByte = 0;
     }
   }

    
   if(stepper.distanceToGo() == 0){
      stepper.move(0);
      gridPosition = stepper.currentPosition() / 334;
      //Serial.write(gridPosition);

      seconds = time/1000;
      if(time != 0){
        Serial.print(time);
        Serial.print("\n");
      }
      
    }

    if(digitalRead(A0) == 0)
    {
      stepper.move(0);
      stepper.setCurrentPosition(0);
      stepper.setMaxSpeed(2000);
      stepper.moveTo(-10);
      
      while(true)
      {
        stepper.run();
        if(stepper.distanceToGo() == 0)
        {
          stepper.setCurrentPosition(0);
          stepper.setMaxSpeed(2000);
          gridStepPosition = 0;
          break;
        }
      }
      
    }
    
    stepper.run();
    
  
}
