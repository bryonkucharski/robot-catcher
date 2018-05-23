#include <AccelStepper.h>

//this is for no microstepping
//information:
//it takes 206 steps to get 1 revolution 
//GT2 belt = 2mm peak to peak
//20 tooth sprocket * 2mm peak to peak = 40mm per revolution
//some QUIK MAFS
//to travel 1000mm it would take 1000mm/40mm = 25 revolutions
//206 steps * 25 = 5150
//334.75 == steps needed for 65 mm

AccelStepper stepper(1,9,8); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

//pin 1 for default

//WIRING
//pin 8 for DIR -
//pin 9 for PUL-
//PUL + and DIR + go to 5v on arduino
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A0

   //Negative mmToSteps : Towards end
   //Positive mmToStep : Towards Stepper Motor
   //stepper.moveTo(mmToSteps);

int incomingByte = 0;
#define mmPerRevolution 40
#define stepsPerRevolution 206
int counter;
int gridStepPosition = 0;
int gridPosition = 0;

//added in for modularity
int amountOfGridSpaces = 5;
int totalStepsFor2D = 1339;
int stepPositionValue;

//Amount of steps for grid space
#define stepperMovement 334

void setup()
{  
   //starts the serial
   Serial.begin(9600);
   counter = 0;
   stepPositionValue = totalStepsFor2D / amountOfGridSpaces;
   stepper.setMaxSpeed(2000);
   stepper.setAcceleration(10000);
   pinMode(A0, INPUT);
}

void loop()
{  
  if(counter == 0)
    {
      //really large number to reset back to the limit switch
      gridStepPosition = 1500;
      stepper.moveTo(gridStepPosition);
      counter++;
    }
    
  if(Serial.available()){
    //reads serial communication and saves what grid space it need to go to
    incomingByte = Serial.read();

    //takes modular amount of steps for position and multiplies it by the position to obtain moveTo location
    gridStepPosition = stepPositionValue * incomingByte;

    //needs to be negative due to going away from motor
    stepper.moveTo(-gridStepPosition);
   }

    
   if(stepper.distanceToGo() == 0){
      stepper.move(0);  
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

