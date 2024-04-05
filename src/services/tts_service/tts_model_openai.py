import time
import os
import wave

from openai import OpenAI

# from src.config.cfg_secrets import OPENAI_API_KEY
from src.services.tts.tts_factory import TTSModel

# Example of using FastAPI StreamingResponse for streaming via websockets
# https://github.com/openai/openai-python/issues/864


class TTSModel_OpenAI(TTSModel):
    def __init__(self, cfg):
        super().__init__(cfg)

    def generate_speech(self, txt: str):
        src_dir = os.path.dirname(os.getcwd())
        fila_path = os.path.join(src_dir, "output.mp3")
        with open(fila_path, 'r') as f:
            return f.read()




