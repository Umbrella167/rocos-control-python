from crc8 import CCrc8
TRANSMIT_PACKET_SIZE = 25
TRANS_FEEDBACK_SIZE = 20

class Command:
    def __init__(self):
        self.power = 0.0
        self.dribble = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.vr = 0.0
        self.id = 0
        self.valid = False
        self.kick_mode = False

class RadioPacket:
    def __init__(self):
        self.robotID = 0
        self.velX = 0.0
        self.velY = 0.0
        self.velR = 0.0
        self.ctrl = False
        self.ctrlPowerLevel = 0.0
        self.shoot = False
        self.shootPowerLevel = 0.0
        self.shootMode = False
        self.frequency = 0
        self.transmitPacket = bytearray(25)  # Initialize with the correct size

    def encode(self):
        HU_CMD = Command()

        HU_CMD.valid = True
        HU_CMD.id = self.robotID
        HU_CMD.vx = self.velX
        HU_CMD.vy = self.velY
        HU_CMD.vr = self.velR
        HU_CMD.dribble = self.ctrlPowerLevel if self.ctrl else 0
        HU_CMD.power = self.shootPowerLevel if self.shoot else 0
        HU_CMD.kick_mode = self.shootMode

        tx = self.transmitPacket
        tx[:] = [0x00] * len(tx)  # Fill with 0x00
        tx[0] = 0xff
        tx[21] = ((self.frequency & 0x0f) << 4) | 0x07

        self.transmitPacket = self.encodeLegacy(HU_CMD, tx, 0)
        return True

    def encodeLegacy(self,command, tx, num):
        TXBuff = tx
        i = num
        real_num = command.id
        vx = int(command.vx)
        vy = int(command.vy)
        ivr = int(command.vr)
        vr = min(abs(ivr), 511) * (1 if ivr > 0 else -1)
        power = int(command.power)
        kick_mode = command.kick_mode
        dribble = int(command.dribble + 0.1)

        # vx
        vx_value_uint = abs(vx)
        # vy
        vy_value_uint = abs(vy)
        # w
        w_value_uint = abs(vr)

        if real_num >= 8:
            TXBuff[1] |= 0x01 << (real_num - 8)

        TXBuff[2] |= 0 if 0x01 << real_num >= 256 else 0x01 << real_num


        # dribble & kick_mode
        TXBuff[6*i + 3] = 0x01 | ((((0x01 if kick_mode else 0x00) << 2) | (0x03 & dribble)) << 4)

        # velx
        if vx < 0:
            TXBuff[6*i + 4] |= 0x20
        TXBuff[6*i + 4] |= ((vx_value_uint & 0x1f0) >> 4)
        TXBuff[6*i + 5] |= ((vx_value_uint & 0x0f) << 4)
        # vely
        if vy < 0:
            TXBuff[6*i + 5] |= 0x08
        TXBuff[6*i + 5] |= ((vy_value_uint & 0x1c0) >> 6)
        TXBuff[6*i + 6] |= ((vy_value_uint & 0x3f) << 2)
        # w
        if vr < 0:
            TXBuff[6*i + 6] |= 0x02
        TXBuff[6*i + 6] |= ((w_value_uint & 0x100) >> 8)
        TXBuff[6*i + 7] |= (w_value_uint & 0x0ff)

        # shoot power
        TXBuff[6*i + 8] = power
        return TXBuff

    def create_start_packet(self):
        self.transmitPacket = bytearray((TRANSMIT_PACKET_SIZE))
        

start_packet1 = bytearray((TRANSMIT_PACKET_SIZE))
start_packet1[0] = 0xFF
start_packet1[1] = 0xB0
start_packet1[2] = 0x01
start_packet1[3] = 0x02
start_packet1[4] = 0x03
start_packet1[TRANSMIT_PACKET_SIZE - 1] = CCrc8.calc(start_packet1[:-1], TRANSMIT_PACKET_SIZE - 1)


start_packet2 = bytearray((TRANSMIT_PACKET_SIZE))
start_packet2[0] = 0xff
start_packet2[1] = 0xb0
start_packet2[2] = 0x04
start_packet2[3] = 0x05
start_packet2[4] = 0x06
start_packet2[5] = 0x10 + 2
start_packet2[TRANSMIT_PACKET_SIZE - 1] = CCrc8.calc(start_packet2[:-1], TRANSMIT_PACKET_SIZE - 1)
