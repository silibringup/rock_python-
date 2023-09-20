export PYTHONPATH=/home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/tests

sudo ./clean.sh
sleep 1
sudo raspi-gpio set 23 op dl; sudo raspi-gpio set 23 op dh
sleep 1

sudo /home/erot/dev/recovery_regression/openocd/src/openocd -f /home/erot/dev/recovery_regression/sr01.cfg -socket 1234 -no_scan_verbo &
python -B /home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/tests/recovery_test/rcv_test.py --ip 127.0.0.1 --port 1234 --platform JTAG --target fpga --disable_peripheral_init_agent --fmc_bin /home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/tests/recovery_test/mashUpBin.bin --testlist /home/erot/dev/recovery_regression/testlist

sleep 1
sudo ./clean.sh

python /home/erot/dev/recovery_regression/openocd/src/erot_pkg_dev/logcheck