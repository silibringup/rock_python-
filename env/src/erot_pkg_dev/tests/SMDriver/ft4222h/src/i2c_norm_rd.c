#include "local_util.h"
#include "ftd2xx.h"
#include "libft4222.h"

int main(void) {
    FT_HANDLE ftHandle = NULL;
    FT_STATUS ftStatus;
    FT4222_STATUS ft4222Status;

    ftStatus = FT_Open(0, &ftHandle);
    if (FT_OK != ftStatus){
        std::cerr << "Open ftHandle failed!" << std::endl;
        return 1;
    }

    // initial i2c master with 1000K bps
    ft4222Status = FT4222_I2CMaster_Init(ftHandle, 1000);
    if (FT4222_OK != ft4222Status){
        std::cerr << "i2c master init failed!" << std::endl;
        return 1;
    }

    const uint16 slaveAddr = 0x22;
    uint8 slave_data[4];
    uint16 sizeTransferred = 0;
    // read 4 bytes data from master
    ft4222Status = FT4222_I2CMaster_Read(ftHandle, slaveAddr, slave_data, sizeof(slave_data), &sizeTransferred);
    if (FT4222_OK == ft4222Status){
        std::cout << "Read: ";
        std::cout << bytes_stringfy(slave_data, 4) << std::endl;
    }
    else{
        std::cerr << "Read failed!" << std::endl;
        return 1;
    }

    FT4222_UnInitialize(ftHandle);
    FT_Close(ftHandle);

    return 0;
 }


