import time
import os

path = os.path.join(os.path.dirname(os.getcwd()), 'services', 'output.wav')

def text_to_speech(txt):
    with open(path, 'rb') as f:
        return f.read()


if __name__ == "__main__":

    import pyaudio
    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    t0 = time.time()
    res = text_to_speech('')
    t1 = time.time()
    print("TTS: ", t1 - t0)
    player_stream. write(res)

    t1 = time.time()
    print("TTS: ", t1-t0)

