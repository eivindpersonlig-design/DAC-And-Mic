.PHONY: clean build run_py run_cpp run run_full

SHELL := /bin/sh

ARDUINO_CLI ?= arduino-cli
PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null || echo python)
BOARD_FQBN := arduino:mbed_nano:nano33ble
PORT ?=
ROOT_DIR := .
PY_DIR := $(ROOT_DIR)/src/code/py
CPP_DIR := $(ROOT_DIR)/src/code/cpp/DAC_R-2R
SOUND_DIR := $(ROOT_DIR)/src/sound
GENERATED_HEADER := audio_data.h
SOUND_HEADER := $(SOUND_DIR)/$(GENERATED_HEADER)
CPP_HEADER := $(CPP_DIR)/$(GENERATED_HEADER)
BUILD_DIR := $(CPP_DIR)/build
WAV_FILE ?= $(firstword $(wildcard $(SOUND_DIR)/*.wav))

clean:
	@echo "Cleaning..."
	@$(PYTHON) -c "from pathlib import Path; import shutil; paths = [Path('$(SOUND_HEADER)'), Path('$(CPP_HEADER)')]; build_dir = Path('$(BUILD_DIR)'); [path.unlink() for path in paths if path.exists()]; shutil.rmtree(build_dir, ignore_errors=True)"
	@echo "Cleaning completed."

build:
	@echo "Building..."
	@command -v $(ARDUINO_CLI) >/dev/null 2>&1 || { echo "Error: arduino-cli not found in PATH"; exit 1; }
	@$(ARDUINO_CLI) core update-index
	@$(ARDUINO_CLI) core install arduino:mbed_nano
	@echo "Build completed."

run_py:
	@echo "Running Python script..."
	@test -n "$(strip $(WAV_FILE))" || { echo "Error: no .wav file found in $(SOUND_DIR). Set WAV_FILE=path/to/file.wav or add one .wav file there."; exit 1; }
	@test -f "$(WAV_FILE)" || { echo "Error: WAV file not found: $(WAV_FILE)"; exit 1; }
	@$(PYTHON) $(PY_DIR)/soundConvert.py --input-file "$(WAV_FILE)" --output-dir "$(SOUND_DIR)" --header-name "$(GENERATED_HEADER)"
	@test -f "$(SOUND_HEADER)" || { echo "Error: Python conversion did not produce $(SOUND_HEADER)"; exit 1; }
	@echo "Python script completed."

run_cpp:
	@echo "Running C++ program..."

	@echo "Reading .h-file and converting to audio on DAC..."
	@test -n "$(strip $(PORT))" || { echo "Error: set PORT to the serial port for your board, for example PORT=COM3 on Windows or PORT=/dev/ttyACM0 on Linux."; exit 1; }
	@command -v $(ARDUINO_CLI) >/dev/null 2>&1 || { echo "Error: arduino-cli not found in PATH"; exit 1; }
	@$(PYTHON) -c "from pathlib import Path; import shutil; src = Path('$(SOUND_HEADER)'); dst = Path('$(CPP_HEADER)'); dst.write_bytes(src.read_bytes())"
	@$(ARDUINO_CLI) compile --fqbn $(BOARD_FQBN) --output-dir "$(BUILD_DIR)" "$(CPP_DIR)"
	@$(ARDUINO_CLI) upload -p $(PORT) --fqbn $(BOARD_FQBN) --build-path "$(BUILD_DIR)" "$(CPP_DIR)"
	
	@echo "C++ program completed."

run: run_py run_cpp

run_full: build run clean