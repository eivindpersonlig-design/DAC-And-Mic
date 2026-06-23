#include <Arduino.h>
#include <math.h>

const uint8_t PINS[8] = {2, 3, 4, 5, 6, 7, 8, 9};

struct GpioPinMap {
  NRF_GPIO_Type* port;
  uint32_t       mask;
};

GpioPinMap pinMap[8];

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

uint8_t sineTable[256];

void buildSineTable() {
  for (int i = 0; i < 256; i++) {
    sineTable[i] = (uint8_t)(127.5f + 127.5f * sinf(2.0f * M_PI * i / 256.0f));
  }
}

// Frequency sweep: ramps from START_HZ up to END_HZ and back down
#define START_HZ   100
#define END_HZ    2000
#define STEP_HZ     10   // how many Hz to change per cycle
#define HOLD_CYCLES  2   // how many full cycles to hold each frequency

void setup() {
  setupPins();
  buildSineTable();
}

void loop() {
  static int  currentHz  = START_HZ;
  static int  direction  = 1;
  static int  holdCount  = 0;

  // µs per sample for current frequency
  // 1 cycle = 256 samples, period = 1/Hz seconds = 1000000/Hz µs
  // µs per sample = 1000000 / (Hz * 256)
  unsigned int usPerSample = 1000000UL / ((unsigned long)currentHz * 256);

  for (int i = 0; i < 256; i++) {
    dacWrite(sineTable[i]);
    delayMicroseconds(usPerSample);
  }

  holdCount++;
  if (holdCount >= HOLD_CYCLES) {
    holdCount = 0;
    currentHz += direction * STEP_HZ;

    if (currentHz >= END_HZ) {
      currentHz = END_HZ;
      direction = -1;
    } else if (currentHz <= START_HZ) {
      currentHz = START_HZ;
      direction = 1;
    }
  }
}