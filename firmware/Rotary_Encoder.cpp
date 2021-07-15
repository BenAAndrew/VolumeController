#include "Rotary_Encoder.h"

Rotary_Encoder::Rotary_Encoder(unsigned int _pinA, unsigned int _pinB, unsigned int _pinBtn, unsigned int _a){
  index = 0;
  pinA = _pinA;
  pinB = _pinB;
  pinBtn = _pinBtn;
  pushDuration = 0;
  pushed = false;
  stepThreshold = 2;
  pushThreshold = 10000;
  previousVal = _a;
}

unsigned int Rotary_Encoder::update(unsigned int _a, unsigned int _b, unsigned int _button){
  // Push
  if (_button == 0 && !pushed){
    pushDuration++;
    if(pushDuration == pushThreshold){
      pushed = true;
      return index*10+3;
    }
  } else if(_button == 1){
    pushed = false;
    pushDuration = 0;
  }

  // Rotate
  if (_a != previousVal) {
    previousVal = _a;
    if (_b != _a) {
      totalRotation++;
      if(totalRotation == stepThreshold){
        totalRotation = 0;
        return index*10+2;
      }
    } else {
      totalRotation--;
      if(totalRotation == -stepThreshold){
        totalRotation = 0;
        return index*10+1;
      }
    }
  }
  
  return 0;
}
