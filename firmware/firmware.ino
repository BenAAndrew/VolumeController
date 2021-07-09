#include <Adafruit_GFX.h>    // Core graphics library
#include <Adafruit_ST7735.h> // Hardware-specific library
#include "Rotary_Encoder.h" // Hardware-specific library
#include <SPI.h>

// TFT Screen
#define sclk 13
#define mosi 11
#define cs   10
#define dc   8
#define rst  5

#define icon_size 60
#define icon_area icon_size*icon_size
#define margin_x 2
#define margin_y 10

Adafruit_ST7735 tft = Adafruit_ST7735(cs, dc, mosi, sclk, rst);
uint8_t r;
uint8_t g;
uint8_t b;

// Encoders
#define numEncoders 1
#define stepSize 2
#define pushDuration 10000

#define encoder1A 2
#define encoder1B 3
#define encoder1Btn 4

Rotary_Encoder encoders[] = {
  Rotary_Encoder(encoder1A, encoder1B, encoder1Btn, digitalRead(encoder1A))
};

// Variables
uint8_t command;
uint8_t output;

void setup() {
  // Screen setup
  tft.initR(INITR_BLACKTAB);
  tft.fillScreen(ST7735_BLACK);
  tft.setTextColor(ST7735_GREEN, ST7735_BLACK);
  tft.setTextSize(1);

  // Encoder setup
  pinMode(encoder1A, INPUT);
  pinMode(encoder1B, INPUT);
  pinMode(encoder1Btn, INPUT_PULLUP);
  
  Serial.begin(19200);
}

void loop() {
  if (Serial.available() > 0) {
    command = getNextInput();
    if(command == 'i'){
      drawIcon();
    } else if(command == 'v'){
      displayVolume();
    }
  }
  checkEncoders();
}

void checkEncoders(){
  for(uint8_t i = 0; i < numEncoders; i++){
    output = encoders[i].update(digitalRead(encoders[i].pinA), digitalRead(encoders[i].pinB), digitalRead(encoders[i].pinBtn));
    if(output != 0)
      Serial.write(output);
  }
}

uint8_t getXPosition(uint8_t index){
  uint8_t x = margin_x;
  if(index % 2 == 1){
    x += margin_x + icon_size;
  }
  return x;
}

uint8_t getYPosition(uint8_t index){
  uint8_t y = margin_y;
  if(index > 1){
    y += margin_y*2 + icon_size;
  }
  return y;
}

void displayVolume(){
  uint8_t pos = getNextInput();
  uint8_t volume = getNextInput();
  String text = String(volume);
  if(volume < 9){
    text += ' ';
  }
  if(volume < 99){
    text += ' ';
  }
  uint8_t x = getXPosition(pos);
  uint8_t y = getYPosition(pos);
  tft.setCursor(x,y);
  tft.print(text);
  Serial.write('d');
}

void drawIcon(){
  uint8_t pos = getNextInput();
  uint8_t x = getXPosition(pos);
  uint8_t y = getYPosition(pos);
  uint8_t starting_x = x;

  // Colours
  uint8_t num_colours = getNextInput();
  int colours[num_colours];
  for(uint8_t i = 0; i < num_colours; i++){
    r = getNextInput();
    g = getNextInput();
    b = getNextInput();
    colours[i] = tft.Color565(r,g,b);
  }

  // Drawing
  uint8_t index;
  for(int pixel_counter = 0; pixel_counter < icon_area; pixel_counter++){
    index = getNextInput();
    tft.drawPixel(x, y, colours[index]);
    if(x == icon_size-1+starting_x){
      x = starting_x;
      y++;
    } else {
      x++;
    }
  }
  Serial.write('d');
}

uint8_t getNextInput() {
  while(!Serial.available());
  return Serial.read();
}
