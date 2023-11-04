#files has changes
#cp ../openocd/src/jtag/drivers/driver.c src/jtag/drivers/
#cp ../openocd/src/jtag/drivers/ftdi.c src/jtag/drivers/
#cp ../openocd/src/jtag/core.c src/jtag/
#cp ../openocd/src/jtag/tcl.c src/jtag/
#cp ../openocd/src/helper/options.c src/helper/
#cp ../openocd/src/openocd.c src/
#cp -rf ../openocd/src/erot_pkg_dev ./src/


./bootstrap 
./configure --enable-ftdi --enable-ft2232_ftd2xx --enable-maintainer-mode --enable-ft2232_libftdi
cp Makefile Makefile.old
cp Makefile.new Makefile
make

