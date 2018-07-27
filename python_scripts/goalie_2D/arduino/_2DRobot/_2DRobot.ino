
#include <AccelStepper.h>
#include <String.h> 

//This Original 2D robot API is for non diagonal movement./This should change eventually, but this is just to get it up and running

//this is for no microstepping
//information:
//it takes 206 steps to get 1 revolution 
//GT2 belt = 2mm peak to peak
//20 tooth sprocket * 2mm peak to peak = 40mm per revolution
//some QUIK MAFS
//to travel 1000mm it would take 1000mm/40mm = 25 revolutions
//206 steps * 25 = 5150
//334.75 == steps needed for 65 mm

//RIGHT STEPPER MOTOR
AccelStepper stepper(1,9,8); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5

//LEFT STEPPER MOTOR
AccelStepper stepper2(1,11,10); //Second stepper motor

//pin 1 for default

//WIRING RIGHT STEPPER
//pin 8 for DIR -
//pin 9 for PUL-
//PUL + and DIR + go to 5v on arduino

//WIRING LEFT STEPPER
//pin 10 for DIR -
//pin 11 for PUL-
//PUL + and DIR + go to 5v on arduino

//LIMIT SWITCH WIRING

//BOTTOM LEFT
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A0

//TOP RIGHT
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A1

//LEFT MIDDLE
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A2

//RIGHT MIDDLE
//Limit switch red wire to 3.3v power
//Limit switch black wire to ground
//Limit switch green wire to pin A3

//HOUSE KEEPING
//Negative mmToSteps : Towards end
//Positive mmToStep : Towards Stepper Motor
//stepper.moveTo(mmToSteps);

//setup for the incoming string
String readString = "";
int Xint = 0;
int Yint = 0;
int x = 0;
int y = 0;
#define mmPerRevolution 40
#define stepsPerRevolution 206
#define STOP 0
int axisFlag = 1;
int counter = 0;
int gridStepPosition = 0;
int gridStepPositionY = 0;
int stepperReset = 1;
int stepperReset2 = 1;

//X grid space position
int amountOfGridSpacesX = 5;
//Y grid space position
int amountOfGridSpacesY = 3;
#define totalStepsX 1395 //This is the amount of steps for 5 grid spaces
#define totalStepsY 628  //Steps for 3 grid spaces
int stepPositionValueX;
int stepPositionValueY;

//Keeping track of step positions
//This is so after Y movement, we can revert back to equal step positions
int stepperPosition = 0;
int stepper2Position = 0;
int YGridSpacePosition = 0;

//Amount of steps for grid space (~65mm)
#define gridSpaceSteps 334

void setup()
{  
   //starts the serial
   Serial.begin(9600);
   counter = 0;
   
   //This gives the amount of steps per grid space
   //EX for X: 334 = 1336 / (5-1)
   stepPositionValueX = totalStepsX / (amountOfGridSpacesX - 1);
   stepPositionValueY = totalStepsY / (amountOfGridSpacesY - 1);
   
   stepper.setCurrentPosition(0);
   stepper2.setCurrentPosition(0);
   
   //right stepper
   stepper.setMaxSpeed(2000);
   stepper.setAcceleration(10000);

   //left stepper 
   stepper2.setMaxSpeed(2000);
   stepper2.setAcceleration(10000);

   //limit switches
   pinMode(A0, INPUT);
   pinMode(A1, INPUT);
   pinMode(A2, INPUT);
   pinMode(A3, INPUT);
}

//Y Axis
//move down for right stepper == negative
//move down for left stepper == positive
//this needs to be opposite for going away

//X Axis
//move right for right stepper = positive
//move left for left stepper = positive
//needs to be opposite


void loop()
{  
  //Serial.print(counter);
  //Serial.print("\n");
  //resetting Y Axis
  if(counter == 1)
  {
    //really large number to reset back to the limit switch
    //right motor is negative
    //left motor is positive
    gridStepPosition = 6000;
    stepper.move(-gridStepPosition);
    stepper2.move(gridStepPosition);
  }
  else if(counter == 0)
  {
    
    //resetting X
    //Serial.print(1);
    //Serial.print("\n");
    //both stepper motors positive to move in X direction
    stepper.move(6000);
    stepper2.move(6000);
  } 
  
  else if(counter == 2)
  {
    //setting X to middle of gridspace
    gridStepPosition = stepPositionValueX * (3 - 1);
    stepper.setAcceleration(25000);
    stepper2.setAcceleration(25000);
    stepper.moveTo(-gridStepPosition);
    stepper2.moveTo(-gridStepPosition);
    
    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
      {
        stepperPosition = stepper.currentPosition();
        stepper2Position = stepper2.currentPosition();
        counter++;
        break;
      }
    }

    //Y movement
    //This is moving "UP" away from steppers
    gridStepPositionY = stepPositionValueY * (2 - 1);
    stepper.moveTo(stepperPosition + gridStepPositionY);
    stepper2.moveTo(stepper2Position - gridStepPositionY);

    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
      {
        YGridSpacePosition = 2;
        stepper.setCurrentPosition(stepperPosition);
        stepper2.setCurrentPosition(stepper2Position);
        stepper.setMaxSpeed(2000);
        stepper2.setMaxSpeed(2000);
        counter++;
        break;
      }
    }
  }
  

  if(Serial.available() && counter > 3)
  {  
    busyWaitForData();
    readFromSerialBuffer();

    if (msgReceived())
    {
      x = getXCoordinate(readString);
      y = getYCoordinate(readString);
      readString = ""; // Clear the readString

      if(x == 0 && y == 0)
      {
        counter = 0;
      }
    }
    
    if(axisFlag == 1 && counter > 3)
    {
      //X first
      //EX X = 2, Y = 3:
      //334 = 334 * (2-1)
      gridStepPosition = stepPositionValueX * (x - 1);
      //Since the stepper polarity is in negative boundaries, they have negative step values
      // |  1  |  2  |  3  |  4  |  5  |
      // | -0  |-334 |-668 |-1002|-1336|
      //Since we move X in with same rotation, we turn both in same direction
      stepper.moveTo(-gridStepPosition);
      stepper2.moveTo(-gridStepPosition);
      
      //This runs the stepper motors continuously until they finish
      while(true)
      {
        stepper.run();
        stepper2.run();
        if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
        {
          //gathering current position so we can revert back to that after Y movement
          stepperPosition = stepper.currentPosition();
          stepper2Position = stepper2.currentPosition();

          //flips flag after X movement to move to Y
          axisFlag = 2;
          break;
        }
      }
      //Serial.print("What we think is X position: ");
      //Serial.print(stepperPosition);
      //Serial.print("\n");
    }
    if(axisFlag == 2 && counter > 3)
    {
      //if the new coordinate is greater than the current Y position
      if(y > YGridSpacePosition)
      {
        //EX X = 2, Y = 3 and current grid space is 1
        //668 = 334 * (3 - 1)
        gridStepPositionY = stepPositionValueY * (y - YGridSpacePosition);

        //This moves the steppers in opposite directions for Y axis
        //moveTo stepperPosition + steps calculated above
        stepper.moveTo(stepperPosition + gridStepPositionY);

        //moveTo stepper2Position - steps calculated above
        //**************
        //MAY DELETE VARIABLE STEPPER2POSTION SINCE X STEPS ARE LINKED
        //**************
        stepper2.moveTo(stepper2Position - gridStepPositionY);

        //runs until done
        while(true)
        {
          stepper.run();
          stepper2.run();
          if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
          {
            YGridSpacePosition = y;

            //This resets the step position back to the previous, to maintain X positions
            stepper.setCurrentPosition(stepperPosition);
            stepper2.setCurrentPosition(stepper2Position);
            stepper.setMaxSpeed(2000);
            stepper2.setMaxSpeed(2000);
            axisFlag = 1;
            break;
          }
        }
        //Serial.print("What we think is Y position: ");
        //Serial.print(YGridSpacePosition);
        //Serial.print("\n");
      }
      else if(y < YGridSpacePosition)
      {
        //If Y is less than current Y grid position
        //If the same, does nothing
        gridStepPositionY = stepPositionValueY * (YGridSpacePosition - y);
        stepper.moveTo(stepperPosition - gridStepPositionY);
        stepper2.moveTo(stepper2Position + gridStepPositionY);
        while(true)
        {
          stepper.run();
          stepper2.run();
          if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
          {
            YGridSpacePosition = y;
            stepper.setCurrentPosition(stepperPosition);
            stepper2.setCurrentPosition(stepper2Position);
            stepper.setMaxSpeed(2000);
            stepper2.setMaxSpeed(2000);
            axisFlag = 1;
            break;
          }
        }
      //Serial.print("What we think is Y position: ");
      //Serial.print(YGridSpacePosition);
      //Serial.print("\n");
      }
      else if(y == YGridSpacePosition)
      {
        YGridSpacePosition = y;
        //This resets the step position back to the previous, to maintain X positions
        stepper.setCurrentPosition(stepperPosition);
        stepper2.setCurrentPosition(stepper2Position);
        stepper.setMaxSpeed(2000);
        stepper2.setMaxSpeed(2000);
        axisFlag = 1;
      }
    }
   //counter = 0;
  }

  //lower left limit switch (TRUE 0)
  if(digitalRead(A0) == 0)
  {
    stepper.move(STOP);
    stepper2.move(STOP);

    //if(stepperReset == 1)
    //{
      stepper.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      stepper.setMaxSpeed(2000);
      stepper2.setMaxSpeed(2000);
      stepper.moveTo(10);
      stepper2.moveTo(-10);
      //moving off of the Y axis by 10 steps
    //}
    //else
    //{
     // stepper.move(10);
      //stepper2.move(-10);
    //}  
    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper.distanceToGo() == 0 && stepper2.distanceToGo() == 0)
      {
        //if(stepperReset == 1)
        //{
          stepper.setCurrentPosition(0);
          stepper2.setCurrentPosition(0);
          stepper.setMaxSpeed(2000);
          stepper2.setMaxSpeed(2000);
        //}  
        gridStepPosition = 0;
        gridStepPositionY = 0;
        //counter++;
        break;
      }
    } 
    counter++;
    stepperReset = 2;
  }

  //left middle limit switch (TRUE 0)
  if(digitalRead(A1) == 0)
  {
    stepper.move(STOP);
    stepper2.move(STOP);
    //if(stepperReset2 == 1)
    //{
      stepper.setCurrentPosition(0);
      stepper2.setCurrentPosition(0);
      stepper.setMaxSpeed(2000);
      stepper2.setMaxSpeed(2000);
      stepper.moveTo(-10);
      stepper2.moveTo(-10);
    //}
   // else
    //{
      //stepper.move(-10);
      //stepper2.move(-10);
    //}
      
    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
      {
        //if(stepperReset2 == 1)
        //{
          stepper.setCurrentPosition(0);
          stepper2.setCurrentPosition(0);
          stepper.setMaxSpeed(2000);
          stepper2.setMaxSpeed(2000);
        //}
        gridStepPosition = 0;
        gridStepPositionY = 0;
        break;
      }
    } 
    counter++;
    stepperReset2 = 2;
  }

  //top right switch
  //basically backs off the limit switch by 10 steps
  if(digitalRead(A2) == 0)
  {
    stepper.move(STOP);
    stepper2.move(STOP);
    stepper.setMaxSpeed(2000);
    stepper2.setMaxSpeed(2000);
    stepper.move(-10);
    stepper2.move(10);

    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
      {
        break;
      }
    }
  }
    
  //right middle switch
  if(digitalRead(A3) == 0)
  {
    stepper.move(STOP);
    stepper2.move(STOP);
    stepper.setMaxSpeed(2000);
    stepper2.setMaxSpeed(2000);

    //move is moveto(currentPos + relative)
    stepper.move(10);
    stepper2.move(10);

    while(true)
    {
      stepper.run();
      stepper2.run();
      if(stepper2.distanceToGo() == 0 && stepper.distanceToGo() == 0)
      {
        break;
      }
    }
  }

  stepper.run();
  stepper2.run();    
}

void readFromSerialBuffer()
{
  while (Serial.available())
  {
    delay(30);  // delay to allow buffer to fill
    if (Serial.available() > 0)
    {
      char msg = Serial.read();
      readString += msg;
    }
  }
}

void busyWaitForData()
{
  while (!Serial.available()) {} // wait for data to arrive
}

int getXCoordinate(String msg)
{
  return msg.substring(0, msg.indexOf(',')).toInt();
}

int getYCoordinate(String msg)
{
  return msg.substring(msg.indexOf(',') + 1).toInt();
}
bool msgReceived()
{
  return readString.length() > 0;
}

void printAcknowledgement(int x, int y)
{
    Serial.print("Arduino received: \n");  
    Serial.print("\tx = "); //see what was received
    Serial.print(x); //see what was received
    Serial.print(";");
    Serial.print("\n\ty = ");
    Serial.print(y);
    Serial.print(";");
}

