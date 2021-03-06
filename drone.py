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
            self.connection_string, wait_ready=True)
        self.connected = True

    def status(self):
        position = self.vehicle.location.global_relative_frame
        velocity = self.vehicle.velocity
        heading = self.vehicle.heading
        mode = self.vehicle.mode
        armed = self.vehicle.armed
        battery = self.vehicle.battery
        status = {
            'position': position,
            'velocity': velocity,
            'heading': heading,
            'mode': mode,
            'armed': armed,
            'battery': battery
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
        goto(1, 0, self.vehicle, self.vehicle.simple_goto)
        condition_yaw(90, self.vehicle, relative=True)
        time.sleep(10)
        condition_yaw(180, self.vehicle, False)

        land(self.vehicle)
