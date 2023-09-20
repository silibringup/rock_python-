#ifndef __LOCAL_UTIL_C__
#define __LOCAL_UTIL_C__

#include <iostream>
#include <vector>
#include <sstream>
#include <iomanip>
#include "local_util.h"


std::string bytes_stringfy(uint8_t* data, uint32_t len){
    std::stringstream sstrm;
    for(uint32_t i=0; i<len; i++){
        sstrm << "0x" << std::uppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << (unsigned)data[i];
        if(i < len-1){
            sstrm << " ";
        }
    }
    return sstrm.str();
}


int SMBus_init(uint32_t i2c_kbps, FT_HANDLE* ftHandle){
    FT_STATUS ftStatus;
    FT4222_STATUS ft4222Status;
    
    ftStatus = FT_Open(0, ftHandle);
    if (FT_OK != ftStatus){
        std::cerr << "Open ftHandle failed!" << std::endl;
        return 0;
    } else {
        std::cout << "Open ftHandle succeeded!" << std::endl;
    }

    // initial i2c master with 1000K bps
    ft4222Status = FT4222_I2CMaster_Init(*ftHandle, i2c_kbps);
    if (FT4222_OK != ft4222Status){
        std::cerr << "i2c master init failed!" << std::endl;
        return 0;
    } else {
        std::cout << "i2c master init succeeded!" << std::endl;
    }
    return 1;
}


void SMBus_close(FT_HANDLE ftHandle){
    FT4222_UnInitialize(ftHandle);
    FT_Close(ftHandle);
}



int SMBus_write(FT_HANDLE ftHandle, uint16_t slaveAddr, uint8_t command, uint8_t count, uint8_t data[]){
    FT4222_STATUS ft4222Status;
    uint8_t* sm_stream = new uint8_t[count + 2];
    sm_stream[0] = command;
    sm_stream[1] = count;
    for(int i=2;i<count+2;i++){
        sm_stream[i] = data[i-2];
    }
    // std::cout << "SMBus intend to write: " << bytes_stringfy(sm_stream, count+2) << std::endl;
    uint16_t sizeTransferred = 0;
    // write 4 bytes data to master
    ft4222Status = FT4222_I2CMaster_Write(ftHandle, slaveAddr, sm_stream, count+2, &sizeTransferred);
    if (FT4222_OK == ft4222Status){
        // std::cout << "Write: ";
        // std::cout << bytes_stringfy(sm_stream, count+2) << std::endl;
    }
    else{
        std::cerr << "Write failed!" << std::endl;
        return 0;
    }
    delete [] sm_stream;
    
    return 1;
}


int SMBus_read(FT_HANDLE ftHandle, uint16_t slaveAddr, uint8_t command, uint16_t desire_n_byte, uint8_t data[]){
    FT4222_STATUS ft4222Status;
    uint16_t sizeTransferred = 0;
    uint8_t command_arr[1] = {command};
    // flag: START, Repeated_START, STOP, START_AND_STOP
    ft4222Status = FT4222_I2CMaster_WriteEx(ftHandle, slaveAddr, START, &command_arr[0], 1, &sizeTransferred);
    if (FT4222_OK == ft4222Status){
        // std::cout << "SMBus Read Command: " << bytes_stringfy(command_arr, 1) << std::endl;
    }
    else{
        std::cerr << "Write failed!" << std::endl;
        return 0;
    }

    ft4222Status = FT4222_I2CMaster_ReadEx(ftHandle, slaveAddr, Repeated_START | STOP, data, desire_n_byte, &sizeTransferred);
    if (FT4222_OK == ft4222Status){
        sizeTransferred = data[0]; // data[0] is count!

        // shift out [Count] byte
        for(int i=0;i<sizeTransferred;i++){
            data[i] = data[i+1];
        }
        // std::cout << 
        // "SMBus Read Back " << (uint32_t)sizeTransferred << " bytes, "
        // "Data: " << bytes_stringfy(data, sizeTransferred) << std::endl;
    }
    else{
        std::cerr << "Read failed!" << std::endl;
        return 0;
    }

    return sizeTransferred;
}


#endif