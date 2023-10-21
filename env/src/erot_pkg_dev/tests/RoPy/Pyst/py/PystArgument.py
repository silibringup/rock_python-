import struct
from RoPy.Pyst.py.PystPacket import PystPacket
from RoPy.Pyst.py.PystParam import *


class PystArgument:
    def __init__(self, atype=ArgumentType.INT, value=[], byte_stream=None):
        super(PystArgument, self).__init__()
        self.iter_idx = 0
        self.atype = None
        self.value = []
        self.value_in_bytes = []
        self.n_arg = None
        self.n_arg_bytes = []

        if not byte_stream:
            self.parse_from_args(atype, value)
        else:
            self.parse_from_byte_stream(byte_stream)

        self.bytes = bytearray()
        self.bytes += int(self.atype).to_bytes(1, Param.BYTE_ORDER)
        self.bytes += self.n_arg.to_bytes(1, Param.BYTE_ORDER)
        for i in self.n_arg_bytes:
            self.bytes += i.to_bytes(2, Param.BYTE_ORDER)
        for i in self.value_in_bytes:
            self.bytes += i

    def parse_from_args(self, atype, value=[]):
        self.atype = atype
        if dim(value) == 0:
            self.value = [value]
        if dim(value) == 1:
            self.value = value
        elif dim(value) >= 2:
            rpfatal(f"value must have dimension < 2")

        self.value_in_bytes = []
        if self.atype == ArgumentType.CHAR:
            for v in self.value:
                if len(v) != 1:
                    rpfatal(f"char format requires a bytes object of length 1")
                self.value_in_bytes.append(v.encode())
        elif self.atype == ArgumentType.UCHAR:
            self.value_in_bytes = [bytearray(struct.pack("B", v)) for v in self.value]
        elif self.atype == ArgumentType.SHORT:
            self.value_in_bytes = [bytearray(struct.pack("h", v)) for v in self.value]
        elif self.atype == ArgumentType.USHORT:
            self.value_in_bytes = [bytearray(struct.pack("H", v)) for v in self.value]
        elif self.atype == ArgumentType.INT:
            self.value_in_bytes = [bytearray(struct.pack("i", v)) for v in self.value]
        elif self.atype == ArgumentType.UINT:
            self.value_in_bytes = [bytearray(struct.pack("I", v)) for v in self.value]
        elif self.atype == ArgumentType.LONG:
            self.value_in_bytes = [bytearray(struct.pack("q", v)) for v in self.value]
        elif self.atype == ArgumentType.ULONG:
            self.value_in_bytes = [bytearray(struct.pack("Q", v)) for v in self.value]
        elif self.atype == ArgumentType.FLOAT:
            self.value_in_bytes = [bytearray(struct.pack("f", v)) for v in self.value]
        elif self.atype == ArgumentType.DOUBLE:
            self.value_in_bytes = [bytearray(struct.pack("d", v)) for v in self.value]
        elif self.atype == ArgumentType.STRING:
            self.value_in_bytes = [v.encode() for v in self.value]

        self.n_arg = len(self.value)
        self.n_arg_bytes = [len(v) for v in self.value_in_bytes]

    def parse_from_byte_stream(self, byte_stream):
        i = 0
        self.atype = ArgumentType(int.from_bytes(byte_stream[i:i+1], byteorder=Param.BYTE_ORDER))
        i += 1
        self.n_arg = int.from_bytes(byte_stream[i:i+1], byteorder=Param.BYTE_ORDER)
        i += 1
        for k in range(self.n_arg):
            self.n_arg_bytes.append(int.from_bytes(byte_stream[i:i+2], byteorder=Param.BYTE_ORDER))
            i += 2
        for k in self.n_arg_bytes:
            self.value_in_bytes.append(byte_stream[i:i + k])
            i += k

            if self.atype == ArgumentType.CHAR:
                self.value.append(self.value_in_bytes[-1].decode())
            elif self.atype == ArgumentType.UCHAR:
                self.value.append(struct.unpack("B", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.SHORT:
                self.value.append(struct.unpack("h", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.USHORT:
                self.value.append(struct.unpack("H", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.INT:
                self.value.append(struct.unpack("i", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.UINT:
                self.value.append(struct.unpack("I", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.LONG:
                self.value.append(struct.unpack("q", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.ULONG:
                self.value.append(struct.unpack("Q", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.FLOAT:
                self.value.append(struct.unpack("f", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.DOUBLE:
                self.value.append(struct.unpack("d", self.value_in_bytes[-1])[0])
            elif self.atype == ArgumentType.STRING:
                self.value.append(self.value_in_bytes[-1].decode())

    def get_type(self):
        return self.atype

    def get_value(self, idx):
        return self.value[idx]

    def __iter__(self):
        while self.iter_idx < len(self.value_in_bytes):
            yield self.value_in_bytes[self.iter_idx]
            self.iter_idx += 1
        self.idx = 0

    def __str__(self):
        s = ""
        s += f"type = {self.atype.name}\n"
        s += f"n_arg = {self.n_arg}\n"
        for i in range(len(self.value)):
            s += f"arg {i}, value = {self.value[i]}, n_bytes = {self.n_arg_bytes[i]}, bytes = {bytes_stringfy(self.value_in_bytes[i])}\n"
        s += f"bytes = {bytes_stringfy(self.bytes)}\n"
        return s


class PystFunctionPacket(PystPacket):
    def __init__(self,
                 pid=0,
                 pcomponent=0,
                 proutine=0,
                 byte_stream=None,
                 function_name="",
                 args=[]):
        self.function_name = PystArgument(ArgumentType.STRING, [function_name]) if function_name else None
        self.args = []
        self.ret = None
        # ptype sets to READ: always assume it has return value
        ptype = PacketType.FUNC
        if self.function_name:  # for send data to remote
            for i, a in enumerate(args):
                if not isinstance(a, PystArgument):
                    rpfatal(f"arg {i} is not type of {PystArgument.__name__}")
            self.args = args
            fields = [[self.function_name.bytes]] + [[a.bytes] for a in self.args]
            super(PystFunctionPacket, self).__init__(pid=pid,
                                                     ptype=ptype,
                                                     pcomponent=pcomponent,
                                                     proutine=proutine,
                                                     fields=fields)
        else:  # for get return data from remote, typically, the return value
            super(PystFunctionPacket, self).__init__(pid=pid,
                                                     ptype=ptype,
                                                     pcomponent=pcomponent,
                                                     proutine=proutine,
                                                     byte_stream=byte_stream)
            self.function_name = PystArgument(byte_stream=self.payload.fields[0])
            # return value from remote, only one return argument is allowed, field 0 is function name
            self.ret = PystArgument(byte_stream=self.payload.fields[-1])

    def __str__(self):
        s = f"|------------ Argument Packet -------------|\n"
        s += str(self.header)
        s += f"------------ Funtion name -------------\n"
        s += str(self.function_name)
        if self.args:
            for i, a in enumerate(self.args):
                s += f"------------ Argument {i} -------------\n"
                s += str(a)
        else:
            s += f"------------ Return -------------\n"
            s += str(self.ret)
        s += str(self.payload)
        s += f"packet bytes: {bytes_stringfy(self.bytes)}\n"
        return s


if __name__ == "__main__":
    args = []
    args.append(PystArgument(ArgumentType.STRING, ["ab"]))
    args.append(PystArgument(ArgumentType.STRING, ["cd", "efgh"]))
    args.append(PystArgument(ArgumentType.CHAR, ["a", "Z"]))
    args.append(PystArgument(ArgumentType.ULONG, [12, 34]))
    args.append(PystArgument(ArgumentType.DOUBLE, [5.1, 13.37]))
    s0 = str(args[4])
    r_arg = PystArgument(byte_stream=args[4].bytes)
    s1 = str(r_arg)
    if s0 != s1:
        raise Exception("Wrong!")
    print(s0)

    arg_pkt = PystFunctionPacket(function_name="foo", args=args)
    s0 = str(arg_pkt)
    r_arg_pkt = PystFunctionPacket(byte_stream=arg_pkt.bytes)
    s1 = str(r_arg_pkt)
    print(s0)
    print(s1)
