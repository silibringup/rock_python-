import os
from RoPy.Pyst.py.PystClient import PystClient
from RoPy.Pyst.py.PystPacket import PystPacket
from RoPy.Pyst import PystFunctionPacket
from RoPy.Pyst.py.PystParam import *

class PystLink:
    def __init__(self, port=8000, host=None, connect_timeout=-1):
        super(PystLink, self).__init__()
        inner_trace("Link initializing ...")
        if connect_timeout < 0:
            if 'PYST_TIMEOUT' in os.environ:
                connect_timeout = int(os.environ['PYST_TIMEOUT']) / 1000
            else:
                connect_timeout = 60  # default 60

        self.client = PystClient()
        inner_trace(f"Client[{self.client.id}] connect attempt timeout {connect_timeout} seconds")
        self.client.connect(host=host, port=int(port), retry_max_wait_time=connect_timeout, read_time_out=0.0000001)
        if self.client.id == 0:
            self.__register_farewell(host, int(port))
        inner_trace("Link initialization completed")

    def __del__(self):
        self.finish()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.finish()

    def transport(self, pkt, **kwargs):
        if pkt is not None and not isinstance(pkt, PystPacket):
            rpfatal(f"pkt type should be {PystPacket.__name__}, but received {type(pkt)}")
        inner_trace(f"Client[{self.client.id}] is transporting packet ...")
        echo_pkt = self.client.send(pkt)
        inner_trace(f"Client[{self.client.id}] completes transporting packet")
        return echo_pkt

    def function_call(self, func_pkt=None):
        if func_pkt is not None and not isinstance(func_pkt, PystFunctionPacket):
            rpfatal(f"type should be {PystFunctionPacket.__name__}, but received {type(func_pkt)}")
        echo_pkt = self.client.send(func_pkt)
        return PystFunctionPacket(byte_stream=echo_pkt.bytes)
    
    def finish(self):
        if not self.client.is_closed():
            self.client.close()

    def __register_farewell(self, host, port):
        def in_the_end():
            inner_trace(f"Farewell... {host}:{port}")
            if self.client.is_closed():
                self.client.connect(host=host, port=port, retry_max_wait_time=5)
            self.client.send(PystPacket(ptype=PacketType.ABORT))
            if not self.client.is_closed():
                self.client.close()
            inner_trace("Goodbye, Rock Python.")
        import atexit
        atexit.register(in_the_end)