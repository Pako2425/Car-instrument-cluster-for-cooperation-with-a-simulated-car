import socket
import serial
import struct
import pygame

USER_IP = "192.168.1.33"
UDP_PORT = 4685

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((USER_IP, UDP_PORT))

engineRpm = 0.0         #[17:21]
speed = 0.0             #[250:254]
gear = 0                #[314]
handBrake = 0           #[313]
distanceTraveled = 0.0  #[290:294]
fuel = 0.0              #[286:290]

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
