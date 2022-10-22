import can
import time

bus = can.interface.Bus(bustype='slcan', channel='COM3', bitrate=125000)

msg = can.Message(arbitration_id=0x128, data=[128,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)
fuel = can.Message(arbitration_id=0x0F6, data=[0,0,0,0,0,0,0,0], is_extended_id=False, dlc=8)

counter = 0
while(True):
    try:
        bus.send(fuel)
        print("Message sent")
    except can.CanError:
        print("Message NOT sent")

    time.sleep(1.0)