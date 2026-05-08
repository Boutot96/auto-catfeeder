#include <Stepper.h>

const int STEPS_PER_REV = 2048;
Stepper stepper(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
    stepper.setSpeed(10);
}

void loop() {
    stepper.step(1);
}