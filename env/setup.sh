#cp -rf ../openocd/src/erot_pkg_dev ./src/
#cp ../openocd/src/jtag/drivers/driver.c src/jtag/drivers/driver.c.new
#cp ../openocd/src/jtag/drivers/ftdi.c src/jtag/drivers/ftdi.c.new
#cp ../openocd/src/jtag/core.c src/jtag/core.c.new
#cp ../openocd/src/jtag/tcl.c src/jtag/tcl.c.new
#cp ../openocd/Makefile Makefile.new
#cp ../openocd/src/openocd.c src/openocd.c.new
./bootstrap 
./configure --enable-ftdi --enable-ft2232_ftd2xx --enable-maintainer-mode --enable-ft2232_libftdi
make
mv src/jtag/drivers/driver.c src/jtag/drivers/driver.c.old
mv src/jtag/drivers/ftdi.c src/jtag/drivers/ftdi.c.old
mv src/jtag/core.c src/jtag/core.c.old
mv src/jtag/tcl.c src/jtag/tcl.c.old
mv Makefile Makefile.old
mv src/openocd.c src/openocd.c.old
cp src/jtag/drivers/driver.c.new src/jtag/drivers/driver.c
cp src/jtag/drivers/ftdi.c.new src/jtag/drivers/ftdi.c
cp src/jtag/core.c.new src/jtag/core.c
cp src/jtag/tcl.c.new src/jtag/tcl.c
cp Makefile.new Makefile
cp src/openocd.c.new src/openocd.c
make