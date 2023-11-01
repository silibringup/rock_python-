#include <iostream>
#include "local_util.h"
#include "ftd2xx.h"
#include "libft4222.h"

int main(void) {
    FT_HANDLE ftHandle = NULL;
    SMBus_init(1000, &ftHandle);

    // uint16 sizeTransferred = 0;
    const uint16 slaveAddr = 0x22;
    uint8 command = 0x39;
    uint32 desire_n_byte = 20;
    uint8* recvBuf = new uint8[desire_n_byte];

    uint16_t n_rd = SMBus_read(ftHandle, slaveAddr, command, desire_n_byte, recvBuf);
    printf("read %d bytes\n", n_rd);

    SMBus_close(ftHandle);

    return 0;
 }