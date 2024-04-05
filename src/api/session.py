
# Setting up environment early, before too many imports are collected
# Wierdly, from scipy.io.wavfile import write  adds unittest modules for some reason,
# switching env to test
# from src.utils.app_env import AppEnv
# env = AppEnv().flag

import base64
import os
import uuid
from datetime import datetime
import socketio
from account_manager import AccountMgr
# from src.utils.uuid_utils import mimi_id
from audio_utils import convert_webm_to_wav, convert_wav_to_mp3

from transcribe import transcribe_factory
# from src.services.tts.tts_factory import tts_factory
# from src.chat.languages import LanguageMgr

from tts import text_to_speech

UPLOAD_FOLDER = 'uploads'

# Make sure the same sio is used everywhere
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins="*")


def create_upload_folder(folder_name=UPLOAD_FOLDER):
    # Create upload folder if it doesn't exist
    try:
        os.makedirs(folder_name, exist_ok=True)
    except OSError as error:
        print("Error creating directory: ", error)


class WebsocketSession:
    def __init__(self, ws_session_id, user_id, client_platform):
        self.ws_session_id = ws_session_id
        self.client_platform = client_platform

        self.session_id = uuid.uuid4()  # ID of the current session
        print(f"Session ID: {self.session_id}")
        self.record_id = 0  # ID of the current record (message or voice)

        self.acct_mgr = AccountMgr(user_id, self.session_id)  # TODO: replace with actual user_id
        self.text = ''
        self.voice = []
        self.mode = 'text'
        self.locale = 'en'

        self.last_activity = datetime.now()

    async def add_text(self, data):
        if data == '\b':
            self.text = self.text[:-1]
        elif isinstance(data, dict) and data["payload"] == '\n':
            client_response = self.text.split('\n')[0]
            print(f'Received client response: {client_response}')
            self.text = ''
            await self.send_message(client_response, data.get("label"))
        else:
            self.text += data

    async def send_message(self, client_response, client_label):
        """Callback function to send message to user"""
        # self.acct_mgr.add_memory(client_response, self.session_id, self.record_id)
        self.record_id += 1
        res = self.acct_mgr.next_flow("from_client", client_response, client_label)
        # Switch between client-driven and server-driven chat
        if isinstance(res, dict):
            # Client-driven: message is generated immediately
            message_to_client = res
        else:
            # Server-driven: create a message on the second call to next_flow
            message_to_client = self.acct_mgr.next_flow("to_client")
        print('emit message_ack')
        await sio.emit('message_ack', message_to_client, to=self.ws_session_id)

        # TTS and voice message to client
        speech = text_to_speech(message_to_client.get('msg'))
        mp3_data = convert_wav_to_mp3(speech)
        chunk = base64.b64encode(mp3_data).decode('utf-8')
        msg = {"msg": chunk, "label": "voice"}
        await sio.emit('voice_ack', msg, to=self.ws_session_id)

        # for chunk in speech_stream(message_to_client.get('msg')):
        #     chunk = base64.b64encode(chunk).decode('utf-8')
        #     msg = {"msg": chunk, "label": "voice"}
        #     await sio.emit('voice_ack', msg, to=self.ws_session_id)

        # self.acct_mgr.add_memory(message_to_client, self.session_id, self.record_id, mimi_id)
        print(f"Record ID: {self.record_id} for session {self.ws_session_id}")
        self.record_id += 1
        return message_to_client

    async def add_voice(self, data):
        print(len(data))
        self.voice.append(data)


    async def finish_voice(self, client_label):
        print(f'Session {self.ws_session_id} finished recording voice')
        print("Total: " + str(len(self.voice)))
        # Use a generator expression to decode chunks directly into the join method for efficiency
        # audio_data_bytes = b''.join(base64.b64decode(chunk) for chunk in self.voice)
        audio_data_bytes = b''.join(base64.b64decode(chunk) for chunk in self.voice)
        wav_audio_bytes = convert_webm_to_wav(audio_data_bytes) if self.client_platform == "web" else audio_data_bytes
        self.voice = []

        # For debugging
        filename = f'{datetime.now().strftime("%Y%m%d_%H%M%S")}'
        audio_path = os.path.join(UPLOAD_FOLDER, filename)
        with open(audio_path + '.wav', 'wb') as file:
            file.write(wav_audio_bytes)
        # with open(audio_path + '.webm', 'wb') as file:
        #     file.write(audio_data_bytes)
        print(f'Audio saved to {filename}')

        # Voice-to-text
        # lang_enum = self.acct_mgr.preferred_language()
        transcript = transcribe_factory().transcribe(wav_audio_bytes)
        # Send transcribed text back to chat
        msg = {"msg": transcript, "label": "voice_transcript"}
        await sio.emit('message_ack', msg, to=self.ws_session_id)
        # Response to client
        await self.send_message(transcript, client_label)

    def change_mode(self, mode):
        self.mode = mode

    def change_locale(self, locale):
        self.locale = locale
