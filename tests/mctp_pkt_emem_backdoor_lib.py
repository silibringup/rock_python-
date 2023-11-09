"""
This class define the MCTP packet class for OOBHUB testing
"""
from driver import *

#####################################
#Write MCTP packet into OOBHUB EMEM
#####################################
class mctpPkt():
    def __init__(self, targetEngine, src_eid, msg_to, msg_tag, payload, msg_size, msg_type):
        self.hdr_version = 0x1
        self.targetEngine = targetEngine
        self.src_eid = src_eid
        self.msg_to = msg_to
        self.msg_tag = msg_tag
        self.payload = payload
        # message size in bytes
        self.msg_size = msg_size
        # message type insert in first byte of payload
        self.msg_type = msg_type
        # Get EID for target engine
        self.dest_eid = self.getEngineEid(targetEngine)
        # parameters and variables
        self.MCTP_BASE_PKT_SIZE = 64
        self.BASE_UNIT_SIZE_IN_DWORDS = 17
        self.EMEM_ADDR_WIDTH = 10
        self.dw0_sel = 1
        self.mctp_payload_pointer = 0
        self.mctp_payload_array = []
        self.payload_dw = 0
        self.byte_per_dw = 0
        self.oobhub_emem_load_process = 0

    def load_mctp_pkt_systop(self):
        # Mark start of loading process
        self.mods_loading_process = 1
                
        # Write each byte of the payload into mctp_payload_array in TB
        for i in range(self.msg_size):
            oobhub_payload = self.payload[i]
            self.load_mctp_payload_array(oobhub_payload)
            helper.wait_sim_time('us',1)
            
        # Mark end of loading process
        self.mods_loading_process = 0
        
        # Start EMEM load process
        self.oobhub_emem_load_process = 1
        self.load_oobhub_emem()
        # Poll till EMEM load process finished
        emem_load_processing = self.oobhub_emem_load_process
        while emem_load_processing != 0:
            helper.wait_sim_time('us',1)
            emem_load_processing = self.oobhub_emem_load_process
        
    # Engine EID mapping
    def getEngineEid(self, engine):
        if engine == "FSP":
            return 0x1
        elif engine == "OOBHUBipc":
            return 0x2
        elif engine == "OOBHUBext":
            return 0x3

    #load MCTP packets process
    def load_mctp_payload_array(self, oob_payload):
        if self.mods_loading_process == 1:
            if self.mctp_payload_pointer == 0:
                self.mctp_payload_array = [None]*64
            self.mctp_payload_array[self.mctp_payload_pointer] = oob_payload
            self.mctp_payload_pointer += 1

    #EMEM load process
    def load_oobhub_emem(self):
        som = 0
        eom = 0
        payload_ptr = 0
        #Calculate how many packets will be needed for this message
        packets_required = self.get_pkt_cnt_for_msg(self.msg_size)
        for i in range(packets_required): 
            #First packet SOM = 1
            if (i == 0):
                som = 1
            #Last packet EOM = 1
            if (i == packets_required - 1):
                eom = 1
        
            #Calculate emem addr
            emem_addr = (i)*self.BASE_UNIT_SIZE_IN_DWORDS*4

            #Get MCTP header
            hdr = self.mctp_hdr(som, eom, i%4)
            #preload_addr = (emem_addr&0x1f8)>>3 #[EMEM_ADDR_WIDTH-1:3]
            preload_addr = emem_addr
            self.preload_emem(preload_addr, hdr) 
            emem_addr = emem_addr + 4
 
            #Get payload size for each packet
            if((eom == 1) & (self.msg_size % self.MCTP_BASE_PKT_SIZE != 0)):
                payload_size = self.msg_size % self.MCTP_BASE_PKT_SIZE
            else:
                payload_size = self.MCTP_BASE_PKT_SIZE

            #Loop through payload in mctp_payload_array and load into EMEM
            helper.pdebug(f'payload_ptr={payload_ptr}, payload_size={payload_size}')
            helper.pdebug(f'mctp_payload_array length = {len(self.mctp_payload_array)}')
            for j in range(payload_ptr, (payload_ptr + payload_size)):
                self.payload_dw |= (self.mctp_payload_array[j] << (self.byte_per_dw*8)) 
                helper.pdebug(f'payload_dw={hex(self.payload_dw)}')
                self.byte_per_dw += 1
                if(self.byte_per_dw == 4) | (j == (len(self.mctp_payload_array)-1)):
                    #Load number of packet in message*packet size(I2C/I3C 17 DW, VDM 19 DW) + 1(for header)
                    helper.pdebug(f'j={j}, emem_addr={emem_addr}, preload_addr={preload_addr}')
                    #preload_addr = (emem_addr&0x1f8)>>3 #[EMEM_ADDR_WIDTH-1:3]
                    preload_addr = emem_addr
                    self.preload_emem(preload_addr, self.payload_dw) 
                    self.byte_per_dw = 0
                    self.payload_dw = 0
                    emem_addr += 4
            payload_ptr += payload_size
        #End emem_load process
        self.oobhub_emem_load_process = 0
        #Reset the pointer for next message
        self.mctp_payload_pointer = 0

    #calculate how many packets will be needed for this message
    def get_pkt_cnt_for_msg(self, msg_size):
        pkt_required = int(msg_size / self.MCTP_BASE_PKT_SIZE)
        if ((msg_size % self.MCTP_BASE_PKT_SIZE) != 0 ):
            pkt_required = pkt_required + 1
        return pkt_required

    #get the MCTP header for each packet
    def mctp_hdr(self, som, eom, seqnum):
        mctp_hdr = (som<<31) | (eom<<30) | (seqnum<<28) | (self.msg_to<<27) | (self.msg_tag<<24) | (self.src_eid<<16) | (self.dest_eid<<8) | self.hdr_version
        return mctp_hdr

    #load emem
    def preload_emem(self, emem_addr, payload_dw):
        test_api.oobhub_icd_write(0x1200000+(emem_addr), payload_dw)
        #EMEM write is 64 bits, upper 32 or lower 32 bits
        '''if(self.dw0_sel == 1):
            M_path = 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_misc_wrap.u_rx_mem.M['+str(emem_addr)+'][31:0]'
             
            helper.hdl_force(M_path, payload_dw)
            self.dw0_sel = 0
        else:
            M_path_hi = 'ntb_top.u_nv_top.u_sra_sys0.u_l2_cluster.u_NV_oobhub.u_misc_wrap.u_rx_mem.M['+str(emem_addr)+'][63:32]'

            helper.hdl_force(M_path_hi, payload_dw)
            self.dw0_sel = 1'''

