#files has changes
#cp ../openocd/src/jtag/drivers/driver.c src/jtag/drivers/
#cp ../openocd/src/jtag/drivers/ftdi.c src/jtag/drivers/
#cp ../openocd/src/jtag/core.c src/jtag/
#cp ../openocd/src/jtag/tcl.c src/jtag/
#cp ../openocd/src/helper/options.c src/helper/
#cp ../openocd/src/openocd.c src/
#cp -rf ../openocd/src/erot_pkg_dev ./src/

# install dependency
sudo apt install automake autoconf build-essential texinfo libtool libftdi-dev libusb-1.0-0-dev
sudo dpkg -i wiringpi-latest.deb

# install libftd2xx driver
sudo cp ./libftd2xx/build/libftd2xx.* /usr/local/lib
sudo chmod 0755 /usr/local/lib/libftd2xx.so.1.4.27
sudo ln -sf /usr/local/lib/libftd2xx.so.1.4.27 /usr/local/lib/libftd2xx.so
sudo cp ./libftd2xx/ftd2xx.h  /usr/local/include
sudo cp ./libftd2xx/WinTypes.h  /usr/local/include
sudo ldconfig -v

# install libft4222-linux driver
cd libft4222-linux-1.4.4.170
sudo ./install4222.sh
sudo cp ./build-arm-v7-hf/libft4222.so.1.4.4.170 /usr/local/lib/

# install test dependecy
sudo apt install python3-termcolor
sudo apt install python3-yaml 
cd ..


./bootstrap 
./configure --enable-ftdi --enable-ft2232_ftd2xx --enable-maintainer-mode --enable-ft2232_libftdi
make

