import socket
import can
import time
from timeit import default_timer as timer
import struct
import pygame
from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    def __init__(self, next, socket, bus):
        self.next = next
        self.sock = socket
        self.bus = bus

    @abstractmethod
    def processData(self, data):
        pass

    #@abstractmethod
    def handle(self, data=0):
        data = self.processData(data)
        if self.next is None:
            return
        else:
            self.next.handle(data)

class ReceiveData(AbstractHandler):
    def processData(self, data):
        recvData = self.sock.recvfrom(324)
        return recvData[0]

class DataProcessing(AbstractHandler):
    def processData(self, data):
        data_to_send = [0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0]
        data_to_send[0] = struct.unpack('f', data[16:20])[0]                #engineRPM
        data_to_send[1] = struct.unpack('f', data[256:260])[0]              #speed
        data_to_send[2] = struct.unpack('f', data[288:292])[0]              #fuel
        data_to_send[3] = struct.unpack('f', data[292:296])[0]              #distanceTraveled
        data_to_send[4] = struct.unpack('f', data[84:88])[0]                #flTireGrip
        data_to_send[5] = struct.unpack('f', data[88:92])[0]                #frTireGrip
        data_to_send[6] = struct.unpack('f', data[92:96])[0]                #blTireGrip
        data_to_send[7] = struct.unpack('f', data[96:100])[0]               #brTireGrip
        data_to_send[8] = struct.unpack('f', data[20:24])[0]                #accelerationX
        data_to_send[9] = struct.unpack('f', data[28:32])[0]                #accelerationZ
        data_to_send[10] = struct.unpack('H', data[318:319] + b'\x00')[0]   #handbrake
        data_to_send[11] = struct.unpack('H', data[319:320] + b'\x00')[0]   #gear
        return data_to_send

class SendData(AbstractHandler):
    def prepare_to_send(self, data):
        rpm = int(data[0] * 8.200)
        speed = int(data[1] * 357.142)
        fuel_level = int(data[2] * 100.0)
        print(fuel_level)
        handBreak = data[10]

        data_speedAndRpm = [(rpm >> 8 & 0xFF), (rpm & 0xFF), (speed >> 8 & 0xFF), (speed & 0xFF), 0, 0, 0, 0]

        data_lightsAndGear = [0,0,0,0,0,0,0,0]
        if data[11] == 0:
            data_lightsAndGear[1] = 16
        elif data[11] == 1:
            data_lightsAndGear[1] = 144
        elif data[11] == 2:
            data_lightsAndGear[1] = 128
        elif data[11] == 3:
            data_lightsAndGear[1] = 112
        elif data[11] == 4:
            data_lightsAndGear[1] = 96
        elif data[11] == 5:
            data_lightsAndGear[1] = 80
        else:
            data_lightsAndGear[1] = 64

        data_warningLights = [255, 255, 255, 16, 255, 255, 255, 255]

        data_fuelGauge = [0, 0, 0, fuel_level, 0, 0, 0, 0]
        data_temperature = [8,0,0,0,0,0,0,0]

        return [data_speedAndRpm, data_lightsAndGear, data_fuelGauge, data_warningLights]

    def send(self, data):
        msg_fuelGauge = can.Message(arbitration_id=0x161, data=[2], is_extended_id=False, dlc=8)
        msg_temperatureGauge = can.Message(arbitration_id=0x0F6, data=[8,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)
        msg_speedAndRpm = can.Message(arbitration_id=0x0B6, data=data[0], is_extended_id=False, dlc=8)
        msg_lightsAndGear = can.Message(arbitration_id=0x128, data=data[1], is_extended_id=False, dlc=8)
        msg_warning_lights = can.Message(arbitration_id=0x168, data=[0,0,0,1,0,0,0,0], is_extended_id=False, dlc=8)
        try:
            self.bus.send(msg_temperatureGauge)
            self.bus.send(msg_fuelGauge)
            self.bus.send(msg_speedAndRpm)
            self.bus.send(msg_lightsAndGear)
            self.bus.send(msg_warning_lights)

            print("Message sent")
        except can.CanError:
            print("Message NOT sent")

    def processData(self, data):
        data_to_bus = self.prepare_to_send(data)
        self.send(data_to_bus)

class Receiver:
    def __init__(self, RECEIVER_IP, UDP_PORT):
        self.RECEIVER_IP = RECEIVER_IP
        self.UDP_PORT = UDP_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.RECEIVER_IP, self.UDP_PORT))
        self.bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=125000)
        self.sd = SendData(None, None, self.bus)
        self.dp = DataProcessing(self.sd, None, None)
        self.r = ReceiveData(self.dp, self.sock, None)

        while True:
            self.r.handle()

    def receive(self):
        recvData = self.sock.recvfrom(324)
        return recvData[0]

Receiver = Receiver("192.168.8.102", 5555)
