#ifndef _ROTARY_ENCODER
#define _ROTARY_ENCODER

class Rotary_Encoder {
  public:
    Rotary_Encoder(unsigned int _pinA, unsigned int _pinB, unsigned int _pinBtn, unsigned int _a);
    unsigned int update(unsigned int _a, unsigned int _b, unsigned int _button);
    unsigned int
      pinA, pinB, pinBtn;
  private:
  int
    previousVal, totalRotation, stepThreshold;
  unsigned int
    index, pushDuration, pushThreshold;
  bool
    pushed;
};

#endif
