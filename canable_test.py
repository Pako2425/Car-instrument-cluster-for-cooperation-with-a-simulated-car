import can
import time
from timeit import default_timer as timer
import pygame
pygame.init()
display = pygame.display.set_mode((100,100))

bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=125000)
msg = can.Message(arbitration_id=0x128, data=[0,90,0,0,0,0,0,0], is_extended_id=False, dlc=8)
msg_speed_and_rpm = can.Message(arbitration_id=0x0B6, data=[0,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)
msg_light_and_gear = can.Message(arbitration_id=0x128, data=[0,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)
msg_warning_lights = can.Message(arbitration_id=0x168, data=[0,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)
speed = 0 #to 65535
rpm = 0 #to 65535
gear = 0
light = 0
left = 0
right = 0
handbreak = 0

#while True:
    #try:
    #    bus.send(msg)
    #    print("Message sent")
    #except can.CanError:
    #    print("Message NOT sent")
    #
    #time.sleep(1.0)
warning_lights = [8, 0, 0, 0, 0, 0, 0, 0]
i = 7
while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                warning_lights[i] = (warning_lights[i] + 1)%256
            elif event.key == pygame.K_s:
                warning_lights[i] = (warning_lights[i] - 1) % 256
    print(bin(warning_lights[i]))


    msg_temperatureGauge = can.Message(arbitration_id=0x0F6, data=warning_lights, is_extended_id=False, dlc=8)

    try:
        #bus.send(speed_and_rpm)
        bus.send(msg_temperatureGauge)
        #bus.send(msg_warning_lights)
        print("Message sent")
    except can.CanError:
        print("Message not sent, ERROR")
    time.sleep(0.05)