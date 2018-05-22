from __future__ import print_function
import jwt
import yaml
from tornado import websocket
import tornado.ioloop
import json
import dronekit
import time
import threading
from flight import arm_and_takeoff, land, condition_yaw


class DroneHandler:
    def __init__(self, connection_string, config_file="config.yaml"):
        self.connection_string = connection_string
        self.connected = False
        self.initialized = False
        self.vehicle = None

        thread = threading.Thread(target=self.run)
        thread.start()

    def arm(self, arg):
        self.vehicle.armed = arg

    def armed(self):
        return self.vehicle.armed

    def run(self):
        self.vehicle = dronekit.connect(
            self.connection_string, wait_ready=True)
        self.connected = True

    def stream_altitude(self):
        return self.vehicle.location.global_relative_frame.alt

    def is_created(self):
        return self.vehicle.system_status

    def initialize(self):
        print("Initalizing")
        self.vehicle.initialize()
        self.initialized = True

    def fucking_fly_bitch(self, alt):
        print("FUCKING FLYING")
        while not arm_and_takeoff(alt, self.vehicle):
            pass
        condition_yaw(360, self.vehicle, True)
        time.sleep(10)
        land(self.vehicle)


class AuthHandler:
    def __init__(self, config_file="config.yaml"):
        self.config_file = config_file
        self.config = None
        self.load_config()

    def load_config(self):
        with open("config.yaml", 'r') as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as ex:
                print(ex)

    def get_config(self, config_attribute):
        return self.config[config_attribute]

    def verify_token(self, token):
        secret = self.get_config('jwt')['secret']
        decoded = jwt.decode(token, secret)
        print(decoded)


class EchoWebSocket(websocket.WebSocketHandler):
    def initialize(self, auth_handler, drone_handler):
        self.auth_handler = auth_handler
        self.drone_handler = drone_handler

    def check_origin(self, origin):
        return True

    def open(self):
        print("Websocket Opened")

    def on_message(self, message):
        request = json.loads(message)
        # if not 'token' in request:
        #     self.write_message('No access token')
        print(request)
        if not 'command' in request:
            self.write_message('There is no command')
        if request['command'] == 'arm':
            drone_handler.arm(True)
        if request['command'] == 'go':
            print("here")
            drone_handler.fucking_fly_bitch(0.3)
        # self.auth_handler.verify_token(request['token'])

    def on_close(self):
        print("Websocket closed")


drone_handler = DroneHandler("/dev/ttyACM1")
auth_handler = AuthHandler()
application = tornado.web.Application(
    [("/", EchoWebSocket, dict(auth_handler=auth_handler, drone_handler=drone_handler)), ])

if __name__ == "__main__":
    print("Connecting to drone, please wait")
    while not drone_handler.connected:
        pass

    print("Drone initialized and Server starting")
    application.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
