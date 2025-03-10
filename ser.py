import serial
import pocket
import time

if __name__ == "__main__":

    ser = serial.Serial('/dev/ttyUSB0', 115200)

    if ser.is_open:
        print('Open')
    else:
        print('Close')
        exit()

    ser.write(pocket.start_packet1)
    ser.flush()

    start_time = time.time()
    while time.time() - start_time < 2:
        if ser.in_waiting > 0:
            response = ser.read_all()
            break
    # Send second start packet

    time.sleep(0.1)
    ser.write(pocket.start_packet2)
    ser.flush()
    print(pocket.start_packet2)

    send_comd = pocket.RadioPacket()
    send_comd.robotID = 2
    send_comd.velX = 50
    send_comd.velY = 0.0
    send_comd.velR = 0.0
    send_comd.ctrl = False
    send_comd.ctrlPowerLevel = 0.0
    send_comd.shoot = False
    send_comd.shootPowerLevel = 0.0
    send_comd.shootMode = False
    send_comd.frequency = 2
    send_comd.encode()
    time.sleep(3)

    while True:
        ser.write(send_comd.transmitPacket)
        ser.flush()
        time.sleep(0.01)