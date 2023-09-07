#ifndef RAMPS_GRIPPER_H_
#define RAMPS_GRIPPER_H_

#include "RampsStepper.h"

class Ramps_Gripper {
public:
  Ramps_Gripper(int aStepPin, int aDirPin, int aEnablePin, bool aInverse, float main_gear_teeth, float motor_gear_teeth, int microsteps, int steps_per_rev);

  ~Ramps_Gripper(){
    delete stepper;
  }

  void cmdOn();
  void cmdOff();

private:
  int grip_steps;
  RampsStepper *stepper;
  
};

#endif
