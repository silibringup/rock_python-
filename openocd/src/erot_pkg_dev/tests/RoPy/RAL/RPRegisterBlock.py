import os
import sys
import json
from RoPy.Pyst import PystLink, PystPacket, PacketType, rpfatal, rpinfo, rperror, rpwarning, inner_trace

__has_pyral = True
try:
    from PyRAL.RegisterModel import RegisterBlock, Register, RegisterField
    from PyRAL.simspec2raldesc import RegSpecParser
except ImportError as e:
    __has_pyral = False
    inner_trace(f"{e}. Make sure pyral is in searchable paths if you want to use RoPy register model. Current searchable paths are:")
    for i in sys.path:
        inner_trace(f"| {i}")


if __has_pyral:
    _REG_COMPONENT_ID = 2
     
    class LinkTree:
        def __get_link__(self, parent):
            if 'link' in parent.__dict__:
                return parent.link
            else:
                return self.__get_link__(parent.parent)
     
     
    class RPRegisterField(RegisterField, LinkTree):
        def write(self, *args, **kwargs):
            if 'force_me' in kwargs and kwargs['force_me']:
                rpwarning(f"{self.name} enabled the limited feature 'force_me'. The result is not guaranteed.")
                super(RPRegisterField, self).set(*args, **kwargs)
                if 'parent_update' not in kwargs or not kwargs['parent_update']:
                    if 'read_after_write' not in kwargs or not kwargs['read_after_write']:
                        addr_fld = self.parent.offset.to_bytes(4, 'little')
                        value_fld = self.value.to_bytes(4, 'little')
                        msb_fld = self.msb.to_bytes(4, 'little')
                        lsb_fld = self.lsb.to_bytes(4, 'little')
                        pkt = PystPacket(ptype=PacketType.WRITE, 
                                        pcomponent=_REG_COMPONENT_ID, 
                                        fields=[[addr_fld], [value_fld], [msb_fld], [lsb_fld]])
                        link = self.__get_link__(self.parent)
                        link.transport(pkt)
                    else:
                        rd_val = self.parent.read(update_model=False)
                        wr_val = rd_val | (self.value << self.lsb)
                        self.parent.write(wr_val)
            else:
                rpfatal("Field write not supported")
                
     
        def read(self, *args, **kwargs):
            if 'force_me' in kwargs and kwargs['force_me']:
                rpwarning(f"{self.name} enabled the limited feature 'force_me'. The result is not guaranteed.")
                if 'parent_update' not in kwargs or not kwargs['parent_update']:
                    rd_val = self.parent.read(update_model=False)
                    mask = int('1' * self.length, 2) << self.lsb
                    data = rd_val & mask
                    if 'update_model' not in kwargs or kwargs['update_model']:
                        super(RPRegisterField, self).set(data) # update local model
                    return data
            else:
                rpfatal("Field read not supported")
     
     
    class RPRegister(Register, LinkTree):
        def write(self, *args, **kwargs):
            super(RPRegister, self).set(*args, **kwargs)
            if len(args) == 1 or 'value' in kwargs:
                # only write the whole reg
                wr_val = self.value.to_bytes(4, 'little')
            elif kwargs:
                if 'read_first' in kwargs and kwargs['read_first']:
                    wr_val = self.read(update_model=False)
                else:
                    wr_val = 0
                # write individual field
                for f, v in kwargs.items():
                    if f in self.fields:
                        if isinstance(v, list):
                            for i in range(len(v)):
                                # self.fields[f][i].write(v[i])
                                mask = int('1' * self.fields[f][i].length, 2) << self.fields[f][i].lsb
                                wr_val = wr_val & (~mask) | (self.fields[f][i].value << self.fields[f][i].lsb)
                        else:
                            # self.fields[f][0].write(v)
                            mask = int('1' * self.fields[f][0].length, 2) << self.fields[f][0].lsb
                            wr_val = wr_val & (~mask) | (self.fields[f][0].value << self.fields[f][0].lsb)
                    else:
                        # do nothing, may have other non-field arguments
                        pass
                wr_val = wr_val.to_bytes(4, 'little')
            else:
                raise ValueError(f"Nither value nor field are provided")
            addr = self.offset.to_bytes(4, 'little')
            pkt = PystPacket(ptype=PacketType.WRITE,
                             pcomponent=_REG_COMPONENT_ID,
                             fields=[[addr], [wr_val]])
            link = self.__get_link__(self.parent)
            link.transport(pkt)
     
        def read(self, *args, **kwargs):
            link = self.__get_link__(self.parent)
            addr = self.offset.to_bytes(4, 'little')
            rd_pkt = link.transport(PystPacket(ptype=PacketType.READ, 
                                               pcomponent=_REG_COMPONENT_ID, 
                                               fields=[[addr]]))
            rd_value = int.from_bytes(rd_pkt.payload.fields[-1], 'little')
            if 'update_model' not in kwargs or kwargs['update_model']:
                super(RPRegister, self).set(value=rd_value)  # update local value
            return rd_value
     
        def update(self, *args, **kwargs):
            kwargs['read_first'] = True
            self.write(*args, **kwargs)
     
        def poll(self, *args, **kwargs):
            '''
            read timeout times, retrun True if succeed else False, default 1000 times
            '''
            times = 1000
            if 'timeout' in kwargs:
                times = kwargs['timeout']
                kwargs.pop('timeout')
     
            if times < 0:
                rpfatal("timeout must be >= 1")
            
            if not args and not kwargs:
                rpfatal(f"No args were provided. What do you want to poll on?")
            
            for i in range(times):
                rd_val = self.read()
                unsucceed = True
                
                if len(args) == 1 or 'value' in kwargs:
                    # only write the whole reg
                    if len(args) == 1:
                        value = args[0]
                    else:
                        value = kwargs['value']
                    unsucceed &= (rd_val != value)
                elif kwargs:
                    # individual field
                    for f, v in kwargs.items():
                        if f in self.fields:
                            if isinstance(v, list):
                                for i in range(len(v)):
                                    if isinstance(v, str):
                                        unsucceed &= (self.fields[f][i].value != self.fields[f][i].enum2value(v))
                                    else:
                                        unsucceed &= (self.fields[f][i].value != v)
                            else:
                                if isinstance(v, str):
                                    unsucceed &= (self.fields[f][0].value != self.fields[f][0].enum2value(v))
                                else:
                                    unsucceed &= (self.fields[f][0].value != v)
                # quit when succeeds
                if not unsucceed:
                    return True
     
            if unsucceed:
                rperror(f"{self.name} did't get the expected value after polling {times} times. Final value = {hex(self.value)}")
     
            return False
     
    class RPRegisterBlock(RegisterBlock):
        def __init__(self, regjson, link, **kwargs):
            if not isinstance(link, PystLink):
                raise Exception(f"{link} wrong type")
            self.link = link
     
            if not os.path.exists(regjson):
                raise ValueError(f"{regjson} No such a file or directory")

            cust = {}
            if 'cust' in kwargs:
                with open(kwargs['cust'], 'r') as f:
                    cust = json.load(f)
            
            regblk_fd = None
            with open(regjson, 'r') as f:
                spec_parser = RegSpecParser(json.load(f), cust)
                regblk_fd = list(spec_parser.register_blocks.values())[0]

            if not regblk_fd:
                raise ValueError(f"Unable to find valud register block in {regjson}")
     
            if 'RegBlkCls' not in kwargs:
                kwargs['RegBlkCls'] = RPRegisterBlock
            if 'RegCls' not in kwargs:
                kwargs['RegCls'] = RPRegister
            if 'RegFldCls' not in kwargs:
                kwargs['RegFldCls'] = RPRegisterField
            super(RPRegisterBlock, self).__init__(regblk_fd, **kwargs)
     

