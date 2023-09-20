import random
from itertools import chain
from RoPy.Pyst.py.PystParam import *


class PystPacketHeader:
    """
    order |--->
    n_bytes     4     4       4      4         1           x               x           ...        x
    name      [id]  [type] [comp] [rout] [n_fields] [n_byte_field 0] [n_byte_field 1] ... [[n_byte_field X]
    """

    def __init__(self, pid=0, ptype=PacketType.WRITE, pcomponent=0, proutine=0, n_each_field_bytes=None):
        super(PystPacketHeader, self).__init__()
        self.set_pid(pid)
        self.type = ptype
        self.component= pcomponent
        self.routine = proutine
        self.n_each_field_bytes = n_each_field_bytes if n_each_field_bytes else []
        self.n_fields = len(self.n_each_field_bytes)
        self.n_total_field_bytes = sum(self.n_each_field_bytes)
        self.bytes = self.to_bytes()

    def to_bytes(self):
        ans = self.pid.to_bytes(Param.N_ID_BYTES, Param.BYTE_ORDER) + \
              self.type.to_bytes(Param.N_TYPE_BYTES, Param.BYTE_ORDER) + \
              self.component.to_bytes(Param.N_PORT_BYTES, Param.BYTE_ORDER) + \
              self.routine.to_bytes(Param.N_USER_BYTES, Param.BYTE_ORDER) + \
              self.n_fields.to_bytes(Param.N_NBR_FIELD_BYTES, Param.BYTE_ORDER)
        for i in self.n_each_field_bytes:
            ans += int(i).to_bytes(Param.N_EACH_NBR_FIELD_BYTES, Param.BYTE_ORDER)
        return ans

    def set_pid(self, pid=None, client_id=None, thread_id=None, pkt_nbr=None):
        # client id | thread id | pkt nbr
        if pid is not None:
            self.pid = pid
            self.client_id = pid >> 24
            self.thread_id = (pid >> 16) & 0xff
            self.pkt_nbr = pid  & 0xffff
        elif client_id is not None and thread_id is not None and pkt_nbr is not None:
            self.client_id = client_id
            self.thread_id = thread_id
            self.pkt_nbr = pkt_nbr
            self.pid = client_id << 24 | thread_id << 16 | pkt_nbr
        else:
            rpfatal(f"Please provide correct pid")

    def __str__(self):
        s = f"---------- Header -----------\n"
        s += f"id: {self.pid}\n"
        s += f"client id: {self.client_id}\n"
        s += f"thread id: {self.thread_id}\n"
        s += f"packet number: {self.pkt_nbr}\n"
        s += f"type: {self.type.name}\n"
        s += f"component: {self.component}\n"
        s += f"routine: {self.routine}\n"
        s += f"n_fields: {self.n_fields}\n"
        for i, n in enumerate(self.n_each_field_bytes):
            s += f"field #{i}: {n} bytes\n"
        s += f"total bytes in payload: {self.n_total_field_bytes}\n"
        s += f"header bytes: {bytes_stringfy(self.bytes)}\n"
        return s


class PystPacketPayload:
    def __init__(self, n_each_field_bytes=None, fields=None, byte_stream=None):
        super(PystPacketPayload, self).__init__()

        def field_to_bytes(field):
            t = bytearray()
            for int_val in field:
                if int_val == 0:
                    t += b"\x00"  # (0).to_bytes returns empty byte array, manually define it
                elif isinstance(int_val, bytes) or isinstance(int_val, bytearray):
                    t += int_val
                else:
                    t += int_val.to_bytes((int_val.bit_length() + 7) // 8, byteorder=Param.BYTE_ORDER)
            max_lim = (1<<(Param.N_EACH_NBR_FIELD_BYTES*8)) - 1
            if len(t) > max_lim:
                rpfatal(f"Field byte length exceeds max allowed limit {max_lim}")
            return t

        self.bytes = bytearray()
        self.fields = []
        self.n_each_field_bytes = []

        if byte_stream:
            field_byte_offset = Param.N_ID_BYTES + Param.N_TYPE_BYTES + Param.N_PORT_BYTES + Param.N_USER_BYTES
            n_fields = int(byte_stream[field_byte_offset])
            n_each_fld_srt = field_byte_offset + 1
            n_each_fld_end = field_byte_offset + 1 + n_fields * Param.N_EACH_NBR_FIELD_BYTES
            for i in range(n_each_fld_srt, n_each_fld_end, Param.N_EACH_NBR_FIELD_BYTES):
                self.n_each_field_bytes.append(int.from_bytes(byte_stream[i: i+Param.N_EACH_NBR_FIELD_BYTES], byteorder=Param.BYTE_ORDER))
            self.bytes = byte_stream[n_each_fld_end:n_each_fld_end+sum(self.n_each_field_bytes)]
            s = 0
            for n in self.n_each_field_bytes:
                self.fields.append(self.bytes[s:s + n])
                s += n
        elif fields:
            fs = None
            if dim(fields) == 0:
                fs = [[fields]]
            elif dim(fields) == 1:
                fs = [fields]
            elif dim(fields) == 2:
                fs = fields
            else:
                rpfatal("input data fields should have dimension number <= 2")

            for f in fs:
                x = field_to_bytes(f)
                self.bytes += x
                self.fields.append(x)
                self.n_each_field_bytes.append(len(x))
        else:
            if n_each_field_bytes and sum(n_each_field_bytes) == 0:
                rpfatal(
                    f"Check input field byte format, each field byte number should > 0, get {self.n_each_field_bytes}")
            self.n_each_field_bytes = n_each_field_bytes if n_each_field_bytes else []
            self.fields = [[Param.FIELD_BYTE_DEFAULT_VALUE] * n for n in self.n_each_field_bytes]
            self.fields = [field_to_bytes(f) for f in self.fields]
            for f in self.fields:
                self.bytes += f

    def __str__(self):
        s = f"---------- Payload -----------\n"
        for i, f in enumerate(self.fields):
            s += f"field #{i}, {self.n_each_field_bytes[i]} bytes: {bytes_stringfy(f)}\n"
        s += f"payload bytes: {bytes_stringfy(self.bytes)}\n"
        return s


class PystPacket:
    def __init__(self, pid=0, ptype=PacketType.WRITE, pcomponent=0, proutine=0, n_each_field_bytes=None, fields=None, byte_stream=None):
        super(PystPacket, self).__init__()

        if byte_stream:
            self.pid = int.from_bytes(byte_stream[0 : Param.N_ID_BYTES], byteorder=Param.BYTE_ORDER)
            self.ptype = PacketType(int.from_bytes(byte_stream[Param.N_ID_BYTES : Param.N_ID_BYTES + Param.N_TYPE_BYTES],
                                                   byteorder=Param.BYTE_ORDER))
            self.pcomponent = int.from_bytes(byte_stream[Param.N_ID_BYTES + Param.N_TYPE_BYTES : Param.N_ID_BYTES + Param.N_TYPE_BYTES + Param.N_PORT_BYTES],
                                                   byteorder=Param.BYTE_ORDER)
            self.proutine = int.from_bytes(byte_stream[Param.N_ID_BYTES + Param.N_TYPE_BYTES + Param.N_PORT_BYTES : Param.N_ID_BYTES + Param.N_TYPE_BYTES + Param.N_PORT_BYTES + Param.N_USER_BYTES],
                                                   byteorder=Param.BYTE_ORDER)
        else:
            self.pid = pid
            self.ptype = ptype
            self.pcomponent = pcomponent
            self.proutine = proutine

        self.payload = PystPacketPayload(n_each_field_bytes=n_each_field_bytes,
                                         fields=fields,
                                         byte_stream=byte_stream)
        self.header = PystPacketHeader(pid=self.pid,
                                       ptype=self.ptype,
                                       pcomponent=self.pcomponent,
                                       proutine=self.proutine,
                                       n_each_field_bytes=self.payload.n_each_field_bytes)
        self.bytes = self.header.bytes + self.payload.bytes
        if len(self.bytes) > Param.MAX_PACKET_TOTAL_BYTES_LIMIT:
            rpfatal(f"Packet byte length exceeds max allowed limit {Param.MAX_PACKET_TOTAL_BYTES_LIMIT}")

    def rebuild(self):
        self.pid = self.header.pid
        self.ptype = self.header.type
        self.pcomponent = self.header.component
        self.proutine = self.header.routine
        self.header.bytes = self.header.to_bytes()
        self.bytes = self.header.bytes + self.payload.bytes
        
    def __str__(self):
        s = f"|------------ Packet -------------|\n"
        s += str(self.header)
        s += str(self.payload)
        s += f"packet bytes: {bytes_stringfy(self.bytes)}\n"
        return s


def generate_random_packet(pid=None, ptype=None, pcomponent=None, proutine=None, max_n_fields=5, max_each_fields_bytes=15):
    pid = pid if pid is not None else random.randint(0, (1<<(Param.N_ID_BYTES*8))-1)
    ptype = ptype if ptype is not None else PacketType.WRITE
    pcomponent = pcomponent if pcomponent is not None else 0
    proutine = proutine if proutine is not None else 0
    n_fields = random.randint(0, max_n_fields)
    n_each_field_bytes = [random.randint(0, max_each_fields_bytes) for i in range(n_fields)]
    data = list(chain.from_iterable([random.sample(range(0, 255), k) for k in n_each_field_bytes]))
    byte_stream = pid.to_bytes(Param.N_ID_BYTES, Param.BYTE_ORDER) + \
                  ptype.to_bytes(Param.N_TYPE_BYTES, Param.BYTE_ORDER) + \
                  pcomponent.to_bytes(Param.N_PORT_BYTES, Param.BYTE_ORDER) + \
                  proutine.to_bytes(Param.N_USER_BYTES, Param.BYTE_ORDER) + \
                  n_fields.to_bytes(Param.N_NBR_FIELD_BYTES, Param.BYTE_ORDER)
    for i in n_each_field_bytes:
        byte_stream += i.to_bytes(Param.N_EACH_NBR_FIELD_BYTES, Param.BYTE_ORDER)
    for i in data:
        byte_stream += i.to_bytes(1, Param.BYTE_ORDER)
    return PystPacket(byte_stream=byte_stream)


if __name__ == "__main__":
    # b = PystPacketPayload(byte_stream=b"\x02\x00\x01\x03\x02\x05\x03\x11\x12\x13\x14\x15\x77\x88\x99")
    # b = PystPacketPayload(byte_stream=b"\x02\x00\x01\x03\x01\x05\x03\x11\x12\x13\x14\x15\x77\x88\x99")
    # b = PystPacketPayload(fields=[[75587, 256, 21], [15, 254]])
    # b = PystPacketPayload(n_each_field_bytes=[3, 4])
    # b = PystPacketHeader()
    # b = PystPacketHeader(n_each_field_bytes=[255, 1])
    # b = PystPacket(byte_stream=b"\x02\x00\x01\x03\x02\x05\x03\x11\x12\x13\x14\x15\x77\x88\x99")
    # b = PystPacket(byte_stream=b"\x02\x00\x01\x03\x01\x05\x03\x11\x12\x13\x14\x15\x77\x88\x99")
    # b = PystPacket(fields=[[75587, 256, 21], [15, 254]])
    b = PystPacket(n_each_field_bytes=[3, 4])
    # b = PystPacket(n_each_field_bytes=[255, 1])
    # b = PystPacket()
    # b = PystPacket(fields=[[255] * 255]*255)
    print(b)


