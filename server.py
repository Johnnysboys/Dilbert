from tornado import websocket, ioloop, web
import json
from auth import Auth
from drone import Drone
import threading
import time


class EchoWebSocket(websocket.WebSocketHandler):
    def initialize(self, auth_handler, drone_handler):
        self.auth_handler = auth_handler
        self.drone_handler = drone_handler
        self.streaming = threading.Event()
        self.streamer_thread = threading.Thread(
            target=self.stream_status, args=(self.streaming,))

    def check_origin(self, origin):
        return True

    def open(self):
        print("Websocket Opened")

    def on_message(self, message):
        request = json.loads(message)
        if not 'token' in request:
            self.write_message('No access token')
        self.auth_handler.verify_token(request['token'])

        if not 'command' in request:
            self.write_message('There is no command')
        if request['command'] == 'arm':
            self.write_message('{"status": "acknowleged", "armed": true"}')
            drone_handler.arm(True)
        if request['command'] == 'go':
            drone_handler.fucking_fly_bitch(0.3)
        if request['command'] == 'stream_status':
            self.streamer_thread.start()
        if request['command'] == 'stop_status_stream':
            self.streaming.set()

    def stream_status(self, stopper, interval=0.25):
        while not stopper.isSet():
            status = self.drone_handler.status()
            status['type'] = 'status'
            status_json = json.dumps(status, default=self.dumper, indent=2)
            self.write_message(status_json)
            time.sleep(interval)

    def dumper(self, obj):
        try:
            return obj.toJSON()
        except:
            return obj.__dict__

    def on_close(self):
        print("Websocket closed")
        self.streaming.set()
        self.streamer_thread.join()


drone_handler = Drone("tcp:127.0.0.1:5760")
auth_handler = Auth()
application = web.Application(
    [("/", EchoWebSocket, dict(auth_handler=auth_handler, drone_handler=drone_handler)), ])

if __name__ == "__main__":
    print("Connecting to drone, please wait")
    while not drone_handler.connected:
        pass

    print("Drone initialized and Server starting")
    application.listen(9000)
    ioloop.IOLoop.instance().start()
