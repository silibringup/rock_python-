from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent
from RoPy import RPCommon, rpinfo, rpdebug, rperror, rpwarning

class Priv(EROTComponent):
    ######## Public #############
    def __init__(self):
        pass

    def write(self,rockpy_handle,addr,data,priv_id=0,wait_tick=1,priv_level=0x3,source_id=0x1f):
        rpdebug("PRIV COMPONNET WRITE : %x %x %x %x" % ( addr,data,priv_level, source_id) )
        if wait_tick == 1:
            n_each_field_bytes = [4,4,4,4]
        else:
            n_each_field_bytes = [4,4,4,4,4]
        addr_bytes = [addr & 0xff, (addr & 0xff00)>>8, (addr & 0xff0000) >> 16, (addr & 0xff000000) >> 24]
        data_bytes = [data & 0xff, (data & 0xff00)>>8, (data & 0xff0000) >> 16, (data & 0xff000000) >> 24]
        priv_level_bytes = [ priv_level, 0,0,0 ]
        source_id_bytes  = [ source_id , 0,0,0 ]
        wait_tick_bytes = [0,0,0,0]

        if wait_tick == 1:
            fields = [addr_bytes,data_bytes,priv_level_bytes,source_id_bytes]
        else:
            fields = [addr_bytes,data_bytes,priv_level_bytes,source_id_bytes,wait_tick_bytes]
        if priv_id == 0:
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV, proutine=EROTComponent.SIM_PRIV_WRITE, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 1: #SYSCTRL
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_SYSCTRL, proutine=EROTComponent.SIM_PRIV_WRITE, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 2: #FSP
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_FSP, proutine=EROTComponent.SIM_PRIV_WRITE, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 3: #OOBHUB
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_OOBHUB, proutine=EROTComponent.SIM_PRIV_WRITE, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)

    def read(self,rockpy_handle,addr,priv_id=0,priv_level=0x3,source_id=0x1f):
        n_each_field_bytes = [4,4,4,4]
        addr_bytes = [addr & 0xff, (addr & 0xff00)>>8, (addr & 0xff0000) >> 16, (addr & 0xff000000) >> 24]
        data_bytes = [0,0,0,0]
        priv_level_bytes = [ priv_level, 0,0,0 ]
        source_id_bytes  = [ source_id , 0,0,0 ]
        fields = [addr_bytes,data_bytes,priv_level_bytes,source_id_bytes]
        if priv_id == 0:
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV, proutine=EROTComponent.SIM_PRIV_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 1: #SYSCTRL
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_SYSCTRL, proutine=EROTComponent.SIM_PRIV_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 2: #FSP
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_FSP, proutine=EROTComponent.SIM_PRIV_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 3: #OOBHUB
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_OOBHUB, proutine=EROTComponent.SIM_PRIV_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        x = rockpy_handle.transport(x)
        rdata = x.payload.fields[1][0] | (  x.payload.fields[1][1] << 8 ) |  (  x.payload.fields[1][2] << 16 ) | (  x.payload.fields[1][3] << 24 )
        rpdebug("PRIV COMPONNET READ : %x %x %x %x" % ( addr,rdata,priv_level, source_id) )
        return rdata
     

    def burst_read(self,rockpy_handle,addr_list,priv_id=1,priv_level=0x3,source_id=0x1f):
        if not isinstance(addr_list, list):
            rpdebug("Error, addr_list should be a list")
            return
        #if priv_id != 1:
            #rpdebug("Error, only priv_id 1 support burst read")
            #return

        n_each_field_bytes = [4*len(addr_list),4*len(addr_list),4,4]
        addr_bytes = []
        data_bytes = []
        for i in range(len(addr_list)):
            addr_bytes.append(addr_list[i] & 0xff)
            addr_bytes.append((addr_list[i] & 0xff00) >> 8)
            addr_bytes.append((addr_list[i] & 0xff0000) >> 16)
            addr_bytes.append((addr_list[i] & 0xff000000) >> 24)
            for j in range(4):
                data_bytes.append(0);

        priv_level_bytes = [ priv_level, 0,0,0 ]
        source_id_bytes  = [ source_id , 0,0,0 ]

        fields = [addr_bytes,data_bytes,priv_level_bytes,source_id_bytes]
        if priv_id == 1: #SYSCTRL
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_SYSCTRL, proutine=EROTComponent.SIM_PRIV_BURST_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 2: #FSP
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_FSP, proutine=EROTComponent.SIM_PRIV_BURST_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 3: #OOBHUB
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_OOBHUB, proutine=EROTComponent.SIM_PRIV_BURST_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        x = rockpy_handle.transport(x)
        
        rdata_list = []
        for i in range(len(addr_list)):
            rdata_list.append(x.payload.fields[1][i*4+0] | (  x.payload.fields[1][i*4+1] << 8 ) |  (  x.payload.fields[1][i*4+2] << 16 ) | (  x.payload.fields[1][i*4+3] << 24 ))
        return rdata_list


    # wait_tick is an un-used param, to be compatibled with write
    def burst_operation(self,rockpy_handle,addr_list,data_list,cmd_list,priv_id=1,wait_tick=0,priv_level=0x3,source_id=0x1f):
        # addr_list_field, data_list_field, priv_level_field, source_id_field, cmd_list_field, resp_err_field
        n_each_field_bytes = [4*len(addr_list),4*len(addr_list),4,4,len(addr_list),len(addr_list)]
        addr_bytes = []
        data_bytes = []
        cmd_bytes = []
        resp_err_bytes = []
        for i in range(len(addr_list)):
            addr_bytes.append(addr_list[i] & 0xff)
            addr_bytes.append((addr_list[i] & 0xff00) >> 8)
            addr_bytes.append((addr_list[i] & 0xff0000) >> 16)
            addr_bytes.append((addr_list[i] & 0xff000000) >> 24)
            data_bytes.append(data_list[i] & 0xff)
            data_bytes.append((data_list[i] & 0xff00) >> 8)
            data_bytes.append((data_list[i] & 0xff0000) >> 16)
            data_bytes.append((data_list[i] & 0xff000000) >> 24)
            cmd_bytes.append(cmd_list[i])
            resp_err_bytes.append(0)

        priv_level_bytes = [ priv_level, 0,0,0 ]
        source_id_bytes  = [ source_id , 0,0,0 ]

        fields = [addr_bytes,data_bytes,priv_level_bytes,source_id_bytes,cmd_bytes,resp_err_bytes]
        if priv_id == 1: #SYSCTRL
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_SYSCTRL, proutine=EROTComponent.SIM_PRIV_BURST_OPERATION, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 2: #FSP
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_FSP, proutine=EROTComponent.SIM_PRIV_BURST_OPERATION, n_each_field_bytes=n_each_field_bytes, fields=fields)
        elif priv_id == 3: #OOBHUB
            x = PystPacket(pcomponent=EROTComponent.SIM_PRIV_OOBHUB, proutine=EROTComponent.SIM_PRIV_BURST_OPERATION, n_each_field_bytes=n_each_field_bytes, fields=fields)
        x = rockpy_handle.transport(x)

        rdata_list = []
        resp_err_list = []
        for i in range(len(addr_list)):
            rdata_list.append(x.payload.fields[1][i*4+0] | (  x.payload.fields[1][i*4+1] << 8 ) |  (  x.payload.fields[1][i*4+2] << 16 ) | (  x.payload.fields[1][i*4+3] << 24 ))
            resp_err_list.append(x.payload.fields[5][i])
        return [rdata_list, resp_err_list]
