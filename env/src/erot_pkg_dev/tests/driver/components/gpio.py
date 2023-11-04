from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent
from RoPy import RPCommon, rpinfo, rpdebug, rperror, rpwarning

class Gpio(EROTComponent):
    ######## Public #############
    def __init__(self):
        pass

    def write_gpio(self,rockpy_handle,intf_name,data):
        
        if not isinstance(intf_name, str):
            rperror("Error, intf_name should be a string")
            return

        if data != 0 and data != 1:
            rperror("Error, data should be either 0 or 1")
            return

        intf_name_bytes_array = [v.encode() for v in intf_name]
        intf_name_size = len(intf_name_bytes_array)
        n_each_field_bytes = [intf_name_size,1]

        data_bytes = [data]
        fields = [intf_name_bytes_array, data_bytes]

        x = PystPacket(pcomponent=EROTComponent.GPIO, proutine=0, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)

    def read_gpio(self,rockpy_handle,intf_name):
        if not isinstance(intf_name, str):
            rperror("Error, intf_name should be a string")
            return

        intf_name_bytes_array = [v.encode() for v in intf_name]
        intf_name_size = len(intf_name_bytes_array)
        n_each_field_bytes = [intf_name_size,1]

        data_bytes = [0]
        fields = [intf_name_bytes_array,data_bytes]
        
        x = PystPacket(pcomponent=EROTComponent.GPIO, proutine=1, n_each_field_bytes=n_each_field_bytes, fields=fields)
        x = rockpy_handle.transport(x)
        rdata = x.payload.fields[1][0]
        if rdata != 0 and rdata != 1:
            return chr(rdata) 
        return rdata
     

    def wait_rpi_time(self,rockpy_handle,value,wait_time_type=0):
        
        n_each_field_bytes = [4,1]
        
        value_bytes = [value & 0xff, (value & 0xff00)>>8, (value & 0xff0000) >> 16, (value & 0xff000000) >> 24]
        wait_time_type_bytes = [wait_time_type]
        fields = [value_bytes,wait_time_type_bytes]

        x = PystPacket(pcomponent=EROTComponent.GPIO, proutine=2, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)
