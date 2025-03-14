import socket
import threading
import time
import packet
from loguru import logger

HOST = '172.20.64.232'  # 服务器地址
PORT = 16701  # 服务器端口

velX = 0  # 定义为全局变量，不需要global声明


def build_packet(robot_id, velX=0, velY=0, velR=0):
    send_comd = packet.RadioPacket()
    send_comd.robotID = robot_id
    send_comd.velX = velX
    send_comd.velY = velY
    send_comd.velR = velR
    send_comd.ctrl = False
    send_comd.ctrlPowerLevel = 0.0
    send_comd.shoot = False
    send_comd.shootPowerLevel = 0.0
    send_comd.shootMode = False
    send_comd.frequency = 2
    send_comd.encode()
    return send_comd  # 去掉了time.sleep(3)，这个会导致每次build packet都很慢

def start_client(robot_id):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:  # Changed to SOCK_DGRAM for UDP
        try:
            # No need to connect for UDP
            logger.success(f"准备向服务器 {HOST}:{PORT} 发送数据 (UDP)")
            while True:
                global velX  # 声明使用全局变量velX
                send_comd = build_packet(robot_id, velX=velX)
                s.sendto(send_comd.transmitPacket, (HOST, PORT))  # 发送packet数据
                # data, addr = s.recvfrom(1024)  # 接收响应 (optional for UDP)
                # logger.info(f"收到回传：{data.decode()} 来自 {addr}")
                time.sleep(0.01)
        except Exception as e:
            logger.error(f"发生错误: {e}")
        finally:
            s.close()
            logger.info("连接已关闭")




if __name__ == '__main__':
    client1_thread = threading.Thread(target=start_client, args=(2,))
    client1_thread.daemon = True
    client1_thread.start()

    client2_thread = threading.Thread(target=start_client, args=(1,))
    client2_thread.daemon = True
    client2_thread.start()
    while True:
        s = input()
        if s == 'w':
            velX += 10
        elif s == 's':
            velX -= 10
        print(f"velX: {velX}") # 打印velX方便调试