import socket
import can
import time
from timeit import default_timer as timer
import struct
from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    def __init__(self, next, socket, bus):
        self.next = next
        self.sock = socket
        self.bus = bus

    @abstractmethod
    def handler(self, data):
        pass

    def handle(self, data=0):
        data = self.handler(data)
        if self.next is None:
            return
        else:
            self.next.handle(data)


class DataReceivingHandler(AbstractHandler):
    def handler(self, data):
        recvData = self.sock.recvfrom(324)
        return recvData[0]


class DataProcessingHandler(AbstractHandler):

    def rawTelemetryDataProcessing(self, rawTelemetryData):
        engineRpm = struct.unpack('f', rawTelemetryData[16:20])[0]
        speed     = struct.unpack('f', rawTelemetryData[256:260])[0]
        fuel      = struct.unpack('f', rawTelemetryData[288:292])[0]
        gear      = struct.unpack('H', rawTelemetryData[319:320] + b'\x00')[0]
        accelerationX = struct.unpack('f', rawTelemetryData[20:24])[0]
        accelerationZ = struct.unpack('f', rawTelemetryData[28:32])[0]

        return [engineRpm, speed, fuel, gear, accelerationX, accelerationZ]

    def prepareDataForCanMessage(self, processedTelemetryData):
        rpm = int(processedTelemetryData[0] * 8.200)
        speed = int(processedTelemetryData[1] * 357.142)
        fuel_level = int(processedTelemetryData[2] * 100.0)
        gear = processedTelemetryData[3]
        accX = processedTelemetryData[4]
        accY = processedTelemetryData[5]

        data_clusterState   = [8, 0, 0, 0, 0, 0, 0, 0]
        data_warningLights = [0, 0, 0, 1, 0, 0, 0, 0]
        data_fuelGauge     = [0, 0, 0, fuel_level, 0, 0, 0, 0]
        data_speedAndRpm = [(rpm >> 8 & 0xFF), (rpm & 0xFF), (speed >> 8 & 0xFF), (speed & 0xFF), 0, 0, 0, 0]
        data_lightsAndGear = [0, 0, 0, 0, 0, 0, 0, 0]

        if gear == 0:
            data_lightsAndGear[1] = 16
        elif gear == 1:
            data_lightsAndGear[1] = 144
        elif gear == 2:
            data_lightsAndGear[1] = 128
        elif gear == 3:
            data_lightsAndGear[1] = 112
        elif gear == 4:
            data_lightsAndGear[1] = 96
        elif gear == 5:
            data_lightsAndGear[1] = 80
        else:
            data_lightsAndGear[1] = 6

        if pow(accX*accX + accY*accY, 0.5) > 10:
            data_warningLights[0] = 8       #niskie cisnienie oleju
            data_warningLights[2] = 1       #check engine
            data_warningLights[4] = 36      #awaria ukladu wspomagania kierowniczego i awaria systemu SRS
            data_lightsAndGear[0] = 254     #wszystkie kontrolki oświetlenia samochodowego
            data_lightsAndGear[3] = 144     #napis SERVICE na obrotomierzu i aktywacja poduszki pasażera

        return [data_clusterState, data_warningLights, data_fuelGauge, data_lightsAndGear, data_speedAndRpm]

    def handler(self, data):
        return self.prepareDataForCanMessage(self.rawTelemetryDataProcessing(data))


class DataSendingHandler(AbstractHandler):
    def send(self, dataToSend):
        msg_clusterState   = can.Message(arbitration_id=0x0F6, data=dataToSend[0], is_extended_id=False, dlc=8)
        msg_warning_lights = can.Message(arbitration_id=0x168, data=dataToSend[1], is_extended_id=False, dlc=8)
        msg_fuelGauge      = can.Message(arbitration_id=0x161, data=dataToSend[2], is_extended_id=False, dlc=8)
        msg_lightsAndGear  = can.Message(arbitration_id=0x128, data=dataToSend[3], is_extended_id=False, dlc=8)
        msg_speedAndRpm    = can.Message(arbitration_id=0x0B6, data=dataToSend[4], is_extended_id=False, dlc=8)
        try:
            self.bus.send(msg_clusterState)
            self.bus.send(msg_warning_lights)
            self.bus.send(msg_fuelGauge)
            self.bus.send(msg_lightsAndGear)
            self.bus.send(msg_speedAndRpm)
            print("Message sent")
        except can.CanError:
            print("Message NOT sent")

    def handler(self, data):
        self.send(data)

class Receiver:
    def __init__(self, RECEIVER_IP, UDP_PORT, CAN_BUS_CHANNEL):
        self.RECEIVER_IP = RECEIVER_IP
        self.UDP_PORT = UDP_PORT
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.RECEIVER_IP, self.UDP_PORT))
        self.bus = can.interface.Bus(bustype='slcan', channel=CAN_BUS_CHANNEL, bitrate=125000)
        self.DataSender = DataSendingHandler(None, None, self.bus)
        self.DataProcessor = DataProcessingHandler(self.DataSender, None, None)
        self.DataReceiver = DataReceivingHandler(self.DataProcessor, self.sock, None)

        while True:
            self.DataReceiver.handle()


if __name__ == "__main__":
    Receiver = Receiver("192.168.8.102", 5555, 'COM3')
