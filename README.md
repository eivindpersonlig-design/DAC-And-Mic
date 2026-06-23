#Code made by Magnus Næssan Gaarder
#Circuit made by Bjørnar Odden Christiansen & Eivind Næssan Gaarder

# Arduino Audio Playback via R-2R DAC

This project plays audio on an **Arduino Nano 33 BLE** using an 8-bit R-2R resistor ladder DAC. The audio is output using a high-speed timer interrupt (TIMER1) for precise sample timing.

---

## Prerequisites

### 1. Libraries

The code requires the following Arduino libraries:

- **Arduino.h** – Core Arduino library (included by default in Arduino IDE).  
- **Frequency_sweep.h** – Custom header file generated from your audio data (e.g., using Python to convert WAV to an array).  

> Make sure you have `Frequency_sweep.h` in the same folder as your `.ino` file.

### 2. IDE

- **[Arduino IDE](https://www.arduino.cc/en/software)** (version 2.x recommended)  
- Make sure you have the **Arduino mbed-enabled boards** installed:
  - Go to **Tools → Board → Board Manager** → search for **Arduino mbed-enabled boards** → install.
  - Select **Arduino Nano 33 BLE** as the board.

### 3. Hardware

- **Arduino Nano 33 BLE**  
- **8 resistors** forming an R-2R ladder DAC (values usually 10 kΩ and 20 kΩ).  
- **Wires and breadboard** for connections:  
  - Arduino pins 2–9 → R-2R ladder inputs (LSB → MSB physically).  
  - Ladder output → speaker or amplifier input (through capacitor if needed).  

> Note: The Nano 33 BLE outputs **3.3V logic**, so your DAC and amplifier should be compatible with 3.3V logic levels.

### 4. Audio Data

- Audio should be converted to **8-bit samples** at a **defined sample rate** matching `AUDIO_SAMPLE_RATE` in your header file.  
- The audio data array should be named `audio` with length `audio_len`.

---

## Usage

1. Copy your `.ino` file and `Frequency_sweep.h` into a project folder.  
2. Connect the R-2R ladder to pins 2–9 as defined in the code.  
3. Open the project in Arduino IDE.  
4. Select **Arduino Nano 33 BLE** as the board and the correct COM port.  
5. Click **Upload**.  
6. The audio should play continuously via TIMER1 interrupt.

---

## Notes

- The playback is handled entirely in the TIMER1 interrupt for precise timing.  
- Pin mapping is optimized for **fast GPIO** using direct port access (NRF_GPIO_Type).  
- Ensure your speaker or amplifier can handle the voltage levels from the DAC output.  
- Adjust `SAMPLE_RATE` in the header to match your audio file for correct playback speed.


## How to run

- Run the python script with a audio file (.wav) in the same folder. Be mindfull to change the imput_file-name to the name of the audio-file (+ fileending).
- When the python script runs successfully and creates a h-file, rename it and move it to the /cpp/DAC_R-2R/ folder.
- Then open the DAC_R-2R/ folder in Arduino IDE.
- Change the name of the header import to the proper name of the h-file that was created.
- Connect the PC to the Arduino with a USB cable, and set the board and port approperiatly.
- Compile and upload the DAC_R-2R.ino file on your system to the Arduino.
- The Audio should now be available on channel 2 as output.
