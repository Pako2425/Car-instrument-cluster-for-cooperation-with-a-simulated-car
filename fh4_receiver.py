import socket
import can
import time
from timeit import default_timer as timer
import threading
import struct
import pygame


class Receiver:
    def __init__(self, RECEIVER_IP, UDP_PORT):
        self.RECEIVER_IP = RECEIVER_IP
        self.UDP_PORT = UDP_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.RECEIVER_IP, self.UDP_PORT))
        self.bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=125000)

        self.data_speedAndRpm = [0,0,0,0,0,0,0,0]
        self.data_lightsAndGear = [0,0,0,0,0,0,0,0]
        self.data_warningLights = [0,0,0,0,0,0,0,0]


    def receive(self):
        recvData = self.sock.recvfrom(324)
        self.telemetry = recvData[0]

    def processingTelemetryData(self):
        self.engineRpm = struct.unpack('f', self.telemetry[16:20])[0]
        self.speed = struct.unpack('f', self.telemetry[256:260])[0]
        self.fuel = struct.unpack('f', self.telemetry[288:292])[0]
        self.distanceTraveled = struct.unpack('f', self.telemetry[292:296])[0]
        self.flTireGrip = struct.unpack('f', self.telemetry[84:88])[0]
        self.frTireGrip = struct.unpack('f', self.telemetry[88:92])[0]
        self.blTireGrip = struct.unpack('f', self.telemetry[92:96])[0]
        self.brTireGrip = struct.unpack('f', self.telemetry[96:100])[0]
        self.accelerationX = struct.unpack('f', self.telemetry[20:24])[0]
        self.accelerationZ = struct.unpack('f', self.telemetry[28:32])[0]
        self.handBrake = struct.unpack('H', self.telemetry[318:319] + b'\x00')[0]
        self.gear = struct.unpack('H', self.telemetry[319:320] + b'\x00')[0]

    def processingDataForCluster(self):
        #speed = int(self.speed * 1072.404)
        speed = int(self.speed * 357.142)
        rpm = int(self.engineRpm * 8.0)
        self.data_speedAndRpm = [(rpm >> 8 & 0xFF), (rpm & 0xFF), (speed >> 8 & 0xFF), (speed & 0xFF), 0, 0, 0, 0]
        if self.gear == 0:
            self.data_lightsAndGear[1] = 16
        elif self.gear == 1:
            self.data_lightsAndGear[1] = 144

        elif self.gear == 2:
            self.data_lightsAndGear[1] = 128

        elif self.gear == 3:
            self.data_lightsAndGear[1] = 112

        elif self.gear == 4:
            self.data_lightsAndGear[1] = 96

        elif self.gear == 5:
            self.data_lightsAndGear[1] = 80

        else:
            self.data_lightsAndGear[1] = 16

    def send(self):
        msg_speedAndRpm = can.Message(arbitration_id=0x0B6, data=self.data_speedAndRpm, is_extended_id=False, dlc=8)
        msg_lightsAndGear = can.Message(arbitration_id=0x128, data=self.data_lightsAndGear, is_extended_id=False, dlc=8)
        msg_warning_lights = can.Message(arbitration_id=0x168, data=[0, 0, 0, 1, 0, 0, 0, 0], is_extended_id=False, dlc=8)
        try:
            self.bus.send(msg_speedAndRpm)
            self.bus.send(msg_lightsAndGear)
            self.bus.send(msg_warning_lights)
            print("Message sent")
        except can.CanError:
            print("Message NOT sent")

Receiver = Receiver("192.168.0.136", 5555)

while True:
    start = timer()
    Receiver.receive()
    Receiver.processingTelemetryData()
    Receiver.processingDataForCluster()
    Receiver.send()
    end = timer()
    print(end - start)




#start = timer()
#speed_and_rpm
#speed = 10.0             #m/s
#s = int(speed*1072.404)  #m/s to km/h and speed to cluster resolution
#rpm = 4000.0
#r = int(rpm*9.362)
#data_speedAndRpm = [(s>>8 & 0xFF), (s & 0xFF), (r>>8 & 0xFF), (r & 0xFF), 0, 0, 0, 0]
"""
gear = 1
light_and_gear_data = [0,0,0,0,0,0,0,0]
if gear == 0:
    light_and_gear_data[1] = 16
elif gear == 1:
    light_and_gear_data[1] = 144

elif gear == 2:
    light_and_gear_data[1] = 128

elif gear == 3:
    light_and_gear_data[1] = 112

elif gear == 4:
    light_and_gear_data[1] = 96

elif gear == 5:
    light_and_gear_data[1] = 80

else:
    light_and_gear_data[1] = 16

end = timer()
print(end - start)
"""

"""
pygame.init()
window_size = (400,400)
window = pygame.display.set_mode(window_size)
black = pygame.color.Color('#000000')
green = pygame.color.Color('#32CD32')
yellow = pygame.color.Color('#DDDDDD')
font = pygame.font.Font(None, 30)

while(True):
    recvData = sock.recvfrom(324)
    telemetry = recvData[0]

    engineRpm = struct.unpack('f', telemetry[16:20])[0]
    speed = struct.unpack('f', telemetry[256:260])[0]
    fuel = struct.unpack('f', telemetry[288:292])[0]
    distanceTraveled = struct.unpack('f', telemetry[292:296])[0]
    flTireGrip = struct.unpack('f', telemetry[84:88])[0]
    frTireGrip = struct.unpack('f', telemetry[88:92])[0]
    blTireGrip = struct.unpack('f', telemetry[92:96])[0]
    brTireGrip = struct.unpack('f', telemetry[96:100])[0]
    accelerationX = struct.unpack('f', telemetry[20:24])[0]
    accelerationZ = struct.unpack('f', telemetry[28:32])[0]
    handBrake = struct.unpack('H', telemetry[318:319]+b'\x00')[0]
    gear = struct.unpack('H', telemetry[319:320]+b'\x00')[0]

    window.fill(black)
    window.blit(font.render(f"engine_RPM: {format(engineRpm, '.3f')}", False, green), (20, 20))
    window.blit(font.render(f"speed m/s: {format(speed, '.3f')}", False, green), (20, 45))
    window.blit(font.render(f"fuel: {fuel}", False, green), (20, 70))
    window.blit(font.render(f"distanceTraveled: {distanceTraveled}", False, green), (20, 95))
    window.blit(font.render(f"flTireGrip: {format(flTireGrip, '.1f')}", False, green), (20, 120))
    window.blit(font.render(f"frTireGrip: {format(frTireGrip, '.1f')}", False, green), (20, 145))
    window.blit(font.render(f"blTireGrip: {format(blTireGrip, '.1f')}", False, green), (20, 170))
    window.blit(font.render(f"brTireGrip: {format(brTireGrip, '.1f')}", False, green), (20, 195))
    window.blit(font.render(f"acceX <-> m/s: {format(accelerationX, '.1f')}", False, green), (20, 220))
    window.blit(font.render(f"acceY  ^  m/s: {format(accelerationZ, '.1f')}", False, green), (20, 245))
    window.blit(font.render(f"handBrake: {handBrake}", False, green), (20, 270))
    window.blit(font.render(f"gear: {gear}", False, green), (20, 295))
    pygame.display.flip()
"""