#!/home/utils/Python/3.8/3.8.6-20201005/bin/python3
from driver import * 

with Test(sys.argv) as t:
    
    helper.log("Test start")
    helper.gpio_write('ap1_boot_ctrl_0_n_gp12',1)
    helper.wait_rpi_time(1000,1) # wait 1000 ms 
    helper.gpio_write('ap1_boot_ctrl_0_n_gp12',0)
    helper.wait_rpi_time(1000,1) # wait 1000 ms 
    helper.gpio_write('ap1_boot_ctrl_0_n_gp12',1)
    helper.wait_rpi_time(1000) # wait 1000 us 
    helper.gpio_write('ap1_boot_ctrl_0_n_gp12',0)
    helper.wait_rpi_time(1000) # wait 1000 us 

    #value = helper.gpio_read("ap0_qspi_io0")
    #helper.log("read ap0_qspi_io0 = %s" % value)
    #res = helper.hdl_read("ntb_top.u_nv_top.ap0_qspi_io0")
    #print(res)

    #helper.wait_sim_time("us",10)
    #helper.log("write ap0_qspi_io0 to 0")
    #helper.gpio_write("ap0_qspi_io0", 0)

    #helper.wait_sim_time("us", 1)
    #helper.hdl_force("ntb_top.u_nv_top.ap0_qspi_io0", 1)
    #helper.wait_sim_time("ns", 1)
    #res = helper.hdl_read("ntb_top.u_nv_top.ap0_qspi_io0")
    #print("=================")
    #print(res)

    #value = helper.gpio_read("ap0_qspi_io0")
    #helper.log("read ap0_qspi_io0 = %s" % value)

    #helper.wait_sim_time("us",10)
    #helper.log("write ap0_qspi_io0 to 1")
    #helper.gpio_write("ap0_qspi_io0", 1)

    ##helper.wait_sim_time("ns", 1)
    #value = helper.gpio_read("ap0_qspi_io0")
    #helper.log("read ap0_qspi_io0 = %s" % value)

    #helper.log("Test wait rpi time")
    #helper.wait_rpi_time(22)
    #helper.log("Test wait rpi time done")
   
    helper.log("Test done")

