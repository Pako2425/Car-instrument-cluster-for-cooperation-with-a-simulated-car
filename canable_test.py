import can
import time

bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=125000)

msg = can.Message(arbitration_id=0x128, data=[0,90,0,0,0,0,0,0], is_extended_id=False, dlc=8)
fuel = can.Message(arbitration_id=0x0B6, data=[50,255,50,255,0,0,0,0], is_extended_id=False, dlc=8)

counter = 0
while(True):
    try:
        bus.send(msg)
        print("Message sent")
    except can.CanError:
        print("Message NOT sent")

    time.sleep(1.0)