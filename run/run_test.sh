export PYTHONPATH=/home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/tests

sudo ./clean.sh
sleep 1
sudo raspi-gpio set 23 op dl; sudo raspi-gpio set 23 op dh
sleep 1

sudo /home/erot/dev/recovery_regression/openocd/src/openocd -f /home/erot/dev/recovery_regression/sr01.cfg -socket 1234 -no_scan_verbo &
python -B /home/erot/dev/recovery_regression/testlist/erot_j2h_debug_test.py --target fpga --platform JTAG --disable_peripheral_init_agent 

sleep 1

#python /home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/logcheck
sudo ./clean.sh