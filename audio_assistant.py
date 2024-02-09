#!/usr/bin/python
# -*- coding: utf-8 -*-


import time
from openai import OpenAI
import pyaudio
import wave
import math
import audioop
import win32clipboard

chunk = 1024  # Record in chunks of 1024 samples
sample_format = pyaudio.paInt16  # 16 bits per sample
channels = 2
fs = 44100  # Record at 44100 samples per second
threshold = 30
silence_limit = 3
filename = "output.wav"

p = pyaudio.PyAudio()  # Create an interface to PortAudio

print('Recording')

stream = p.open(format=sample_format,
                channels=channels,
                rate=fs,
                frames_per_buffer=chunk,
                input=True)

frames = []  # Initialize array to store frames
start = time.time()
silence_start = None

# Store data in chunks until the volume is below a threshold
while True:
    data = stream.read(chunk)
    rms = audioop.rms(data, 2)  # 2 is the width in bytes of one sample
    db = 20 * math.log10(rms) if rms > 0 else 0  # Convert rms to dB
    print(f"Current volume in dB: {db}")  # Optional: for monitoring the volume
    frames.append(data)
    timer = time.time()
    if timer - start > 5:
        if db < threshold:
            if silence_start is None:
                # Start czasu ciszy
                silence_start = time.time()
            else:
                # Jak długo już trwa cisza?
                silence_duration = time.time() - silence_start
                if silence_duration > silence_limit:
                    # Jeśli cisza trwała dłużej niż ustalony limit, kończymy nagrywanie
                    print('Silence detected, stopping recording.')
                    break
        else:
            silence_start = None

# Stop and close the stream
stream.stop_stream()
stream.close()
# Terminate the PortAudio interface
p.terminate()

# Save the recorded data as a WAV file
wf = wave.open(filename, 'wb')
wf.setnchannels(channels)
wf.setsampwidth(p.get_sample_size(sample_format))
wf.setframerate(fs)
wf.writeframes(b''.join(frames))
wf.close()

print('Recording stopped')

client = OpenAI(api_key=...)

audio_file = open("output.wav", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file,
  response_format="text"
)

print(transcript)

win32clipboard.OpenClipboard()
win32clipboard.EmptyClipboard()
win32clipboard.SetClipboardText(str(transcript))
win32clipboard.CloseClipboard()

