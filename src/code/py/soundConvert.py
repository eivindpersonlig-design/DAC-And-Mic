import wave
import numpy as np
import time

# === SETTINGS ===
input_file = r"Specialz.wav"

# Create a unique output header
timestamp = time.strftime("%Y%m%d_%H%M%S")
output_header = f"audio_{timestamp}.h"

# Downsample factor (reduces sample rate)
DOWNSAMPLE = 16

# === LOAD WAV ===
with wave.open(input_file, 'rb') as wav:
    n_channels = wav.getnchannels()
    sample_width = wav.getsampwidth()
    sample_rate = wav.getframerate()
    n_frames = wav.getnframes()

    print(f"Channels: {n_channels}")
    print(f"Sample width: {sample_width * 8} bits")
    print(f"Sample rate: {sample_rate}")
    print(f"Frames: {n_frames}")

    frames = wav.readframes(n_frames)

# === CONVERT TO NUMPY ARRAY ===
if sample_width == 2:
    data = np.frombuffer(frames, dtype=np.int16)
else:
    raise ValueError("Only 16-bit WAV supported")

# === STEREO → MONO ===
if n_channels == 2:
    data = data.reshape(-1, 2)
    data = np.round(data.mean(axis=1))

# === DOWNSAMPLE ===
data = data[::DOWNSAMPLE]

# === NORMALIZE TO FULL 0–255 RANGE ===
data = data.astype(np.int32)
data = data - np.min(data)  # shift min to 0
if np.max(data) > 0:
    data = (data * 255 // np.max(data)).astype(np.uint8)
else:
    data = np.zeros_like(data, dtype=np.uint8)

# Filter out leading silence (values close to 128). Can comment out if it cuts too much.
"""
silence_threshold = 5
start = next((i for i, v in enumerate(data) if abs(int(v) - 128) > silence_threshold), 0)
data = data[start:]
"""

print("Data min:", np.min(data), "max:", np.max(data))

# === EXPORT HEADER FILE ===
with open(output_header, "w") as f:
    f.write("#pragma once\n\n")
    f.write(f"#define AUDIO_SAMPLE_RATE {sample_rate // DOWNSAMPLE}\n\n")
    f.write("const unsigned char audio[] __attribute__((section(\".rodata\"))) = {\n")

    for i, val in enumerate(data):
        f.write(f"{val}")
        if i != len(data) - 1:
            f.write(",")
        if i % 20 == 19:
            f.write("\n")

    f.write("\n};\n")
    f.write(f"const unsigned int audio_len = {len(data)};\n")

print(f"✅ Done! Generated header file: {output_header}")