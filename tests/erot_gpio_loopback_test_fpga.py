#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

RPI_AP0_BOOT_CTRL_0_N = 11
RPI_AP0_BOOT_CTRL_1_N = 7
RPI_EROT_REQ_AP0_N = 38
RPI_EROT_GNT_AP0_N = 40
RPI_AP0_FW_INTR_N = 35
RPI_AP0_MUX_CTRL_N = 18
RPI_AP0_PGOOD = 16
RPI_RESET_N = 13
RPI_RESET_IND_N = 15
RPI_RESET_MON_N = 12

with Test(sys.argv) as t:

    ap0_input_value_reg_list = ['A_INPUT_00_0','A_INPUT_01_0','A_INPUT_02_0','A_INPUT_03_0','A_INPUT_04_0','A_INPUT_05_0', 'A_INPUT_06_0', 'B_INPUT_00_0', 'B_INPUT_01_0', 'B_INPUT_02_0']
    ap0_enable_reg_list = ['A_ENABLE_CONFIG_00_0','A_ENABLE_CONFIG_01_0','A_ENABLE_CONFIG_02_0','A_ENABLE_CONFIG_03_0','A_ENABLE_CONFIG_04_0','A_ENABLE_CONFIG_05_0', 'A_ENABLE_CONFIG_06_0', 'B_ENABLE_CONFIG_00_0', 'B_ENABLE_CONFIG_01_0', 'B_ENABLE_CONFIG_02_0']
    ap0_output_control_reg_list = ['A_OUTPUT_CONTROL_00_0','A_OUTPUT_CONTROL_01_0','A_OUTPUT_CONTROL_02_0','A_OUTPUT_CONTROL_03_0','A_OUTPUT_CONTROL_04_0','A_OUTPUT_CONTROL_05_0', 'A_OUTPUT_CONTROL_06_0', 'B_OUTPUT_CONTROL_00_0', 'B_OUTPUT_CONTROL_01_0', 'B_OUTPUT_CONTROL_02_0']
    ap0_value_reg_list = [ 'A_OUTPUT_VALUE_00_0','A_OUTPUT_VALUE_01_0','A_OUTPUT_VALUE_02_0','A_OUTPUT_VALUE_03_0','A_OUTPUT_VALUE_04_0','A_OUTPUT_VALUE_05_0', 'A_OUTPUT_VALUE_06_0', 'B_OUTPUT_VALUE_00_0', 'B_OUTPUT_VALUE_01_0', 'B_OUTPUT_VALUE_02_0']

    AP0_GPIO_LIST = [ 
        {'name':'AP0_BOOT_CTRL_0_N_GP01', 'port':'A', 'pin':'00' }, 
        {'name':'AP0_BOOT_CTRL_1_N_GP02', 'port':'A', 'pin':'01' }, 
        {'name':'EROT_REQ_AP0_N_GP03', 'port':'A', 'pin':'02' }, 
        {'name':'EROT_GNT_AP0_N_GP04', 'port':'A', 'pin':'03' }, 
        {'name':'AP0_FW_INTR_N_GP05', 'port':'A', 'pin':'04' }, 
        {'name':'AP0_MUX_CTRL_N_GP06', 'port':'A', 'pin':'05' }, 
        #{'name':'AP0_PGOOD_GP07', 'port':'A', 'pin':'06' }, 
        {'name':'AP0_RESET_N_GP08', 'port':'B', 'pin':'00' }, 
        {'name':'AP0_RESET_IND_N_GP09', 'port':'B', 'pin':'00' }, 
        {'name':'AP0_RESET_MON_N_GP10', 'port':'B', 'pin':'00' }, 
     ]
     
    LOOPBACK_GPIO_LIST = [
        [{'name':'AP1_BOOT_CTRL_0_N_GP12', 'port':'C', 'pin':'00'},
         {'name':'AP1_BOOT_CTRL_1_N_GP13', 'port':'C', 'pin':'01'}],
        [{'name':'EROT_REQ_AP1_N_GP14', 'port':'C', 'pin':'02'},
         {'name':'EROT_GNT_AP1_N_GP15', 'port':'C', 'pin':'03'}],       
        [{'name':'AP1_FW_INTR_N_GP16', 'port':'C', 'pin':'04'},
         {'name':'AP1_MUX_CTRL_N_GP17', 'port':'C', 'pin':'05'}],
        #[{'name':'AP1_PGOOD_GP18', 'port':'C', 'pin':'06'},
        # {'name':'AP1_RESET_N_GP19', 'port':'D', 'pin':'00'}],
        [{'name':'AP1_RESET_IND_N_GP20', 'port':'D', 'pin':'01'},
         {'name':'AP1_RESET_MON_N_GP21', 'port':'D', 'pin':'02'}],
        [{'name':'EROT_ERROR_N', 'port':'E', 'pin':'00'},
         {'name':'EROT_OOB_DSPI_INTR_N', 'port':'E', 'pin':'02'}]       
    ] 
    
    def parse_args():
        t.parser.add_argument("--fpga",type = int, help="running on fpga environment", default=0)
        opts, unknown = t.parser.parse_known_args(sys.argv[1:])
        return opts   

    def ap0_padctrl(input):
        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)   

        erot.PADCTRL_E.AP0_BOOT_CTRL_0_N_GP01_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_BOOT_CTRL_1_N_GP02_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.EROT_REQ_AP0_N_GP03_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.EROT_GNT_AP0_N_GP04_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_FW_INTR_N_GP05_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_MUX_CTRL_N_GP06_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_PGOOD_GP07_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_N_GP08_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_IND_N_GP09_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
        erot.PADCTRL_E.AP0_RESET_MON_N_GP10_0.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)

    def ap1_oobhub_padctrl(loopback_pair_list, input):
        for gpio_pair in loopback_pair_list:
            if gpio_pair[0]['port'] != 'E':
                gpio_reg_1 = erot.PADCTRL_W.get_reg_by_name(gpio_pair[0]['name']+"_0")
                gpio_reg_2 = erot.PADCTRL_W.get_reg_by_name(gpio_pair[1]['name']+"_0")
            else:
                gpio_reg_1 = erot.PADCTRL_S.get_reg_by_name(gpio_pair[0]['name']+"_0")
                gpio_reg_2 = erot.PADCTRL_S.get_reg_by_name(gpio_pair[1]['name']+"_0")               
            
            gpio_reg_1.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
            gpio_reg_2.debug_update(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=not input)

            gpio_reg_1.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=input)
            gpio_reg_2.debug_poll(TRISTATE=0,GPIO_SF_SEL=0,E_INPUT=not input)        

    def check_input_value(gpio):
        gpio_reg = erot.GPIO.get_reg_by_name( f"{gpio['port']}_INPUT_{gpio['pin']}_0")
        rd = gpio_reg.debug_read()
        if rd.value != 1:
            helper.perror("Reg Read/Write Fail -> %s" % str(gpio_reg))

    def rpi_check_input_value(gpio,fpga,exp_value):
        if(fpga):
            helper.pinfo(gpio['name'].lower())
            value = helper.gpio_read(gpio['name'].lower())
            if value != exp_value:
                helper.perror("rpi Read Fail -> gpio:%s" % str(gpio['name']))
        else:
            if helper.target == 'simv_fpga':
                helper.hdl_wait(f"ntb_top.u_nv_fpga_dut.dpcs.dpcs_{gpio['name'].lower()}",exp_value)
            else:
                helper.hdl_wait(f"ntb_top.u_nv_top.dpcs.dpcs_{gpio['name'].lower()}",exp_value)

        #if value != 1:
        #    helper.perror("rpi Read Fail -> gpio:%s" % str(gpio['name']))

    def rpi_config_output_value(gpio,value,fpga):
        if(fpga):
            helper.gpio_write(gpio['name'].lower(), value)
        else:
            if helper.target == 'simv_fpga':
                helper.hdl_force(f"ntb_top.u_nv_fpga_dut.dpcs.dpcs_{gpio['name'].lower()}", value)
            else:
                helper.hdl_force(f"ntb_top.u_nv_top.dpcs.dpcs_{gpio['name'].lower()}", value)
                     
    def ap0_gpio_test(gpio_list,fpga):
        ap0_padctrl(0)
        helper.pinfo('ap0 out, rpi in')
        for gpio in gpio_list:
            config_output_enable(gpio)
            config_output_control(gpio)
            config_output_value(gpio,1)
            rpi_check_input_value(gpio,1,fpga)    
        helper.pinfo('ap0 out finish')

        ap0_padctrl(1)
        helper.pinfo('ap0 in, rpi out')
        for gpio in gpio_list:
            config_input_enable(gpio)
            rpi_config_output_value(gpio,1,fpga)
            check_input_value(gpio)    
        helper.pinfo('ap0 in finish')

    def ap1_oobhub_gpio_test(loopback_pair_list):
        ap1_oobhub_padctrl(loopback_pair_list,0)
        helper.pinfo('0 out, 1 in')
        for gpio_pair in loopback_pair_list:
            config_output_enable(gpio_pair[0])
            config_output_control(gpio_pair[0])
            config_output_value(gpio_pair[0],1)
        for gpio_pair in loopback_pair_list:
            config_input_enable(gpio_pair[1])
            check_input_value(gpio_pair[1])         
        helper.pinfo('0 out finish')

        ap1_oobhub_padctrl(loopback_pair_list,1)
        helper.pinfo('1 out, 0 in')
        for gpio_pair in loopback_pair_list:
            config_output_enable(gpio_pair[1])
            config_output_control(gpio_pair[1])
            config_output_value(gpio_pair[1],1)
        for gpio_pair in loopback_pair_list:
            config_input_enable(gpio_pair[0])
            check_input_value(gpio_pair[0])           
        helper.pinfo('0 in finish')
    
    def config_output_enable(gpio):
        gpio_reg = erot.GPIO.get_reg_by_name(f"{gpio['port']}_ENABLE_CONFIG_{gpio['pin']}_0")
        gpio_reg.debug_update(GPIO_ENABLE=1, IN_OUT=1, TRIGGER_TYPE=2, TRIGGER_LEVEL=1)

    def config_output_value(gpio, value):
        gpio_reg = erot.GPIO.get_reg_by_name(f"{gpio['port']}_OUTPUT_VALUE_{gpio['pin']}_0")
        gpio_reg.debug_write(value)

    def config_output_control(gpio):
        gpio_reg = erot.GPIO.get_reg_by_name(f"{gpio['port']}_OUTPUT_CONTROL_{gpio['pin']}_0")
        gpio_reg.debug_write(0)

    def config_input_enable(gpio):
        gpio_reg = erot.GPIO.get_reg_by_name(f"{gpio['port']}_ENABLE_CONFIG_{gpio['pin']}_0")
        gpio_reg.debug_update(GPIO_ENABLE=1, IN_OUT=0, TRIGGER_TYPE=2, TRIGGER_LEVEL=1)           

    helper.wait_sim_time('us', 50)
    helper.hdl_force('ntb_top.u_nv_fpga_dut.u_nv_top_fpga.u_nv_top_wrapper.u_nv_top.nvjtag_sel', 1)

    helper.jtag.Reset(0)
    helper.jtag.DRScan(100, hex(0x0)) #add some delay as jtag only work when nvjtag_sel stable in real case
    helper.jtag.Reset(1)  

    #unlock j2h interface
    helper.pinfo(f'j2h_unlock sequence start')
    helper.j2h_unlock()
    helper.pinfo(f'j2h_unlock sequence finish')
    #make sure l3 reset is released
    erot.RESET.NVEROT_RESET_CFG.SW_L3_RST_0.debug_poll(timeout=10, RESET_LEVEL3=1)
    #reset uart 
    erot.RESET.NVEROT_RESET_CFG.SW_GPIO_CTRL_RST_0.debug_update(RESET_GPIO_CTRL=1)
    helper.set_gpio_loop_back(1)
    LOG("START GPIO LOOPBACK SANITY TEST")

    options = parse_args() 
    fpga = int(options.fpga)
    
    #ap0_gpio_test(AP0_GPIO_LIST,fpga)
    ap1_oobhub_gpio_test(LOOPBACK_GPIO_LIST)