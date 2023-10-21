""" 
Functions to program Falcon DMA through PRI
Note: This module assumes that only a single DMA is in flight at any time.
"""
from driver import *
import sys
import threading
import pdb
import time

DBGSTR = f"[{__name__}]"
supported_engines = ["FSP", "OOBHUB"]

def _wait_for_local_mem_scrub(engine, is_imem=False):    
    mem_str = 'IMEM' if is_imem else 'DMEM'
    helper.pdebug(f'{DBGSTR} Beginning polling for {mem_str} SCRUBBING_DONE')        
    if engine in ["OOBHUB"]:
        if is_imem:
            erot.OOBHUB.PEREGRINE_FALCON_DMACTL_0.poll(IMEM_SCRUBBING=0, timeout=500)
        else:
            erot.OOBHUB.PEREGRINE_FALCON_DMACTL_0.poll(DMEM_SCRUBBING=0, timeout=500)
    elif engine in ["FSP"]:
        if is_imem:
            erot.FSP.FALCON_DMACTL_0.poll(IMEM_SCRUBBING=0, timeout=500)
        else:
            erot.FSP.FALCON_DMACTL_0.poll(DMEM_SCRUBBING='DONE', timeout=500) 
    else:
        helper.perror(f'{DBGSTR} engine not supported')

    helper.pdebug(f'{DBGSTR} Done polling for {mem_str} SCRUBBING_DONE')

def read_falcon_mem(engine, address, num_msg, is_imem=False, port=0):
    if engine not in supported_engines:
        helper.perror(f'{DBGSTR} Unsupported engine {engine}')
    if address % 4:
        helper.perror(f'{DBGSTR} Unsupported read address: {address:#x}, must be on 4 byte boundary')
    
    _wait_for_local_mem_scrub(engine, is_imem)

    helper.pdebug(f'{DBGSTR} Begin falcon read')
    
    if engine in ["OOBHUB"]:
        if is_imem:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCR
            getattr(erot.OOBHUB, f"PEREGRINE_FALCON_IMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<25))
        else:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCR
            getattr(erot.OOBHUB, f"PEREGRINE_FALCON_DMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<25)) 
    elif engine in ["FSP"]:
        if is_imem:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCR
            getattr(erot.FSP, f"FALCON_IMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<25)) 
        else:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCR
            getattr(erot.FSP, f"FALCON_DMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<25)) 
    else:
        helper.perror(f'{DBGSTR} engine not supported')

    data = []
    for i in range(num_msg):
        if engine in ["OOBHUB"]:
            if is_imem:
                rd = getattr(erot.OOBHUB, f"PEREGRINE_FALCON_IMEMD_{port}").read()
                datum = rd.value
            else:
                rd = getattr(erot.OOBHUB, f"PEREGRINE_FALCON_DMEMD_{port}").read()
                datum = rd.value
        elif engine in ["FSP"]:
            if is_imem:
                rd = getattr(erot.FSP, f"FALCON_IMEMD_{port}").read()
                datum = rd.value
            else:
                rd = getattr(erot.FSP, f"FALCON_DMEMD_{port}").read() 
                datum = rd.value
        data.append(datum)
    return data

def write_falcon_mem(engine, address, data, num_msg, is_imem=False, port=0):
    if engine not in supported_engines:
        helper.perror(f'{DBGSTR} Unsupported engine {engine}')
    if address % 4:
        helper.perror(f'{DBGSTR} Unsupported write address: {address:#x}, must be on 4 byte boundary')
    
    _wait_for_local_mem_scrub(engine, is_imem)

    helper.pdebug(f'{DBGSTR} Begin falcon write')
    
    if engine in ["OOBHUB"]:
        if is_imem:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCW
            getattr(erot.OOBHUB, f"PEREGRINE_FALCON_IMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<24))
        else:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCW
            getattr(erot.OOBHUB, f"PEREGRINE_FALCON_DMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<24)) 
    elif engine in ["FSP"]:
        if is_imem:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCW
            getattr(erot.FSP, f"FALCON_IMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<24)) 
        else:
            #[7:2]_OFF, [23:8]_BLK, [25:25]_AINCW
            getattr(erot.FSP, f"FALCON_DMEMC_{port}").write((address&0xFC) | (address&0xFFFF00) | (0x1<<24)) 
    else:
        helper.perror(f'{DBGSTR} engine not supported')    
    
    for i in range(num_msg):
        if engine in ["OOBHUB"]:
            if is_imem:
                getattr(erot.OOBHUB, f"PEREGRINE_FALCON_IMEMD_{port}").write(data[i])
            else:
                getattr(erot.OOBHUB, f"PEREGRINE_FALCON_DMEMD_{port}").write(data[i])
        elif engine in ["FSP"]:
            if is_imem:
                getattr(erot.FSP, f"FALCON_IMEMD_{port}").write(data[i])
            else:
                getattr(erot.FSP, f"FALCON_DMEMD_{port}").write(data[i])
