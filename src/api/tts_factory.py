from abc import abstractmethod

# import logging
#
# from src.utils.log import get_logger
# logger = get_logger(__name__)
#
# logging.getLogger('numba').setLevel(logging.WARNING)


class TTSModel(object):
    def __init__(self, cfg):
        # All config parameters turn into local variables
        self.__dict__.update(cfg)

    @abstractmethod
    def generate_speech(txt: str):
        pass

cfg = {
    "tts": {
        "config": "openai_tts_1",
        "openai_tts_1": {
          "model": "tts-1",
          "voice": "nova",
          "speed": 1.0,
          "response_format": "wav"
        }
    }
}

def tts_factory(config=cfg, working_path=None):
    """Factory for TTS model"""
    tts_config = config.get('tts').get('config')
    try:
        cfg_t = config.get('tts').get(tts_config)
    except ValueError:
        print(f"Configs for {tts_config} is not found")

    if tts_config in ['openai_tts_1']:
        from src.services.tts.tts_model_openai import TTSModel_OpenAI
        return TTSModel_OpenAI(cfg_t)
    else:
        TypeError(f"Translator config '{tts_config}' is not supported")


if __name__ == "__main__":
    import time

    # OpenAI
    if True:
        import pyaudio
        player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

        text = """I see skies of blue and clouds of white"""

        model = tts_factory()
        t0 = time.time()
        res = model.generate_speech(text)
        t1 = time.time()
        print("TTS: ", t1 - t0)
        player_stream.write(res)

        # import base64
        #
        # for chunk in speech_stream(text):
        #     # chunk1 = base64.b64encode(chunk)
        #     # chunk2 = chunk1.decode('utf-8')
        #     player_stream.write(chunk)

        t1 = time.time()
        print("TTS: ", t1-t0)

