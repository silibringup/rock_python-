#ifndef __PYST_SIM_LIB_HPP__
#define __PYST_SIM_LIB_HPP__

#include <cstdio>
#include <cstdlib>
#include <cmath>
#include <cstring>
#include <string>
#include <iterator>
#include <vector>
#include <regex>

#if defined(VCS)
#include "vpi_user.h"
#define pystprint(a, args...) vpi_printf((char*)"[PystC++] " a, ##args)
#else
#define pystprint(a, args...) printf((char*)"[PystC++] " a, ##args)
#endif
// #define pystdebug(a, args...) if(__PYST_DEBUG) pystprint("%s@%d: " a, __FILE__, __LINE__, ##args)
#define pystdebug(a, args...) if(__PYST_DEBUG) pystprint(a, ##args)
#define pysterror(a, args...) pystprint("ERROR: " a, ##args)


extern "C"{
  // ---------------------------------------
  // int8
  void bytestoint8(uint8_t** b, int8_t* v);
  void int8tobytes(uint8_t** b, int8_t* v);

  // ---------------------------------------
  // uint8
  void bytestouint8(uint8_t** b, uint8_t* v);
  void uint8tobytes(uint8_t** b, uint8_t* v);

  // ---------------------------------------
  // int16
  void bytestoint16(uint8_t** b, int16_t* v);
  void int16tobytes(uint8_t** b, int16_t* v);

  // ---------------------------------------
  // uint16
  void bytestouint16(uint8_t** b, uint16_t* v);
  void uint16tobytes(uint8_t** b, uint16_t* v);

  // ---------------------------------------
  // int32
  void bytestoint32(uint8_t** b, int32_t* v);
  void int32tobytes(uint8_t** b, int32_t* v);

  // ---------------------------------------
  // uint32
  void bytestouint32(uint8_t** b, uint32_t* v);
  void uint32tobytes(uint8_t** b, uint32_t* v);

  // ---------------------------------------
  // int64
  void bytestoint64(uint8_t** b, int64_t* v);
  void int64tobytes(uint8_t** b, int64_t* v);

  // ---------------------------------------
  // uint64
  void bytestouint64(uint8_t** b, uint64_t* v);
  void uint64tobytes(uint8_t** b, uint64_t* v);

  // ---------------------------------------
  // float : assume no diff vs. double
  void bytestofloat(uint8_t** b, double* v);
  void floattobytes(uint8_t** b, double* v);

  // ---------------------------------------
  // double
  void bytestodouble(uint8_t** b, double* v);
  void doubletobytes(uint8_t** b, double* v);

  // ---------------------------------------
  // string
  void stringtobytes(uint32_t* len, uint8_t** b, char** v);
  void bytestostring(uint32_t* len, uint8_t** b, char** v);

  double cpu_time(void);
}

#endif
