from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent
from RoPy import RPCommon, rpinfo, rpdebug, rperror, rpwarning

class Bm_sim(EROTComponent):
    ######## Public #############
    def __init__(self):
        pass

    def send_payload_to_bm(self,rockpy_handle,payload_byte_list):
        n_each_field_bytes = []
        n_each_field_bytes.append(len(payload_byte_list))
        fields = []
        fields.append(payload_byte_list)
        x = PystPacket(pcomponent=EROTComponent.BM_SIM, proutine=0, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)
