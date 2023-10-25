import argparse
from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent


class JTAG(EROTComponent):
    def __init__(self, link, *args, **kwargs):
        super(JTAG, self).__init__(link, *args, **kwargs)
        parser = argparse.ArgumentParser()
        parser.add_argument('--stepthrough', action="store_true", default=False, help='step debug')
        args, unknown = parser.parse_known_args()
        self.__stepthrough = args.stepthrough

    def Tap(self, value):
        v = self.pack_value(value)
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_TAP, fields=[[v]])
        self.link.transport(pkt)

    def IRScan(self, numbits, value):
        value = self.pad_leading_bits(numbits, value)
        if self.__stepthrough:
            while True:
                g = input(f"Put 'g' to continue IRScan {numbits} bits, {value}: ")
                if g == 'g':
                    break

        n = list(numbits.to_bytes(4,'little'))
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_IRSCAN, fields=[n, reversed(self.__str2bytes__(value))])
        x = self.link.transport(pkt)
        return x.payload.fields[-1]

    def DRScan(self, numbits, value):
        value = self.pad_leading_bits(numbits, value)
        if self.__stepthrough:
            while True:
                g = input(f"Put 'g' to continue DRScan {numbits} bits, {value}: ")
                if g == 'g':
                    break

        n = list(numbits.to_bytes(4,'little'))
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_DRSCAN, fields=[n, reversed(self.__str2bytes__(value))])
        x = self.link.transport(pkt)
        return x.payload.fields[-1]

    def Led(self, value):
        v = self.pack_value(value)
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_LED, fields=[[v]])
        self.link.transport(pkt)

    def Reset(self, value):
        v = self.pack_value(value)
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_RESET, fields=[[v]])
        self.link.transport(pkt)

    def Wait(self, numbits):
        n = list(numbits.to_bytes(4,'little'))
        pkt = PystPacket(pcomponent=EROTComponent.JTAG, proutine=EROTComponent.JTAG_WAIT, fields=[n])
        self.link.transport(pkt)

    def __str2bytes__(self, s):
        v = s.strip()
        if v.startswith('0x') or v.startswith('0X'):
            v = v[2:]
        if len(v) % 2 == 1:
            v = '0' + v
        return bytearray.fromhex(v)

    def pad_leading_bits(self, numbits, v):
        if v.startswith('0x') or v.startswith('0X'):
            v = v[2:]
        if len(v) % 2 == 1:
            v = '0' + v
        n_pad = (numbits+3)//4*4 - len(v) * 4
        v = '0' * (n_pad//4) + v
        return v
