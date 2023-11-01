#include <iostream>
#include "local_util.h"
#include "ftd2xx.h"
#include "libft4222.h"

int main(void) {
    FT_HANDLE ftHandle = NULL;
    SMBus_init(1000, &ftHandle);

    const uint16 slaveAddr = 0x22;
    uint8 command = 0x39;
    uint8 data[] = {0x1A, 0x2B, 0x3C, 0x4D}; // little indian
    uint8 count = (sizeof(data)/sizeof(data[0]));

    SMBus_write(ftHandle, slaveAddr, command, count, data);
    
    SMBus_close(ftHandle);

    return 0;
 }

