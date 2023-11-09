"""
OOBHUB Common library
This file contains all the functions to configure OOBHUB into state for tests requirement
"""
from driver import *
import argparse
from enum import Enum

class oobhubCommonLibrary():
    #def __init__(self):

    #function to put the OOBHUB into bypass mode
    def configBypassMode(self):
        test_api.oobhub_icd_write(0x14420f4,(0x1<<1)|(0x0)) #NV_COOBHUB_MCTP_BDG_CFG_0.BYPASS_ENABLE=1 .ENABLE=0

    # Set RXMEM start address
    def setRxmemStartAddr(self, phy_type, addr):
        # set register name based on PHY type
        if (phy_type == "I2C"):
            phy_reg_name = "NV_COOBHUB_MCTP_PHY_PHY1_RXMEM_START_ADDR"
        elif (phy_type == "I3C"):
            phy_reg_name = "NV_COOBHUB_MCTP_PHY_PHY2_RXMEM_START_ADDR"
        elif (phy_type == "BYPASS"):
            test_api.oobhub_icd_write(0x1442468,addr) #NV_COOBHUB_MCTP_BDG_BYP_RXMEM_START_ADDR
        else :
            helper.prror("[oobhub_common_lib] no PHY type specified for Rx memory start address write")

    # Function to write to RX command FIFO
    def writeRxCmdFifo(self, phy_type, offset, dw_cnt, pad_len):
        # set register name based on PHY type
        if (phy_type == "I2C"):
            phy_reg_name = "NV_COOBHUB_MCTP_PHY_PHY1_RXMEM_CMDFIFO_OP"
        elif (phy_type == "I3C"):
            phy_reg_name = "NV_COOBHUB_MCTP_PHY_PHY2_RXMEM_CMDFIFO_OP"
        elif (phy_type == "BYPASS"):
            phy_reg_name = "NV_COOBHUB_MCTP_BDG_BYP_RXMEM_CMDFIFO_OP"
            test_api.oobhub_icd_write(0x1442470,(offset<<0)|(dw_cnt<<16)|(pad_len<<24)|(1<<31)) #NV_COOBHUB_MCTP_BDG_BYP_RXMEM_CMDFIFO_OP
        else :
            helper.prror("[oobhub_common_lib] no PHY type specified for command FIFO write")



