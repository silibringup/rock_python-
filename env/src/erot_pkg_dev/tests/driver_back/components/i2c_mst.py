from RoPy import rpinfo, rpdebug, rperror
from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent

class I2c_mst(EROTComponent):
    ######## Public #############
    def __init__(self):
        pass
    
    def data_to_byte_list(self, data, size):
        if size <= 0:
            rperror("Invalid size")
        if data > (1 << (size*8)):
            rperror("Invalid data %s" % data)
        byte_list = []
    
        for i in range(size):
            byte_list.append(data & 0xff)
            data = data >> 8
        return byte_list

    def byte_list_to_data(self, byte_list):
        if len(byte_list) <= 0:
            rperror("empty byte_list")
            return 0
    
        data = 0
        for i in range(len(byte_list)):
            data = data | (byte_list[i]<<(i*8))
        return data

    def write(self,rockpy_handle,addr,data,size=16,i2c_id=0,en_10bits_addr=0, wo_STOP=0):
        rpdebug("I2C mater COMPONNET WRITE(addr, byte_size, i2c_id, en_10bits_addr): %x %d %x %x" % (addr, size, i2c_id, en_10bits_addr) )
        rpdebug(data)
        if size <= 0:
            rperror("Invalid size %s" % size)

        if isinstance(data, list):
            if len(data) != size:
                rperror("data is a list, however, it's size is mismatch with the size parameter")
        
        #if wo_STOP == 1 and i2c_id != 3:
            #rperror("wo_STOP mode is only for oobhub i2c")

        if wo_STOP == 1:
            n_each_field_bytes = [4,size,4]
        else:
            n_each_field_bytes = [4,size]
        
        if en_10bits_addr == 1 and addr > 0x3ff:
            rperror("addr overflows for 10bits I2C")
        elif en_10bits_addr == 0 and addr > 0x7f:
            rperror("addr overflows for 7bits I2C")

        # Set addr[31:16] to 0xff_ff for 10bits addr, while 0x00_00 for 7 bits addr
        if en_10bits_addr == 1:
            addr_bytes = [addr & 0xff, (addr & 0x0300)>>8, 0xff, 0xff]
        else:
            addr_bytes = [addr & 0x7f, 0x00, 0x00, 0x00]

        if isinstance(data, list):
            data_bytes = []
            for i in range(len(data)):
                data_bytes.append(data[i])
        else:
            data_bytes = self.data_to_byte_list(data, size)
        
        if wo_STOP == 1:
            wo_STOP_fields = [0, 0, 0, 0]
            fields = [addr_bytes,data_bytes,wo_STOP_fields]
        else:
            fields = [addr_bytes,data_bytes]

    
        if i2c_id == 0:
            pcomponent_id = EROTComponent.AP1_I2C
        elif i2c_id == 1:
            pcomponent_id = EROTComponent.AP2_I2C
        elif i2c_id == 3:
            pcomponent_id = EROTComponent.BMC_I2C
        else:
            rperror("unsupported i2c_id")
        x = PystPacket(pcomponent=pcomponent_id, proutine=EROTComponent.I2C_WRITE, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)
     
    
    def read(self,rockpy_handle,addr,size=16,i2c_id=0,en_10bits_addr=0,wo_ADDR=0,wo_STOP=0):
        rpdebug("I2C mater COMPONNET READ BYTE: %x %x %x" % (addr, i2c_id, en_10bits_addr) )
        if size <= 0:
            rperror("Invalid size")

        #if wo_ADDR==1 or wo_STOP==1:
            #if i2c_id != 3:
                #rperror("wo_ADDR or wo_STOP is only for oobhub recovery i2c")

        if wo_ADDR==1 or wo_STOP==1:
            n_each_field_bytes = [4,size,4]
        else:
            n_each_field_bytes = [4,size]


        if en_10bits_addr == 1 and addr > 0x3ff:
            rperror("addr overflow for 10bits I2C")
        elif en_10bits_addr == 0 and addr > 0x7f:
            rperror("addr overflow for 7bits I2C")


        # Set addr[31:16] to 0xff_ff for 10bits addr, while 0x00_00 for 7 bits addr
        if en_10bits_addr == 1:
            addr_bytes = [addr & 0xff, (addr & 0x0300)>>8, 0xff, 0xff]
        else:
            addr_bytes = [addr & 0x7f, 0x00, 0x00, 0x00]
        
        data_bytes = []
        for i in range(size):
            data_bytes.append(0)
        fields = [addr_bytes,data_bytes]
        
        if wo_ADDR == 1 and wo_STOP == 0:
            extra_field_bytes = [0,0,0,0]
            fields.append(extra_field_bytes)
        elif wo_ADDR == 0 and wo_STOP == 1:
            extra_field_bytes = [1,0,0,0]
            fields.append(extra_field_bytes)

        if i2c_id == 0:
            pcomponent_id = EROTComponent.AP1_I2C
        elif i2c_id == 1:
            pcomponent_id = EROTComponent.AP2_I2C
        elif i2c_id == 3:
            pcomponent_id = EROTComponent.BMC_I2C
        else:
            rperror("unsupported i2c_id")

        x = PystPacket(pcomponent=pcomponent_id, proutine=EROTComponent.I2C_READ, n_each_field_bytes=n_each_field_bytes, fields=fields)
        x = rockpy_handle.transport(x)
        rdata = self.byte_list_to_data(x.payload.fields[1])
        return rdata

