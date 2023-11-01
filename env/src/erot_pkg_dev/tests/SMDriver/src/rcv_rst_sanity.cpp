#include <iostream>
#include <fstream>
#include <cstring>
#include <chrono>
#include <thread>
#include "local_util.h"

int BMC_poll(FT_HANDLE ftHandle, uint16_t slaveAddr, uint8_t cmd, uint16_t exp, uint16_t mask, uint32_t timeout){
    int ans = 1;
    int cnt = 0;
    uint16_t rd = exp - 1;
    uint8_t recvBuf[32] = {0};

    while((rd & mask) != exp){
        if(cnt >= timeout){
            ans = 0;
            break;
        }
        uint16_t n_rd = SMBus_read(ftHandle, slaveAddr, cmd, 32, recvBuf);
        rd = recvBuf[0];
        cnt++;
        printf("Poll 0x%x with command %d %d times\n", slaveAddr, cmd, cnt);
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }

    printf("rd = 0x%x\n", rd);

    return ans;
}


int main(void) {
    const uint16_t slaveAddr = 0x69;
    FT_HANDLE ftHandle = NULL;
    SMBus_init(20, &ftHandle);

    uint8_t command = 0;
    uint8_t data[] = {0x01, 0x0F, 0x00}; // little Endian
    uint8_t count = (sizeof(data)/sizeof(data[0]));

    // reset command
    command = 37;
    SMBus_write(ftHandle, slaveAddr, command, count, data);
    
    std::this_thread::sleep_for(std::chrono::seconds(2));
    
    command = 36;
    if(!BMC_poll(ftHandle, slaveAddr, command, 0x3, 0xff, 200)){
        printf("[ERROR] Poll 0x%x with command %d failed!\n", slaveAddr, command);
        return 1;
    }
    command = 39;
    if(!BMC_poll(ftHandle, slaveAddr, command, 0x1, 0xff, 200)){
        printf("[ERROR] Poll 0x%x with command %d failed!\n", slaveAddr, command);
        return 1;
    }

    // write RECOVERY_CTRL
    printf("Write RECOVERY_CTRL register\n");
    data[0] = 0x00;
    data[1] = 0x01;
    data[2] = 0x00;
    command = 38;
    SMBus_write(ftHandle, slaveAddr, command, 3, data);

    command = 36;
    if(!BMC_poll(ftHandle, slaveAddr, command, 0x4, 0xff, 200)){
        printf("[ERROR] Poll 0x%x with command %d failed!\n", slaveAddr, command);
        return 1;
    }
    command = 39;
    if(!BMC_poll(ftHandle, slaveAddr, command, 0x1, 0xff, 200)){
        printf("[ERROR] Poll 0x%x with command %d failed!\n", slaveAddr, command);
        return 1;
    }

    SMBus_close(ftHandle);

    printf("Test passed\n");

    return 0;
 }
