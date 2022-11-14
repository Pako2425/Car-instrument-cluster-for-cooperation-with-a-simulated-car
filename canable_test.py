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

while True:
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if speed < 65000:
                    speed = speed + 1000
            elif event.key == pygame.K_s:
                if speed > 0:
                    speed = speed - 1000
            elif event.key == pygame.K_l:
                light = (light+1) % 2
            elif event.key == pygame.K_a:
                if gear < 5:
                    gear = gear + 1
            elif event.key == pygame.K_z:
                if gear > 0:
                    gear = gear - 1
            elif event.key == pygame.K_LEFT:
                left = (left + 1) % 2
            elif event.key == pygame.K_RIGHT:
                right = (right + 1) % 2
            elif event.key == pygame.K_SPACE:
                handbreak = (handbreak + 1) % 2

    a = speed & 0xFF
    b = (speed >> 8) & 0xFF
    light_and_gear_data = [0,0,0,0,0,0,0,0]
    light_and_gear_data[0] = light*64 + left*2 + right*4
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

    print(light)
    speed_and_rpm = can.Message(arbitration_id=0x0B6, data=[b, a, b, a, 0, 0, 0, 0], is_extended_id=False, dlc=8)
    msg_light_and_gear = can.Message(arbitration_id=0x128, data=light_and_gear_data, is_extended_id=False, dlc=8)
    msg_warning_lights = can.Message(arbitration_id=0x168, data=[0, 0, 0, 1, 0, 0, 0, 0], is_extended_id=False, dlc=8)

    try:
        bus.send(speed_and_rpm)
        bus.send(msg_light_and_gear)
        bus.send(msg_warning_lights)
        print("Message sent")
    except can.CanError:
        print("Message not sent, ERROR")
    time.sleep(0.1)