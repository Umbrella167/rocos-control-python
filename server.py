import queue
import time
import serial
import packet
import socket
import threading
from loguru import logger

SER_PORT='COM6'
SER_BAUDRATE = 115200
HOST = '0.0.0.0'
PORT = 11451

packet_queue = queue.Queue(maxsize=1000)

def init_ser(port, baudrate):
    try:
        ser = serial.Serial(SER_PORT, SER_BAUDRATE)
        if not ser.is_open:
            logger.error(f"无法打开串口 {SER_PORT}")
            exit()
    except serial.SerialException as e:
        logger.error(f"串口错误: {e}")
        exit()
    # 传入第一个包
    ser.write(packet.start_packet1)
    ser.flush()
    # 等待两秒后传入第二个包
    start_time = time.time()
    while time.time() - start_time < 2:
        if ser.in_waiting > 0:
            response = ser.read_all()
            break
    time.sleep(0.1)
    ser.write(packet.start_packet2)
    ser.flush()
    logger.success(f"串口连接成功")
    return ser

def handle_client(sock, packet_queue):
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            logger.info(f"收到来自{addr}的数据：{data}, {len(data)}")
            packet_queue.put(data)  # 将数据放入队列
        except Exception as e:
            logger.error(f"处理客户端数据时发生错误: {e}")
            break

def start_server(packet_queue):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))
        logger.success(f"服务器启动，监听于 {HOST}:{PORT}")

        while True:
            handle_client(sock, packet_queue)


def serial_transmit(ser, packet_queue):
    while True:
        try:
            if not packet_queue.empty():
                transmit_packet = packet_queue.get()
                ser.write(transmit_packet)
                ser.flush()
        except Exception as e:
            logger.error(f"串口发送数据时发生错误: {e}")
            # time.sleep(1) # 发生错误后等待一段时间再重试

if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, args=(packet_queue,))
    server_thread.daemon = True
    server_thread.start()

    ser = init_ser(SER_PORT, SER_BAUDRATE)
    serial_thread = threading.Thread(target=serial_transmit, args=(ser, packet_queue))
    serial_thread.daemon = True
    serial_thread.start()

    while True:
        time.sleep(1)