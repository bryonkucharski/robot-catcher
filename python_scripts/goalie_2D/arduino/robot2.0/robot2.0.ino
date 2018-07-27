#include <AccelStepper.h>
#include <String.h> 
/*
  This Original 2D robot API is for non diagonal movement.
  This should change eventually, but this is just to get it up and running
  this is for no microstepping
  information:
  it takes 206 steps to get 1 revolution 
  GT2 belt = 2mm peak to peak
  20 tooth sprocket * 2mm peak to peak = 40mm per revolution
  some QUIK MAFS
  to travel 1000mm it would take 1000mm/40mm = 25 revolutions
  206 steps * 25 = 5150
  334.75 == steps needed for 65 mm
  
  WIRING RIGHT STEPPER
  pin 8 for DIR -
  pin 9 for PUL-
  PUL + and DIR + go to 5v on arduino
  
  WIRING LEFT STEPPER
  pin 10 for DIR -
  pin 11 for PUL-
  PUL + and DIR + go to 5v on arduino
  
  LIMIT SWITCH WIRING
  BOTTOM LEFT
  Limit switch red wire to 3.3v power
  Limit switch black wire to ground
  Limit switch green wire to pin A0
  
  TOP RIGHT
  Limit switch red wire to 3.3v power
  Limit switch black wire to ground
  Limit switch green wire to pin A1
  
  LEFT MIDDLE
  Limit switch red wire to 3.3v power
  Limit switch black wire to ground
  Limit switch green wire to pin A2
  
  RIGHT MIDDLE
  Limit switch red wire to 3.3v power
  Limit switch black wire to ground
  Limit switch green wire to pin A3
  
  HOUSE KEEPING
  Negative mmToSteps : Towards end
  Positive mmToStep : Towards Stepper Motor
  stepperRight.moveTo(mmToSteps);
*/
#define mmPerRevolution     40
#define stepsPerRevolution  206
#define numGridSpacesX 5
#define numGridSpacesY 3
#define XInches 12
#define YInches 8

//CONSTANTS
#define mmPerInch 25.4
#define mmPerRevolution 40
#define stepsPerRevolution 206

//MATH
#define mmPerGridX (XInches/numGridSpacesX) * mmPerInch //60.93mm
#define mmPerGridY (YInches/numGridSpacesY) * mmPerInch //67.73mm

#define mmPerStep stepsPerRevolution / mmPerRevolution //5.15 mm/step
#define totalStepsX mmPerStep * (mmPerGridX * numGridSpacesX - 1 ) //1251
#define totalStepsY mmPerStep * (mmPerGridY *numGridSpacesY -1 ) //698

//#define totalStepsX 1251 //This is the amount of steps for 5 grid spaces
//#define totalStepsY 698  //Steps for 3 grid spaces
#define HOME 6000
#define STOP 0
#define X 1
#define Y 2
#define HOMING_X  0
#define HOMING_Y  1
#define HOMED     2
#define READY     3
AccelStepper stepperRight(1, 9, 8); // Defaults to AccelStepper::FULL4WIRE (4 pins) on 2, 3, 4, 5
AccelStepper stepperLeft(1, 11, 10); //Second stepper motor, pin 1 for default
String msgFromPython = "";
int x = 0;
int y = 0;
int state;
int axisFlag;
int gridStepPosition = 0;
int gridStepPositionY = 0;
int stepPositionValueX;
int stepPositionValueY;
//Keeping track of step positions
//This is so after Y movement, we can revert back to equal step positions
int stepperRightPosition = 0;
int stepperLeftPosition = 0;
//int YGridSpacePosition = 0;
int YGridSpacePosition = 1;
void setup()
{  
   Serial.begin(9600);
   
   state = HOMING_X;
   axisFlag = X;
   
   //This gives the amount of steps per grid space
   //EX for X: 334 = 1336 / (5-1)
   stepPositionValueX = totalStepsX / (numGridSpacesX - 1);
   stepPositionValueY = totalStepsY / (numGridSpacesY - 1);
   
   stepperRight.setCurrentPosition(0);
   stepperLeft.setCurrentPosition(0);
   
   stepperRight.setMaxSpeed(2000);
   stepperLeft.setMaxSpeed(2000);
   
   stepperRight.setAcceleration(10000);
   stepperLeft.setAcceleration(10000);
   
   //limit switches
   pinMode(A0, INPUT);
   pinMode(A1, INPUT);
   pinMode(A2, INPUT);
   pinMode(A3, INPUT);
}
/*
  Y Axis
  move down for right stepper == negative
  move down for left stepper == positive
  this needs to be opposite for going away
  
  X Axis
  move right for right stepper = positive
  move left for left stepper = positive
  needs to be opposite
*/
void loop()
{  
  if (state == HOMING_X)
  {
    homeX();
  } 
  else if (state == HOMING_Y)
  {
    homeY();
  }
  else if (state == HOMED)
  {
    resetYGridSpacePosition();
    moveToCenter();
    state = READY;
  }
  else if (state == READY)
  {
    getCoordinateFromPython();
    moveToCoordinate(x, y);
    delay(500);
    state = HOMING_X;
  }
  checkAllLimitSwitches();
  stepperRight.run();
  stepperLeft.run();    
}
void readFromSerialBuffer()
{
  while (Serial.available())
  {
    delay(30);  // delay to allow buffer to fill
    if (Serial.available() > 0)
    {
      char c = Serial.read();
      msgFromPython += c;
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
  return msgFromPython.length() > 0;
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
void checkLowerLeftLimitSwitch()
{
   //lower left limit switch (TRUE 0)
  if(digitalRead(A0) == 0)
  {
    stepperRight.move(STOP);
    stepperLeft.move(STOP);
    stepperRight.setCurrentPosition(0);
    stepperLeft.setCurrentPosition(0);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    stepperRight.moveTo(10);
    stepperLeft.moveTo(-10);
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      
      if(steppersDoneMoving())
      {
        stepperRight.setCurrentPosition(0);
        stepperLeft.setCurrentPosition(0);
        stepperRight.setMaxSpeed(2000);
        stepperLeft.setMaxSpeed(2000);
        gridStepPosition = 0;
        gridStepPositionY = 0;
        break;
      }
    } 
    state++;
  }
}
void checkMiddleLeftLimitSwitch()
{
  if(digitalRead(A1) == 0)
  {
    stepperRight.move(STOP);
    stepperLeft.move(STOP);
    stepperRight.setCurrentPosition(0);
    stepperLeft.setCurrentPosition(0);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    stepperRight.moveTo(-10);
    stepperLeft.moveTo(-10);
      
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if (steppersDoneMoving())
      {
        stepperRight.setCurrentPosition(0);
        stepperLeft.setCurrentPosition(0);
        
        stepperRight.setMaxSpeed(2000);
        stepperLeft.setMaxSpeed(2000);
        gridStepPosition = 0;
        gridStepPositionY = 0;
        break;
      }
    } 
    state++;
  }
}
void checkTopRightLimitSwitch()
{
  if(digitalRead(A2) == 0)
  {
    stepperRight.move(STOP);
    stepperLeft.move(STOP);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    stepperRight.move(-10);
    stepperLeft.move(10);
    
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if(steppersDoneMoving())
      {
        break;
      }
    }
  }
}
void checkMiddleRightLimitSwitch()
{
  if(digitalRead(A3) == 0)
  {
    stepperRight.move(STOP);
    stepperLeft.move(STOP);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    stepperRight.move(10);
    stepperLeft.move(10);
    
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if(steppersDoneMoving())
      {
        break;
      }
    }
  }
}
bool steppersDoneMoving()
{
  if (stepperLeft.distanceToGo() == 0 && stepperRight.distanceToGo() == 0)
  {
    return true;
  }
  return false;
}
void moveX()
{
  //X first
  //EX X = 2, Y = 3:
  //334 = 334 * (2-1)
  gridStepPosition = stepPositionValueX * (x - 1);
  //Since the stepper polarity is in negative boundaries, they have negative step values
  // |  1  |  2  |  3  |  4  |  5  |
  // | -0  |-334 |-668 |-1002|-1336|
  //Since we move X in with same rotation, we turn both in same direction
  stepperRight.moveTo(-gridStepPosition);
  stepperLeft.moveTo(-gridStepPosition);
  
  //This runs the stepper motors continuously until they finish
  while(true)
  {
    stepperRight.run();
    stepperLeft.run();
    if(steppersDoneMoving())
    {
      //gathering current position so we can revert back to that after Y movement
      stepperRightPosition = stepperRight.currentPosition();
      stepperLeftPosition = stepperLeft.currentPosition();
      
      //flips flag after X movement to move to Y
      axisFlag = Y;
      break;
    }
  }
  //Serial.print("What we think is X position: ");
  //Serial.print(stepperRightPosition);
  //Serial.print("\n");
}
void moveY()
{
  //if the new coordinate is greater than the current Y position
  if (y > YGridSpacePosition)
  {
    //EX X = 2, Y = 3 and current grid space is 1
    //668 = 334 * (3 - 1)
    gridStepPositionY = stepPositionValueY * (y - YGridSpacePosition);
    //This moves the steppers in opposite directions for Y axis
    //moveTo stepperRightPosition + steps calculated above
    stepperRight.moveTo(stepperRightPosition + gridStepPositionY);
    //moveTo stepperLeftPosition - steps calculated above
    //**************
    //MAY DELETE VARIABLE stepperLeftPOSTION SINCE X STEPS ARE LINKED
    //**************
    stepperLeft.moveTo(stepperLeftPosition - gridStepPositionY);
    //runs until done
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if (steppersDoneMoving())
      {
        YGridSpacePosition = y;
        
        //This resets the step position back to the previous, to maintain X positions
        stepperRight.setCurrentPosition(stepperRightPosition);
        stepperLeft.setCurrentPosition(stepperLeftPosition);
        
        stepperRight.setMaxSpeed(2000);
        stepperLeft.setMaxSpeed(2000);
        
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
    
    stepperRight.moveTo(stepperRightPosition - gridStepPositionY);
    stepperLeft.moveTo(stepperLeftPosition + gridStepPositionY);
    
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if(steppersDoneMoving())
      {
        YGridSpacePosition = y;
        
        stepperRight.setCurrentPosition(stepperRightPosition);
        stepperLeft.setCurrentPosition(stepperLeftPosition);
        
        stepperRight.setMaxSpeed(2000);
        stepperLeft.setMaxSpeed(2000);
        
        axisFlag = X;
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
    stepperRight.setCurrentPosition(stepperRightPosition);
    stepperLeft.setCurrentPosition(stepperLeftPosition);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    axisFlag = X;
  }
}
void moveY2()
{
  if (y > YGridSpacePosition)
  {
    //Ex. X = 2, Y = 3 and current grid space is 1
    //668 = 334 * (3 - 1)
    gridStepPositionY = stepPositionValueY * (y - YGridSpacePosition);
    //**************
    //MAY DELETE VARIABLE stepperLeftPOSTION SINCE X STEPS ARE LINKED
    //**************
    stepperRight.moveTo(stepperRightPosition + gridStepPositionY);
    stepperLeft.moveTo(stepperLeftPosition - gridStepPositionY);
    
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if (steppersDoneMoving())
      {
        break;
      }
    }
  }
  else if(y < YGridSpacePosition)
  {
    gridStepPositionY = stepPositionValueY * (YGridSpacePosition - y);
    
    stepperRight.moveTo(stepperRightPosition - gridStepPositionY);
    stepperLeft.moveTo(stepperLeftPosition + gridStepPositionY);
    
    while(true)
    {
      stepperRight.run();
      stepperLeft.run();
      if(steppersDoneMoving())
      {
        break;
      }
    }
  }
  if(y == YGridSpacePosition)
  {
    YGridSpacePosition = y;
    
    //This resets the step position back to the previous, to maintain X positions
    stepperRight.setCurrentPosition(stepperRightPosition);
    stepperLeft.setCurrentPosition(stepperLeftPosition);
    
    stepperRight.setMaxSpeed(2000);
    stepperLeft.setMaxSpeed(2000);
    
    axisFlag = X;
  }
}
void homeX()
{
  //both stepper motors positive to move in X direction
  stepperRight.move(HOME);
  stepperLeft.move(HOME);
}
void homeY()
{
  //right motor is negative
  //left motor is positive
  gridStepPosition = HOME;
  stepperRight.move(-HOME);
  stepperLeft.move(HOME);
}
void moveToCenter()
{
  x = 3;
  y = 2;
  
  go();
}
void moveToCoordinate(int x1, int y1)
{
  x = x1;
  y = y1;
  go();
}
void go()
{
  if(axisFlag == X)
  {
    moveX();
  }
  
  if(axisFlag == Y)
  {
    moveY();
  }
}
void resetYGridSpacePosition()
{
  YGridSpacePosition = 1;
}
void checkAllLimitSwitches()
{
  checkLowerLeftLimitSwitch();
  checkMiddleLeftLimitSwitch();
  checkTopRightLimitSwitch();
  checkMiddleRightLimitSwitch();
}
void getCoordinateFromPython()
{
  busyWaitForData();
  
  if(Serial.available())
  {  
    readFromSerialBuffer();
    
    if (msgReceived())
    {
      x = getXCoordinate(msgFromPython);
      y = getYCoordinate(msgFromPython);
      msgFromPython = "";
      //printAcknowledgement(x, y);
    }
  }
}
