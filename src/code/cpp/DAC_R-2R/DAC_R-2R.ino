#include <Arduino.h>
#include <mbed.h>
#include "To-be-continued1.h"

const uint8_t PINS[8] = {2, 3, 4, 5, 6, 7, 8, 9};

struct GpioPinMap {
  NRF_GPIO_Type* port;
  uint32_t mask;
};
GpioPinMap pinMap[8];

volatile unsigned int sampleIndex = 0;

void setupPins() {
  for (int i = 0; i < 8; i++) {
    pinMode(PINS[i], OUTPUT);
    uint32_t pn   = digitalPinToPinName(PINS[i]);
    uint32_t port = (pn >> 5) & 0x1;
    uint32_t bit  = pn & 0x1F;
    pinMap[i].port = (port == 0) ? NRF_P0 : NRF_P1;
    pinMap[i].mask = 1UL << bit;
  }
}

void dacWrite(uint8_t value) {
  for (int i = 0; i < 8; i++) {
    if (value & (1 << i))
      pinMap[i].port->OUTSET = pinMap[i].mask;
    else
      pinMap[i].port->OUTCLR = pinMap[i].mask;
  }
}

// Ticker fires the callback at a fixed interval using mbed OS underneath
mbed::Ticker audioTicker;

void audioISR() {
  dacWrite(audio[sampleIndex]);
  sampleIndex++;
  if (sampleIndex >= audio_len) {
    sampleIndex = 0; // loop
  }
}

void setup() {
  setupPins();

  // attach(callback, interval_in_seconds)
  float interval = 1.0f / (float)AUDIO_SAMPLE_RATE;
  audioTicker.attach(audioISR, interval);
}

void loop() {
  // Ticker runs in the background — nothing needed here
}