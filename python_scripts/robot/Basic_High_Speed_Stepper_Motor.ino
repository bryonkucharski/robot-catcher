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
//pin 9 for DIR -
//pin 8 for PUL-
//PUL + and DIR + go to 5v on arduino

unsigned long time;
double seconds;
bool flag;
double mmToRevolutions;
double mmToSteps;
double mm;
int incomingByte = 0;
#define mmPerRevolution 40
#define stepsPerRevolution 206
#define stepperMovement 334.75


//left 75 
//right 77
//334.75 == steps needed for 65 mm

void setup()
{  
   //starts the serial
   Serial.begin(9600);
   time = 0;
   seconds = 0;
   mmToSteps = 0;
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
  if(Serial.available() > 0){
    incomingByte = Serial.read();

    Serial.Print("I received: ");
    Serial.Println(incomingByte, DEC);

    if(incomingByte == 75){
      stepper.moveTo(-stepperMovement);
    }
    else if(incomingByte == 77){
      stepper.moveTo(stepperMovement);
    }

    
    if(stepper.distanceToGo() == 0){
      stepper.move(0);
      /*
      time = millis();
      seconds = time / 1000.0;
      Serial.print(seconds);
      Serial.print("\n");
      */
      //resets the incoming bit variable
      incomingByte = 0;
    }

    if(digitalRead(A0) == 0)
    {
      stepper.move(0);
      //sets the stepper motor away from the limit switch
      stepper.moveTo(-10);
     }
  
    stepper.run();
  
  }
}

