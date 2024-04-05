import wave
import tempfile
import os.path
from abc import abstractmethod

from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
from src.config.cfg_secrets import GOOGLE_SERVICE_ACCOUNT


class Transcribe(object):
    def __init__(self, cfg, client=None):
        self.cfg = cfg
        self.client = client

    @abstractmethod
    def transcribe(self, audio_content):
        pass


class Transcribe_Google(Transcribe):
    def __init__(self, cfg):
        credentials = service_account.Credentials.from_service_account_info(GOOGLE_SERVICE_ACCOUNT)
        client = speech.SpeechClient(credentials=credentials)
        super().__init__(cfg, client)

    def transcribe(self, audio_content):
        lang = 'en-us'
        try:
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=lang,
            )

            response = self.client.recognize(config=config, audio=audio)
            print(response)
            transcription = '\n'.join(
                result.alternatives[0].transcript for result in response.results
            )
            print('Transcription:', transcription)
            return transcription
        except Exception as e:
            print('Error transcribing audio:', str(e))
            return str(e)


cfg = {
    "transcribe": {
        "config": "google",
        "google": {}
    }
}

def transcribe_factory(config=cfg):
    """Factory returns an appropriate """
    stt_config = config.get('transcribe').get('config')
    cfg_g = config.get('transcribe').get(stt_config)
    if stt_config == "google":
        return Transcribe_Google(cfg_g)
    else:
        TypeError(f"Transcribe config '{stt_config} is not supported")


if __name__ == "__main__":
    # Google

    src_dir = os.path.dirname(os.getcwd())
    fila_path = os.path.join(src_dir, "services", "rec.wav")
    with wave.open(fila_path, 'r') as wav_file:

        # Extract audio parameters
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        framerate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        comp_type = wav_file.getcomptype()
        comp_name = wav_file.getcompname()

        print(f"Number of channels: {n_channels}")
        print(f"Sample width: {sample_width}")
        print(f"Frame rate (sample rate): {framerate}")
        print(f"Number of frames: {n_frames}")
        print(f"Compression type: {comp_type}")
        print(f"Compression name: {comp_name}")

        # Read and return the audio frames
        audio_frames = wav_file.readframes(n_frames)

    transcript = transcribe_factory().transcribe(audio_frames)
    print(transcript)
