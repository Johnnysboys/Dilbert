import threading
import dronekit
import time
from flight import arm_and_takeoff, condition_yaw, land, goto


class Drone:
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
            self.connection_string, wait_ready=False)
        self.connected = True

    def status(self):
        battery = self.vehicle.battery
        position = self.vehicle.location.global_relative_frame,
        mode = self.vehicle.mode
        velocity = self.vehicle.velocity
        status = {
            'position': position,
            'velocity': velocity,
            'heading':  self.vehicle.heading,
            'mode':     mode,
            'armed':    self.vehicle.armed,
            'battery':  battery
        }
        return status

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
        goto(0, 0, self.vehicle, self.vehicle.simple_goto)
        condition_yaw(0, self.vehicle, False)
        time.sleep(5)
        condition_yaw(180, self.vehicle, False)

        land(self.vehicle)
