import os
from fastapi import FastAPI
import socketio
import asyncio
from datetime import datetime, timedelta

from session import sio, WebsocketSession, create_upload_folder

TIMEOUT_SECONDS = 120  # seconds before a session is considered idle
CHECK_INTERVAL_SECONDS = 30  # seconds between checks for idle sessions


class ServerApp:
    def __init__(self):
        self.app = FastAPI()
        self.socket_app = socketio.ASGIApp(sio, other_asgi_app=self.app)
        self.sessions = {}
        self.RECORDING_DURATION = 1  # voice chunk duration in seconds
        self.register_routes()
        self.register_socket_events()
        self.idle_check_interval = CHECK_INTERVAL_SECONDS
        self.idle_timeout = timedelta(seconds=TIMEOUT_SECONDS)

        # Register startup event handler
        # self.app.on_event("startup")(self.start_background_tasks)  #TODO: uncomment when session reconnection is implemented on frontend

    # async def start_background_tasks(self):
    #     asyncio.create_task(self.check_for_idle_sessions())

    def reset_timeout(self, session_id):
        """Resets timeout timer when any activity happens within a session"""
        pass  # TODO: uncomment when session reconnection is implemented on frontend
        # self.sessions[session_id].last_activity = datetime.now()
        # print("Timeout reset")

    def register_routes(self):
        @self.app.get('/')
        async def index():
            return "Server is running."

    def register_socket_events(self):
        @sio.event
        async def connect(sid, environ):
            session_id = sid
            user_id = None  # TODO: get from headers of JWT
            client_platform = environ['QUERY_STRING'].split('&')[0].split('=')[1]
            self.sessions[session_id] = WebsocketSession(session_id, user_id, client_platform)
            self.reset_timeout(session_id)
            await sio.emit('voice_duration', self.RECORDING_DURATION, to=session_id)
            print(f'Session {session_id} connected')

        @sio.event
        async def disconnect(sid):
            session_id = sid
            if session_id in self.sessions:
                del self.sessions[session_id]
            print(f'Session {session_id} disconnected')

        @sio.event
        async def message(sid, data):
            session_id = sid
            if session_id in self.sessions:
                self.reset_timeout(session_id)
                await self.sessions[session_id].add_text(data)

        @sio.event
        async def voice(sid, data):
            session_id = sid
            if session_id in self.sessions:
                self.reset_timeout(session_id)
                await self.sessions[session_id].add_voice(data['data'])

        @sio.event
        async def voice_end(sid, data):
            session_id = sid
            if session_id in self.sessions:
                self.reset_timeout(session_id)
                await self.sessions[session_id].finish_voice(data['msgLabel'])

        @sio.event
        async def change_mode(sid, data):
            session_id = sid
            if session_id in self.sessions:
                self.reset_timeout(session_id)
                self.sessions[session_id].change_mode(data['mode'])
                print(f'Session {session_id} changed input mode to {data["mode"]}')

        @sio.event
        async def change_locale(sid, data):
            session_id = sid
            if session_id in self.sessions:
                self.reset_timeout(session_id)
                self.sessions[session_id].change_locale(data['locale'])
                print(f'Session {session_id} changed locale to {data["locale"]}')

    async def check_for_idle_sessions(self):
        while True:
            print('******* Checking Timeout ******')
            current_time = datetime.now()
            for session_id, session in list(self.sessions.items()):
                print(f"Last activity {session.last_activity} for session {session_id}")
                if current_time - session.last_activity > self.idle_timeout:
                    await sio.disconnect(session_id)
                    print(f"Session {session_id} was idle for more than {TIMEOUT_SECONDS} seconds and has been disconnected.")
            await asyncio.sleep(self.idle_check_interval)


server_app = ServerApp()

if __name__ == '__main__':
    create_upload_folder()
    import uvicorn

    uvicorn.run("app:server_app.socket_app", host='0.0.0.0', port=5000)
