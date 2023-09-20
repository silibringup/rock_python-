#include "PystSimLib.hpp"
#include <sys/time.h>

int __PYST_DEBUG = 0;

extern "C" {
  // ---------------------------------------
  // int8
  void bytestoint8(uint8_t** b, int8_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void int8tobytes(uint8_t** b, int8_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // uint8
  void bytestouint8(uint8_t** b, uint8_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void uint8tobytes(uint8_t** b, uint8_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // int16
  void bytestoint16(uint8_t** b, int16_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void int16tobytes(uint8_t** b, int16_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // uint16
  void bytestouint16(uint8_t** b, uint16_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void uint16tobytes(uint8_t** b, uint16_t* v){
    memcpy(*b, v, sizeof(*v));
  }
  
  // ---------------------------------------
  // int32
  void bytestoint32(uint8_t** b, int32_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void int32tobytes(uint8_t** b, int32_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // uint32
  void bytestouint32(uint8_t** b, uint32_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void uint32tobytes(uint8_t** b, uint32_t* v){
    memcpy(*b, v, sizeof(*v));
  }
  
  // ---------------------------------------
  // int64
  void bytestoint64(uint8_t** b, int64_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void int64tobytes(uint8_t** b, int64_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // uint64
  void bytestouint64(uint8_t** b, uint64_t* v){
    memcpy(v, *b, sizeof(*v));
  }

  void uint64tobytes(uint8_t** b, uint64_t* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // float : assume no diff vs. double
  void bytestofloat(uint8_t** b, double* v){
    memcpy(v, *b, sizeof(*v));
  }

  void floattobytes(uint8_t** b, double* v){
    memcpy(*b, v, sizeof(*v));
  }
  
  // ---------------------------------------
  // double
  void bytestodouble(uint8_t** b, double* v){
    memcpy(v, *b, sizeof(*v));
  }

  void doubletobytes(uint8_t** b, double* v){
    memcpy(*b, v, sizeof(*v));
  }

  // ---------------------------------------
  // string
  void stringtobytes(uint32_t* len, uint8_t** b, char** v){
    for(int i=0;i<(int)(*len);i++){
      (*b)[i] = (*v)[i];
    }
  }

  void bytestostring(uint32_t* len, uint8_t** b, char** v){
    for(int i=0;i<(int)(*len);i++){
      (*v)[i] = (*b)[i];
    }
  }

  double cpu_time(void){
      struct timeval current;
      gettimeofday(&current,NULL);
      return current.tv_sec + current.tv_usec / 1000000.0;
  }
}
