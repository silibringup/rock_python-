#ifndef __PYST_MAIN_HPP__
#define __PYST_MAIN_HPP__

#include <stdint.h>
#if defined(VCS)
#include "svdpi.h"
#endif // defined

#ifdef __cplusplus
extern "C"{
#endif

#if defined(VCS)
  void pyst_service_start(uint32_t len, svOpenArrayHandle ports, int is_c_call);
  int pyst_receive_message(int sv_len, svOpenArrayHandle data, int is_c_call);
  void pyst_send_message(int len, svOpenArrayHandle data, int is_c_call);
#else
  void pyst_service_start(uint32_t len, uint32_t* ports, int is_c_call);
  int pyst_receive_message(int sv_len, uint8_t* data, int is_c_call);
  void pyst_send_message(int len, uint8_t* data, int is_c_call);
#endif // defined
  void pyst_service_stop(void);
  int pyst_has_message(void);
  int pyst_service_alive(void);

#ifdef __cplusplus
}
#endif

#endif
