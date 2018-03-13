#define LED 13

void setup() 
{
    pinMode(LED, OUTPUT);
    Serial.begin(9600);
}

void loop() 
{
    if (Serial.available()) 
    {
        char msg = Serial.read();
        Serial.println(msg);
        
        if (msg == '1') 
        {
            digitalWrite(LED, HIGH);
        }
        else if (msg == '0') 
        {
            digitalWrite(LED, LOW);
        }
    }
}
