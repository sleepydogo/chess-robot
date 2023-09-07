#include "ramps_gripper.h"
#include <Arduino.h>

Ramps_Gripper::Ramps_Gripper(int aStepPin, int aDirPin, int aEnablePin, bool aInverse, float main_gear_teeth, float motor_gear_teeth, int microsteps, int steps_per_rev){
  stepper = new RampsStepper(aStepPin, aDirPin, aEnablePin, aInverse, main_gear_teeth, motor_gear_teeth, microsteps, steps_per_rev);
  stepper->setPosition(0);
  grip_steps= 500; // ver que valor es conveniente
}



void Ramps_Gripper::cmdOn() {
  for (int i = 1; i <= grip_steps; i++) {
      stepper->stepToPosition(i);
      stepper->update();
      delay(2);
  }
}

void Ramps_Gripper::cmdOff() {
  for (int i = 1; i <= grip_steps; i++) {
      stepper->stepToPosition(-i);
      stepper->update();
      delay(2);
  }
}

