#ifndef __LOCAL_UTIL_H__
#define __LOCAL_UTIL_H__

#include <stdint.h>
#include "ftd2xx.h"
#include "libft4222.h"


#ifdef __cplusplus
extern "C"{
#endif

int SMBus_init(uint32_t i2c_kbps, FT_HANDLE* ftHandle);
void SMBus_close(FT_HANDLE ftHandle);
int SMBus_write(FT_HANDLE ftHandle, uint16_t slaveAddr, uint8_t command, uint8_t count, uint8_t data[]);
int SMBus_read(FT_HANDLE ftHandle, uint16_t slaveAddr, uint8_t command, uint16_t desire_n_byte, uint8_t data[]);

#ifdef __cplusplus
}
#endif

#endif