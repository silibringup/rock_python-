#ifndef __LOCAL_UTIL_C__
#define __LOCAL_UTIL_C__

#include <iostream>
#include <vector>
#include <sstream>
#include <iomanip>
#include "local_util.h"
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>

#define SLAVE_SELECT(x) (1 << (x))

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


int SPI_init(FT_HANDLE* ftHandle){
    FT_STATUS ftStatus;
    uint32_t num_devs = 0;
    uint8_t index = 0;

    printf("SPI FT4222 detect begin\n");
    if(FT_OK != FT_CreateDeviceInfoList(&num_devs))
    {
        printf("FT_CreateDeviceInfoList fail\n");
        return 0;
    }
    if(0 == num_devs)
    {
        printf("Cannot find FT4222\n");
        return 0;
    }
    std::vector<FT_DEVICE_LIST_INFO_NODE> dev_info(num_devs);
    if(FT_OK != FT_GetDeviceInfoList(dev_info.data(), &num_devs))
    {
        printf("FT_GetDeviceInfoList fail\n");
        return 0;
    }
    for(index = 0 ; index<(int)num_devs ; index++)
    {   
        size_t descLen = strlen(dev_info[index].Description);
        printf("device_index %0d, type %0d,Locid %d, desc %s\n",index,dev_info[index].Type,dev_info[index].LocId,dev_info[index].Description);
        if(FT_DEVICE_4222H_1_2 == dev_info[index].Type && 'C' == dev_info[index].Description[descLen - 1])
        {
            printf("Find FT4222 location ID is %d\n", dev_info[index].LocId);
            ftStatus = FT_OpenEx((PVOID)(uintptr_t)dev_info[index].LocId, 
                                 FT_OPEN_BY_LOCATION, 
                                 ftHandle);
            if (FT_OK != ftStatus){
                std::cerr << "SPI Open ftHandle failed! Status :" << ftStatus << std::endl;
                return 0;
            } else {
                std::cout << "SPI Open ftHandle succeeded!" << std::endl;
            }                                 
            break;
        }
    }

    FT4222_ClockRate clk;
    FT4222_STATUS ft4222Status;

    ft4222Status = FT4222_SetClock(*ftHandle,SYS_CLK_24);
    if (FT4222_OK != ft4222Status){
        std::cerr << "FT4222 clock set failed! Status :" << FT4222_STATUS(ft4222Status) << std::endl;
        return 0;
    } else {
        std::cout << "FT4222 Set Core Clock succeeded " << std::endl;
    }   
    
    ft4222Status = FT4222_GetClock(*ftHandle,&clk);

    if (FT4222_OK != ft4222Status){
        std::cerr << "FT4222 clock get failed! Status :" << FT4222_STATUS(ft4222Status) << std::endl;
        return 0;
    } else {
        std::cout << "FT4222 Core Clock : "<< clk << "  (0 : 60, 1 : 24, 2 : 48, 3 : 80MHZ)" << std::endl;
    }


	//GPIO init
	if(wiringPiSetupGpio() == -1){
        std::cerr << "GPIO initialization Succeeded" << std::endl;
        return 0;
	}else{
        std::cout << "GPIO initialization Succeeded" << std::endl;
	}
    return 1;
    //ftStatus = FT_Open(4, ftHandle);
    //if (FT_OK != ftStatus){
    //    std::cerr << "SPI Open ftHandle failed! Status :" << ftStatus << std::endl;
    //    return 0;
    //} else {
    //    std::cout << "SPI Open ftHandle succeeded!" << std::endl;
    //}
    //return 1;
}


int SPI_config(FT_HANDLE ftHandle,FT4222_SPIClock clock,uint32_t cs_id){
    FT4222_STATUS ft4222Status;
    FT_STATUS     ftStatus;
    uint8_t       csMap;
    int           cs_pin = 25; //apx_qspi_erot_cs_n

    // initial SPI master 

    if (cs_id == 2){
        csMap = SLAVE_SELECT(0);
        pinMode (cs_pin, OUTPUT); 
    } else {
        csMap = SLAVE_SELECT(cs_id);
    }


    ft4222Status = FT4222_SPIMaster_Init(ftHandle,
                                        SPI_IO_SINGLE, // 1 lane
                                        clock,
                                        CLK_IDLE_LOW,
                                        CLK_LEADING,
                                        csMap
                                        );
    
    if (FT4222_OK != ft4222Status){
        std::cerr << "SPI master init failed! Status :" << FT4222_STATUS(ft4222Status) << std::endl;
        return 0;
    } else {
        std::cout << "SPI master int succeeded!" << std::endl;
    }

    ft4222Status = FT4222_SPI_ResetTransaction(ftHandle,0);
    //ft4222Status = FT4222_SPI_Reset(ftHandle);
    if (FT4222_OK != ft4222Status){
        std::cerr << "SPI master trans reset failed! Status :" << FT4222_STATUS(ft4222Status) << std::endl;
        return 0;
    } else {
        std::cout << "SPI master trans reset succeeded!" << std::endl;
    }
    
    //ft4222Status = FT4222_SPI_SetDrivingStrength(ftHandle,
    //                                             DS_16MA,
    //                                             DS_16MA,
    //                                             DS_16MA);
    //if (FT4222_OK != ft4222Status){
    //    std::cerr << "SPI master drivingstrength failed! Status :" << FT4222_STATUS(ft4222Status) << std::endl;
    //    return 0;
    //}else{
    //    std::cout << "SPI master drivingstrength succeeded!" << std::endl;
    //}

    return 1;
}


void SPI_close(FT_HANDLE ftHandle){
    FT4222_UnInitialize(ftHandle);
    FT_Close(ftHandle);
}

int SPI_read(FT_HANDLE ftHandle,uint32_t cs_id,int spiMode, int sendLen, uint8_t* sbuf,int recvLen, uint8_t* rbuf,bool deassert, int singleBytes){
    FT4222_STATUS status{};
    int           cs_pin = 25; //apx_qspi_erot_cs_n

    // Single mode
    if (spiMode == SPI_IO_SINGLE) {
        uint16_t sizeTransferred=0;
		if (cs_id == 2){ //spi target cs control 
			digitalWrite(cs_pin, LOW);
		}
        status = FT4222_SPIMaster_SingleRead(ftHandle, rbuf, recvLen, &sizeTransferred, deassert);
        if (cs_id == 2){ //spi target cs control 
            delay(500);
			digitalWrite(cs_pin, HIGH);
		}
        if (FT4222_OK == status){
        }
        else{
            std::cerr << "SPI Single Read failed!" << std::endl;
        }
        return sizeTransferred; 
        
    }
    else {  // dual quad mode

        // set mode : DSPI or QSPI
        status = FT4222_SPIMaster_SetLines(ftHandle,FT4222_SPIMode(spiMode));
        if (FT4222_OK == status){
        }
        else{
            std::cerr << "SPI setlines failed!" << std::endl;
        }

        if (singleBytes == -1) { // send all as single bytes
            singleBytes = sendLen;
        }
        sendLen -= singleBytes;
        uint32_t sizeTransferred=0;
		if (cs_id == 2){ //spi target cs control 
			digitalWrite(cs_pin, LOW);
		}
        status = FT4222_SPIMaster_MultiReadWrite(ftHandle, rbuf, sbuf, singleBytes,sendLen, recvLen,
                                                 &sizeTransferred);
		if (cs_id == 2){ //spi target cs control 
            delay(500);
			digitalWrite(cs_pin, HIGH);
		}
        if (FT4222_OK == status){
        }
        else{
            std::cerr << "SPI multi read failed!" << std::endl;
        } 
        return sizeTransferred;

    }

}


int SPI_write(FT_HANDLE ftHandle,uint32_t cs_id,int spiMode, int sendLen, uint8_t* sbuf,bool deassert, int singleBytes){
    FT4222_STATUS status{};
    int           cs_pin = 25; //apx_qspi_erot_cs_n
    
    // Single mode
    if (spiMode == SPI_IO_SINGLE) {
        uint16_t sizeTransferred=0;
        if (cs_id == 2){ //spi target cs control 
			digitalWrite(cs_pin, LOW);
		}
        status = FT4222_SPIMaster_SingleWrite(ftHandle, sbuf, sendLen, &sizeTransferred, deassert);
        if (cs_id == 2){ //spi target cs control 
            delay(500);
			digitalWrite(cs_pin, HIGH);
		}
        if (FT4222_OK == status){
            std::cout << "SPI single write succeeded! " << sizeTransferred << " bytes" << std::endl;
        }
        else{
            std::cerr << "SPI Single Write failed!" << std::endl;
            return 0 ;
        }
        
    }
    else {  // dual quad mode
        // set mode : DSPI or QSPI
        status = FT4222_SPIMaster_SetLines(ftHandle,FT4222_SPIMode(spiMode));
        if (FT4222_OK == status){
        }
        else{
            std::cerr << "SPI setlines failed!" << std::endl;
            return 0;
        }

        if (singleBytes == -1) { // send all as single bytes
            singleBytes = sendLen;
        }
        sendLen -= singleBytes;

        uint8_t* rbuf;
        int recvLen = 0;
        uint32_t sizeTransferred=0;
        if (cs_id == 2){ //spi target cs control 
			digitalWrite(cs_pin, LOW);
		}
        status = FT4222_SPIMaster_MultiReadWrite(ftHandle, rbuf, sbuf, singleBytes,sendLen, recvLen,
                                             &sizeTransferred);
        if (cs_id == 2){ //spi target cs control 
            delay(500);
			digitalWrite(cs_pin, HIGH);
		}   
        if (FT4222_OK == status){
        }
        else{
            std::cerr << "SPI multi read failed!" << std::endl;
            return 0;
        } 

    }
    
    return 1;

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