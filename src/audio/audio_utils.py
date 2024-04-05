import os
import subprocess


def convert_webm_to_wav(webm_data, frame_rate=16000, channgels=1):
    # Use ffmpeg to convert WebM to WAV
    process = subprocess.Popen(
        ['ffmpeg', '-i', '-', '-acodec', 'pcm_s16le', '-ar', str(frame_rate), '-ac', str(channgels), '-f', 'wav', '-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, _ = process.communicate(input=webm_data)
    return wav_data

