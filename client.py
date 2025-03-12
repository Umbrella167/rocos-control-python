import socket
import threading

import packet
import time
from loguru import logger

HOST = '127.0.0.1'  # 服务器地址
PORT = 11451  # 服务器端口


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
    time.sleep(3)
    return send_comd

def start_client(robot_id):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))  # 连接服务器
            logger.success(f"成功连接到服务器 {HOST}:{PORT}")
            send_comd = build_packet(robot_id, velX=20)
            while True:
                s.sendall(send_comd.transmitPacket)  # 发送packet数据
                # data = s.recv(1024)  # 接收响应
                # logger.info(f"收到回传：{data.decode()}")
                time.sleep(0.01)
        except ConnectionRefusedError:
            logger.error("无法连接到服务器。请确保服务器已启动。")
        except Exception as e:
            logger.error(f"发生错误: {e}")
        finally:
            s.close()
            logger.info("连接已关闭")


if __name__ == '__main__':
    client1_thread = threading.Thread(target=start_client, args=(2,))
    client1_thread.daemon = True
    client1_thread.start()

    client1_thread = threading.Thread(target=start_client, args=(1,))
    client1_thread.daemon = True
    client1_thread.start()
    while True:
        time.sleep(1)
