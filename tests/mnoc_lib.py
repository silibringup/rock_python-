"""
MNOC Common library
This file contains all the functions to config MNOC for MCTP tests
"""
from driver import *
import falcondma_lib

class MnocLib():
    def __init__(self, engine, imem_start_addr, imem_num_bytes, dmem_start_addr, dmem_num_bytes):
        self.name = "mnoc_lib"
        
        # Get local class variable setup
        self.engine = engine
        
        # Setup engine reg name prefix
        self.set_engine_reg_name()
        
        self.RISCV_PA_DMEM_START = 0x180000
        # This variable is to set the memory starting space for rx mem 
        self.tx_mem_size = 128
        
        # Get IMEM/DMEM address for test
        self.imem_tx_addr = imem_start_addr
        self.imem_engine_num_bytes = imem_num_bytes
        self.dmem_tx_addr = dmem_start_addr
        self.dmem_engine_num_bytes = dmem_num_bytes
        self.get_local_mem_range()

    #######################################################
    # ENGINE SPECIFIC VALUES
    #######################################################
    
    # Function to setup engine EID and reg name prefix
    def set_engine_reg_name(self):
        if self.engine == "FSP":
            self.mctp_port_prefix = "NV_CFSP_MNOC_"
            self.mnoc_pri_prefix = "NV_PFSP_MNOC_"
        elif self.engine == "OOBHUB":
            self.mctp_port_prefix = "NV_COOBHUB_PEREGRINE_COOB_MNOC_"
            self.mnoc_pri_prefix = "NV_POOBHUB_PEREGRINE_MNOC_"
        else:
            helper.perror('%s: Unknown engine' % self.name)

    # Engine EID mapping
    def get_engine_eid(self, engine, extcomm = 0):
        if engine == "FSP":
            return 0x1
        elif engine == "OOBHUB" and not extcomm:
            return 0x2
        elif engine == "OOBHUB" and extcomm:
            return 0x3

    #######################################################
    # MEMORY MANAGEMENT FUNCTIONS
    #######################################################    
    # Get DMEM mem address for this test
    def get_local_mem_range(self):
        #self.dmem_tx_addr = 0x2400
        #self.dmem_engine_num_bytes = 0x400
        self.dmem_rx_addr = self.RISCV_PA_DMEM_START + self.dmem_tx_addr + self.tx_mem_size

        dmem_pa_addr = self.RISCV_PA_DMEM_START + self.dmem_tx_addr
        # Get tx and rx mem range
        self.lower_tx_tcm = dmem_pa_addr & 0xFFFFFFFF
        self.higher_tx_tcm = (dmem_pa_addr & 0xFFFFFFFF00000000) >> 32
        self.lower_rx_tcm = (dmem_pa_addr + self.tx_mem_size) & 0xFFFFFFFF
        self.higher_rx_tcm = ((dmem_pa_addr + self.tx_mem_size) & 0xFFFFFFFF00000000) >> 32
        helper.pinfo("[mnoc_common_library]: dmem_pa_addr = 0x%x, lower_tx_tcm = 0x%x, higher_tx_tcm = 0x%x, lower_rx_tcm=0x%x, higher_rx_tcm = 0x%x" % (dmem_pa_addr, self.lower_tx_tcm, self.higher_tx_tcm, self.lower_rx_tcm, self.higher_rx_tcm))
    
    # Load packet into memory for sending
    def mem_load_data(self, msg_size, tx_send_message):        
        # use falcondma to load packet into dmem
        helper.pinfo("Load packet into DMEM for send")
        falcondma_lib.write_falcon_mem(self.engine, self.dmem_tx_addr, tx_send_message, msg_size)

    #######################################################
    # MNOC INITIALIZATION FUNCTIONS
    #######################################################
    
    # Function to initialize MNOC source send port
    def initialize_mctp_send_port(self, target_engine, port_num, TAG, TO, max_message_size, enable_interrupts = False, extcomm = 0):
        
        helper.pinfo(f'Info: Initialize port')
        # Get engine EID for target engine
        target_eid = self.get_engine_eid(target_engine, extcomm)

        port_idx = "("+str(port_num)+")"

        if port_num == 0:
            erot.FSP.MNOC_MNOC_MCTP_SENDPORT_CTRL_0_0.write(0x1)
            erot.FSP.MNOC_SETUP_CONFIG_0_SENDPORT_0.write((0x0|(TO << 24)|(0x0 << 18)|(TAG << 16)|(0x0 << 8)|target_eid)&0x810700FF)
            erot.FSP.MNOC_MESSAGE_CONFIG_0_SENDPORT_0.write(self.lower_tx_tcm&0xFFFFFFFE)
            erot.FSP.MNOC_MESSAGE_CONFIG_1_SENDPORT_0.write(self.higher_tx_tcm)
            erot.FSP.MNOC_MESSAGE_CONFIG_2_SENDPORT_0.write(max_message_size&0xFFFFFFFE)
            helper.pinfo("[mnoc_common_library]: Initalize send ports")   

        if enable_interrupts:
            erot.FSP.MNOC_INTERRUPT_ENABLE_0_SENDPORT_0.write(0x1)
            erot.FSP.MNOC_MNOC_COMMON_INTR_ENABLE_0_0.write(0x1)
            erot.FSP.MNOC_MNOC_PORT_CPU_INTR_AGGREGATOR_1_0.write(0x1)
            helper.pinfo("[mnoc_common_library]: Enable interrupts")
            
    # Function to initialize MNOC target receive port
    def initialize_mctp_receive_port(self, target_engine, port_num, TAG, TO, max_message_size, enable_interrupts = False, extcomm = 0):
        
        helper.pinfo("Info: Initialize port")
        # Get engine EID for target engine
        target_eid = self.get_engine_eid(target_engine, extcomm)

        port_idx = "("+str(port_num)+")"

        if port_num == 0:
            erot.FSP.MNOC_MNOC_MCTP_RECEIVEPORT_CTRL_0_0.write(0x1)
            erot.FSP.MNOC_SETUP_CONFIG_0_RECEIVEPORT_0.write(((TO << 24)|(TAG << 16)|target_eid) & 0x810700FF)
            erot.FSP.MNOC_MESSAGE_CONFIG_0_RECEIVEPORT_0.write(self.lower_rx_tcm&0xFFFFFFFE)
            erot.FSP.MNOC_MESSAGE_CONFIG_1_RECEIVEPORT_0.write(self.higher_rx_tcm)
            erot.FSP.MNOC_MESSAGE_CONFIG_2_RECEIVEPORT_0.write(max_message_size)
            erot.FSP.MNOC_MESSAGE_OPERATION_0_RECEIVEPORT_0.write(0x1)
            helper.pinfo("[mnoc_common_library]: Initalize recieve ports")
            rd = erot.FSP.FALCON_LOCKPMB_0.read()
            helper.log("read erot.FSP.FALCON_LOCKPMB_0 = %x" % rd.value)
            erot.FSP.FALCON_LOCKPMB_0.write(rd.value & 0xfffffffd)
            rd = erot.FSP.FALCON_LOCKPMB_0.read()
            helper.log("after configuring read erot.FSP.FALCON_LOCKPMB_0 = %x" % rd.value)

        if enable_interrupts:
 
            erot.FSP.MNOC_INTERRUPT_ENABLE_0_RECEIVEPORT_0.write(0x1)
            erot.FSP.MNOC_MNOC_COMMON_INTR_ENABLE_0_0.write(0x1)
            erot.FSP.MNOC_MNOC_PORT_CPU_INTR_AGGREGATOR_1_0.write(0x1<<port_num)
            helper.pinfo("[mnoc_common_library]: Enable interrupts")

    #######################################################
    # SEND PORT FUNCTIONS
    #######################################################    
    # Function to trigger send MNOC message
    def send_mnoc_message(self, port_num, wr_data):
        
        self.mem_load_data (len(wr_data), wr_data)
        
        helper.pinfo(f'Trigger send MNOC message')
        port_idx = "("+str(port_num)+")"

        if port_num == 0:
            if self.engine == "FSP":
                erot.FSP.MNOC_MESSAGE_OPERATION_0_SENDPORT_0.write(0x1)
            elif self.engine == "OOBHUB":
                test_api.oobhub_icd_write(0x15c100c, 0x1)
            else:
                helper.perror(f'[mnoc_common_library]: invalid engine')
        '''done = self.check_send_done(port_num)
        if done == False:
            helper.perror('Send message no interrupt')
        done = self.check_send_error_status(port_num)
        if done == False:
            helper.perror('Send message status not changed')'''
    
    def check_send_done (self, port_num):
        helper.pinfo("Read %s interrupt status register" % self.engine)
        status_change = False
        if port_num == 0:
            count = 0
            while status_change == False and count < 20:
                rd = erot.FSP.MNOC_INTERRUPT_STATUS_0_SENDPORT_0.read()
                if rd.value != 0x0:
                    status_change = True
                else :
                    status_change = False
                count += 1
        
        if status_change:
            return True
        else:
            return False
    
    def check_send_error_status (self, port_num):
        helper.pinfo(f"Read %s status registers" % self.engine)
        status_change = False
        if port_num == 0:
            count = 0
            while status_change == False and count < 10:
                rd1 = erot.FSP.MNOC_STATUS_0_SENDPORT_0.read()
                rd2 = erot.FSP.MNOC_STATUS_1_SENDPORT_0.read()
                if rd1.value != 0x0 and rd2.value != 0x0:
                    status_change = True
                else :
                    status_change = False
                count += 1
        
        if status_change:
            return True
        else:
            return False

    #######################################################
    #RECEIVE PORT FUNCTIONS
    #######################################################   
    def read_mnoc_message(self, port_num, msg_size):        
        port_idx = "("+str(port_num)+")"

        helper.pinfo("Read MNOC message")

        '''done = self.check_msg_received(port_idx)
        if done == False:
            helper.perror('Send message no interrupt')
        done = self.check_receive_error_status(port_idx)
        if done == False:
            helper.perror('Send message status not changed')'''
        rx_rd_message = falcondma_lib.read_falcon_mem(self.engine, self.dmem_rx_addr, msg_size//4) 
        return rx_rd_message
    
    def check_msg_received (self, port_idx):  
        helper.pinfo("Read %s interrupt status register" % self.engine)
        status_change = False
        if port_idx == 0:
            count = 0
            while status_change == False and count < 50:
                rd = erot.FSP.MNOC_INTERRUPT_STATUS_0_RECEIVEPORT_0.read()
                if rd.value != 0x0:
                    status_change = True
                else :
                    status_change = False
                count += 1
            
        if status_change:
            return True
        else:
            return False

    # Function to check status change in receive port status register
    def check_receive_error_status(self, port_idx):
        helper.pinfo(f"Read %s status registers" % self.engine)
        status_change = False
        if port_idx == 0:
            count = 0
            while status_change == False and count < 50:
                rd1 = erot.FSP.MNOC_STATUS_0_RECEIVEPORT_0.read()
                rd2 = erot.FSP.MNOC_STATUS_1_RECEIVEPORT_0.read()
                if rd1.value != 0x0 and rd2.value != 0x0:
                    status_change = True
                else :
                    status_change = False
                count += 1
            
        if status_change:
            return True
        else:
            return False

    ##################################################
    # MISC HELPER FUNCTIONS
    ##################################################
    
    # Function to break byte array into DW array for compare with read data from memory
    def payloadByteToDWarray(self, byteArray):
        dwArray = []
        ptr = 0
        tmpData = 0
        for i in range(len(byteArray)):
            tmpData = tmpData | byteArray[i]<<(ptr*8)
            ptr+=1
            if ptr == 4 or i == len(byteArray)-1:
                dwArray.append(tmpData)
                tmpData = 0
                ptr = 0
        return dwArray

    #######################################################
    # OOBHUB MNOC INITIALIZATION FUNCTIONS
    #######################################################
    
    # Function to initialize OOBHUB MNOC source send port
    def initialize_oobhub_mctp_send_port(self, target_engine, port_num, TAG, TO, max_message_size, enable_interrupts = False, extcomm = 0):
        
        helper.pinfo(f'Info: Initialize port')
        # Get engine EID for target engine
        target_eid = self.get_engine_eid(target_engine, extcomm)

        port_idx = "("+str(port_num)+")"

        if port_num == 0:
            test_api.oobhub_icd_write(0x15c0000, 0x1) #MNOC_MNOC_MCTP_SENDPORT_CTRL_0
            test_api.oobhub_icd_write(0x15c0010, (0x0|(TO << 24)|(0x0 << 18)|(TAG << 16)|(0x0 << 8)|target_eid)&0x810700FF) #MNOC_SETUP_CONFIG_0_SENDPORT_0
            test_api.oobhub_icd_write(0x15c1000, self.lower_tx_tcm&0xFFFFFFFE) #MNOC_MESSAGE_CONFIG_0_SENDPORT_0
            test_api.oobhub_icd_write(0x15c1004, self.higher_tx_tcm) #MNOC_MESSAGE_CONFIG_1_SENDPORT_0
            test_api.oobhub_icd_write(0x15c1008, max_message_size) #MNOC_MESSAGE_CONFIG_2_SENDPORT_0
            helper.pinfo("[mnoc_common_library]: Initalize oobhub send ports")   

        if enable_interrupts:
            test_api.oobhub_icd_write(0x15c101c, 0x1) #MNOC_INTERRUPT_ENABLE_0_SENDPORT_0
            test_api.oobhub_icd_write(0x15c0120, 0x1) #MNOC_MNOC_COMMON_INTR_ENABLE_0
            test_api.oobhub_icd_write(0x15c012c, 0x1) #MNOC_MNOC_PORT_CPU_INTR_AGGREGATOR_1
            helper.pinfo("[mnoc_common_library]: Enable interrupts on oobhub")
            
    # Function to initialize MNOC target receive port
    def initialize_oobhub_mctp_receive_port(self, target_engine, port_num, TAG, TO, max_message_size, enable_interrupts = False, extcomm = 0):
        
        helper.pinfo("Info: Initialize port")
        # Get engine EID for target engine
        target_eid = self.get_engine_eid(target_engine, extcomm)

        port_idx = "("+str(port_num)+")"

        if port_num == 0:
            test_api.oobhub_icd_write(0x15c0004, 0x1) #MNOC_MNOC_MCTP_RECEIVEPORT_CTRL_0
            test_api.oobhub_icd_write(0x15c0090, ((TO << 24)|(TAG << 16)|target_eid) & 0x810700FF) #MNOC_SETUP_CONFIG_0_RECEIVEPORT_0
            test_api.oobhub_icd_write(0x15c9000, self.lower_rx_tcm&0xFFFFFFFE) #MNOC_MESSAGE_CONFIG_0_RECEIVEPORT_0
            test_api.oobhub_icd_write(0x15c9004, self.higher_rx_tcm) #MNOC_MESSAGE_CONFIG_1_RECEIVEPORT_0
            test_api.oobhub_icd_write(0x15c9008, max_message_size) #MNOC_MESSAGE_CONFIG_2_RECEIVEPORT_0
            test_api.oobhub_icd_write(0x15c900c, 0x1) #MNOC_MESSAGE_OPERATION_0_RECEIVEPORT_0
            helper.pinfo("[mnoc_common_library]: Initalize oobhub recieve ports")

        if enable_interrupts: 
            test_api.oobhub_icd_write(0x15c901c, 0x1) #MNOC_INTERRUPT_ENABLE_0_RECEIVEPORT_0
            test_api.oobhub_icd_write(0x15c0120, 0x1) #MNOC_MNOC_COMMON_INTR_ENABLE_0_0
            test_api.oobhub_icd_write(0x15c012c, 0x1<<port_num) #MNOC_MNOC_PORT_CPU_INTR_AGGREGATOR_1_0
            helper.pinfo("[mnoc_common_library]: Enable interrupts")

    
