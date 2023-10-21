#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3 -B

import os
import time
import fcntl
import errno
import socket
import select
import threading
import queue
from RoPy.Pyst.py.PystPacket import *
from RoPy.Pyst.py.PystParam import *


class ThreadTable:
    def __init__(self):
        super(ThreadTable, self).__init__()
        self.get_lock = threading.RLock()
        self.put_lock = threading.RLock()

    def get(self):
        raise Exception(f"should implement in subclass")

    def put(self, th):
        raise Exception(f"should implement in subclass")


class IncrementalThreadTable(ThreadTable):
    """
    Retrieve valid ID that always increments for a client
    """
    def __init__(self, size):
        super(IncrementalThreadTable, self).__init__()
        if size > 256:
            rpfatal(f"{size} is beyond allowed thread limit")
        self.__max_allowed_size = size
        self.__n_thread_appeared = 0
        self.__thread_id_encode = {} # name, encode

    def get(self):
        th = threading.currentThread().name
        if th not in self.__thread_id_encode:
            self.__n_thread_appeared += 1
            self.__thread_id_encode[th] = self.__n_thread_appeared -1

        if self.__n_thread_appeared >= self.__max_allowed_size:
            rpfatal(f"Number of threads ever created exceeds max allowed size {self.__size}")

        return self.__thread_id_encode[th]

    def put(self, th):
        pass


class MinIDFirstThreadTable(ThreadTable):
    """
    Retrieve valid ID that always from counts mininum available for a client
    """
    def __init__(self, size):
        super(MinIDFirstThreadTable, self).__init__()
        if size > 256:
            rpfatal(f"{size} is beyond allowed thread limit")
        self.__valid_thread = {}
        for i in range(size):
            self.__valid_thread[i] = True
    
    def get(self):
        ans = -1
        with self.get_lock:
            while not any(list(self.__valid_thread.values())):
                time.sleep(0.001)
            for k, v in self.__valid_thread.items():
                if v:
                    self.__valid_thread[k] = False
                    ans = k
                    break
        if ans < 0:
            rpfatal("Unable to fetch thread")
        return ans
            
    def put(self, th):
        with self.put_lock:
            if self.__valid_thread[th]:
                rpfatal(f"Thread {th} was valid, can't put it back to be valid again")
            self.__valid_thread[th] = True
            
    def __del__(self):
        if not all(list(self.__valid_thread.values())):
            rpfatal(f"Thread table is not clean")


class PystClient:
    __instance_cnt = 0
    __instance_cnt_lock = threading.RLock()

    def __init__(self,
                 family=socket.AF_INET,
                 stype=socket.SOCK_STREAM):
        super(PystClient, self).__init__()
        with PystClient.__instance_cnt_lock:
            self.id = PystClient.__instance_cnt
            PystClient.__instance_cnt += 1

        self.family = family
        self.stype = stype
        self.socket = None
        self.host = None
        self.port = None
        self.read_time_out = None
        self.blocking_mode = None
        self.buf_per_thread = {}
        self.nbr_pkt_in_processing = {}
        self.thread_tab = IncrementalThreadTable(size=256) # ThreadTable(size=255)
        self.thread_pkt_cnt = {}
        self.rd_th = None
        self.rd_th_is_alive = False
        self.__closed = True

    # blocking mode -> read_time_out = None
    def connect(self, host=None, port=8000, read_time_out=0.0001, retry_max_wait_time=60, retry_step=0.05):
        if self.is_closed():
            self.host = host if host else socket.gethostname()
            self.port = int(port)
            self.read_time_out = read_time_out
            time_elapsed = 0
            self.socket = socket.socket(self.family, self.stype)

            inner_trace(f"Attempt to connect to {host}:{port} ... timeout in {retry_max_wait_time} sec")
            while True:
                try:
                    self.socket.connect((self.host, self.port))
                    inner_trace("Found connection. Succeed to connect!")
                    break
                except Exception as e:
                    if time_elapsed >= retry_max_wait_time:
                        rpfatal(f"Failed to connect to server")
                    time.sleep(retry_step)
                    time_elapsed += retry_step
                    # inner_trace(f"Attempt failed, time elapsed {time_elapsed} s, retrying to connect ...")
            self.__closed = False
            
            self.blocking_mode = self.read_time_out is None
            inner_trace(f"Client[{self.id}] uses blocking mode = {self.blocking_mode}")

            if self.blocking_mode:
                self.socket.settimeout(self.read_time_out)
            else:
                fcntl.fcntl(self.socket, fcntl.F_SETFL, os.O_NONBLOCK)
 
            self.rd_th = threading.Thread(target=self.__spwan_recv_thread)
            self.rd_th.start()

    def __spwan_recv_thread(self):
        self.rd_th_is_alive = True

        while not self.is_closed():
            if sum(list(self.nbr_pkt_in_processing.values())) == 0:
                continue

            rd_msg_bytes = []

            if not self.blocking_mode: # non blocking
                timeout_elapse = 0
                last_timeout_elapse_show = 0
                while not self.is_closed():
                    try:
                        rd_msg_bytes = self.socket.recv(Param.MAX_PACKET_TOTAL_BYTES_LIMIT)
                    except socket.error as e:
                        err = e.args[0]
                        if err == errno.EAGAIN or err == errno.EWOULDBLOCK:
                            time.sleep(self.read_time_out)
                            timeout_elapse += self.read_time_out
                            if int(timeout_elapse) >= 1 and int(timeout_elapse) != last_timeout_elapse_show:
                                inner_trace(f"non blocking read mode, timeout elapsed = {timeout_elapse} s")
                                last_timeout_elapse_show = int(timeout_elapse)
                            continue
                        else:
                            rpfatal(f"Client closed is {self.is_closed()}, and found message receving error: {err}")
                    else:
                        # got something
                        break
            else: # blocking
                timeout_elapse = 0
                last_timeout_elapse_show = 0
                while not self.is_closed():
                    try:
                        rd_msg_bytes = self.socket.recv(Param.MAX_PACKET_TOTAL_BYTES_LIMIT)
                    except socket.timeout as e:
                        err = e.args[0]
                        if err == "timed out":
                            time.sleep(self.read_time_out)
                            timeout_elapse += self.read_time_out
                            if int(timeout_elapse) >= 1 and int(timeout_elapse) != last_timeout_elapse_show:
                                inner_trace(f"blocking read mode, timeout elapsed = {timeout_elapse} s")
                                last_timeout_elapse_show = int(timeout_elapse)
                            continue
                        else:
                            rpfatal(f"Client closed is {self.is_closed()}, and found message receving error: {err}")
                    except socket.error as e:
                        rpfatal(f"Client closed is {self.is_closed()}, and found message receving error: {err}")
                    else:
                        # got something
                        break

            if not rd_msg_bytes and not self.is_closed():
                self.rd_th_is_alive = False
                rpfatal(f"Received empty message. Server is disconnected before client {self.id} termination.")

            while len(rd_msg_bytes) > 0:
                rsp_pkt = PystPacket(byte_stream=rd_msg_bytes)
                inner_trace(f"client[{self.id}].thread[{rsp_pkt.header.thread_id}] recv: {bytes_stringfy(rd_msg_bytes)}")
                self.buf_per_thread[rsp_pkt.header.thread_id].put(rsp_pkt)
                rd_msg_bytes = rd_msg_bytes[len(rsp_pkt.bytes):]
        
        self.rd_th_is_alive = False

        
    def send(self, pkt):
        th_id = self.thread_tab.get()
        if th_id not in self.thread_pkt_cnt:
            self.thread_pkt_cnt[th_id] = 0
        self.thread_pkt_cnt[th_id] = (self.thread_pkt_cnt[th_id] + 1) & 0xffff
        pkt.header.set_pid(client_id=self.id, thread_id=th_id, pkt_nbr=self.thread_pkt_cnt[th_id])
        pkt.rebuild()
        if th_id not in self.buf_per_thread:
            self.buf_per_thread[th_id] = queue.Queue()
        if th_id not in self.nbr_pkt_in_processing:
            self.nbr_pkt_in_processing[th_id] = 0
        self.nbr_pkt_in_processing[th_id] += 1
        self.socket.sendall(pkt.bytes)
        # always expects server sends back acknowledge message
        inner_trace(f"client[{self.id}].thread[{th_id}] sent: {bytes_stringfy(pkt.bytes)}")

        while self.rd_th_is_alive:
            try:
                echo_pkt = self.buf_per_thread[th_id].get(timeout=0.0001)
                break
            except queue.Empty:
                if not self.rd_th_is_alive:
                    rpfatal(f"client[{self.id}].thread[{th_id}] detected the termination on the remote end to quit")

        self.buf_per_thread[th_id].task_done()
        self.nbr_pkt_in_processing[th_id] -= 1
        self.thread_tab.put(th_id)
        inner_trace(f"client[{self.id}].thread[{th_id}] got echo")
        if not echo_pkt:
            rpfatal(f"link to client {self.client.id} closed without receiving proper echo data. The process(SV/C/C++) on the other side gets terminated abnormally.")
        if pkt.pid != echo_pkt.pid:
            rpfatal(f"sent id = {pkt.pid}, returned id = {echo_pkt.pid}")
        if pkt.ptype != echo_pkt.ptype:
            rpfatal(f"sent type = {pkt.ptype.name}, returned type = {echo_pkt.ptype.name}")
        if pkt.pcomponent != echo_pkt.pcomponent:
            rpfatal(f"sent component = {pkt.pcomponent}, returned component = {echo_pkt.pcomponent}")
        if pkt.proutine != echo_pkt.proutine:
            rpfatal(f"sent routine = {pkt.proutine}, returned routine = {echo_pkt.proutine}")
        return echo_pkt
            
    def close(self):
        for th_id in self.nbr_pkt_in_processing.keys():
            if self.rd_th_is_alive and self.nbr_pkt_in_processing[th_id] > 0:
                inner_trace(f"Client[{self.id}].thread[{th_id}] has {self.nbr_pkt_in_processing[th_id]} packets left unprocessed, waiting ...")
                while self.nbr_pkt_in_processing[th_id] > 0:
                    time.sleep(self.read_time_out)
                inner_trace(f"Client[{self.id}].thread[{th_id}] has no packets left unprocessed, waiting done")

        self.__closed = True
        for th, q in self.buf_per_thread.items():
            q.join()
            inner_trace(f"Client[{self.id}].thread[{th}] queue completed")
        self.rd_th.join()
        self.socket.close()
        inner_trace(f"Client {self.id} closed")
    
    def is_closed(self):
        return self.__closed
