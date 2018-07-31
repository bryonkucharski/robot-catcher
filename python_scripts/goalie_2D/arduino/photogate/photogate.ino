int gate1Pin = A0;
int gate2Pin = A1; 

int gate1Value = 0;
int gate2Value = 0;

int threshold = 900;

unsigned long startTime = 0;
unsigned long stopTime = 0;

bool timerStarted = false;

float gateDistance = 73.9775;
int thrustLevel = -1;

void setup() 
{
  Serial.begin(9600);
}

void loop() 
{
  gate1Value = analogRead(gate1Pin);
  gate2Value = analogRead(gate2Pin);

   //Serial.print(gate1Value);
   //Serial.print(", ");
   //Serial.println(gate2Value);
  
  if (gate1Value < threshold && !timerStarted)
  {
    startTime = millis();
    timerStarted = true;
  }
  else if (gate2Value < threshold && timerStarted == true)
  {
    timerStarted = false;
    stopTime = millis();
    unsigned long elapsedTime = stopTime - startTime;
    if (elapsedTime)
    {
      float vel = (gateDistance / (stopTime - startTime));
      int thrust = convertThrust(vel);
      Serial.write(thrust);
      //Serial.println(thrust,10);
    }
   // printTime(startTime, stopTime);
  }
}

int convertThrust(float velocity)
{
  
  if (velocity >= .1800){ return 2;}
  else if (velocity < .1800 && velocity >= .1450){return 1;}
  else if (velocity < .1450) {return 0;}
  

  
   //for 5 thrust positions
    /*
   if (velocity >= .1725){ return 4;}
   else if (velocity < .1725 && velocity >= .1575){return 3;}
   else if (velocity < .1575 && velocity >= .1450){return 2;}
   else if (velocity < .1450 && velocity >= .1250) {return 1;}
   else if (velocity < .1250) {return 0;}  
   */
  
}

void printTime(unsigned long startTime, unsigned long stopTime) 
{
  Serial.print("Velocity: ");
  float vel = (gateDistance / (stopTime - startTime));
  Serial.print(vel,10);
  Serial.print(" cm/s ");
  Serial.print(convertThrust(vel));
  Serial.println();
}

