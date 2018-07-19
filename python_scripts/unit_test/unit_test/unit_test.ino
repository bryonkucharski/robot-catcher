int incomingByte = 0;

void setup() {
   Serial.begin(9600);
   pinMode(LED_BUILTIN, OUTPUT); //make the LED pin (13) as output
  digitalWrite (LED_BUILTIN, LOW);
  Serial.println("Hi!, I am Arduino");
  
}

void loop() {
   if (Serial.available()) {
    /* read the most recent byte */
    incomingByte = Serial.read();
    /*ECHO the value that was read, back to the serial port. */
    Serial.print(incomingByte);
    delay(1000);
  }

  if (incomingByte == '1'){
    digitalWrite (LED_BUILTIN, HIGH);
  }

  else if (incomingByte == '0'){
digitalWrite (LED_BUILTIN, LOW);
  }

}
