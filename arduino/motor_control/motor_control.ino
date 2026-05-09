#include <Stepper.h>
#include <Arduino.h>

const int STEPS_PER_REV = 2048;
Stepper stepper(STEPS_PER_REV, 8, 10, 9, 11);
long totalSteps = 0;
bool feeding = false;

void setup() {
    stepper.setSpeed(10);
    Serial.begin(9600);
}

void loop() {
    if (Serial.available() > 0) {
        char cmd = Serial.read();
        if (cmd == 'D') {
            stepper.step(13900); // Dispense food (90 degrees)
        }
        if (cmd == 'S') {
            feeding = true; // Reset position
            totalSteps = 0;
        }
        if (cmd == 'R') {
            feeding = false; 
            Serial.print("Total steps: ");
            Serial.println(totalSteps);

        }
    }
    if (feeding) {
        stepper.step(10);
        totalSteps += 10;
    }
}