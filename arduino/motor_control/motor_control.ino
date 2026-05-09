#include <Stepper.h>
#include <Arduino.h>

const int STEPS_PER_REV = 2048;
Stepper stepper(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
    stepper.setSpeed(10);
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 'D') {
            stepper.step(STEPS_PER_REV); // Dispense food (90 degrees)
        }
    }
}