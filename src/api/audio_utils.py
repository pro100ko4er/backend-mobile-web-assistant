import os
import subprocess


def convert_webm_to_wav(webm_data, frame_rate=16000, channgels=1):
    # Use ffmpeg to convert WebM to WAV
    process = subprocess.Popen(
        ['ffmpeg', '-i', '-', '-acodec', 'pcm_s16le', '-ar', str(frame_rate), '-ac', str(channgels), '-f', 'wav', '-'],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    wav_data, _ = process.communicate(input=webm_data)
    return wav_data


def convert_wav_to_mp3(wav_data):
    # Use ffmpeg to convert WAV to MP3
    command = ['ffmpeg', '-i', 'pipe:0', '-f', 'mp3', 'pipe:1']
    process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    mp3_data, err = process.communicate(input=wav_data)
    if process.returncode != 0:
        raise Exception(f'ffmpeg error: {err.decode()}')
    return mp3_data

