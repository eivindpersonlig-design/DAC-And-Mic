import argparse
from pathlib import Path
import sys
import wave

import numpy as np

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a WAV file into an Arduino-compatible header file."
    )
    parser.add_argument(
        "--input-file",
        default="Specialz.wav",
        help="Path to the source WAV file.",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
        help="Directory where the generated header should be written.",
    )
    parser.add_argument(
        "--header-name",
        default="audio_data.h",
        help="Name of the generated header file.",
    )
    parser.add_argument(
        "--downsample",
        type=int,
        default=16,
        help="Downsample factor applied before export.",
    )
    return parser.parse_args()


args = parse_args()
input_file = Path(args.input_file)
output_dir = Path(args.output_dir)
output_header = output_dir / args.header_name
DOWNSAMPLE = args.downsample

if not input_file.is_file():
    print(f"Error: input WAV file not found: {input_file}", file=sys.stderr)
    sys.exit(1)

output_dir.mkdir(parents=True, exist_ok=True)

# === LOAD WAV ===
with wave.open(str(input_file), 'rb') as wav:
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

print(f"Done. Generated header file: {output_header}")