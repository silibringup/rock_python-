#ifndef __PYST_MAIN_CPP__
#define __PYST_MAIN_CPP__

#include <utility>
#include <cstdlib>
#include <vector>
#include <exception>
#include <iostream>
#include "PystServer.hpp"
#include "PystMain.hpp"
#include "PystSimLib.hpp"


extern int __PYST_DEBUG;

#ifdef __cplusplus
extern "C"{
#endif

// ----------------------------------- pyst_service_start -----------------------------------
#if defined(VCS)
  void pyst_service_start(uint32_t len, svOpenArrayHandle ports, int is_c_call){
    uint32_t* p = nullptr;
    if(is_c_call){
      p = (uint32_t*)ports;
    } else {
      p = (uint32_t*)svGetArrayPtr(ports);
    }
#else
  void pyst_service_start(uint32_t len, uint32_t* ports, int is_c_call){
    uint32_t* p = (uint32_t*)ports;
#endif // defined

    const char* pyst_debug_enable_str = std::getenv("PYST_DEBUG");
    if (pyst_debug_enable_str) {
        __PYST_DEBUG = std::stoi(std::string(pyst_debug_enable_str));
    }

    std::vector<uint32_t> port_vec;
    for(int i=0;i<(int)len;i++){
      try{
        pystdebug("Building Pyst server %d ...\n", i);
        build_server(p[i]); // one port one server
        pystdebug("Pyst server successfully starts on port %d\n", p[i]);
      } catch(std::exception& e){
        std::cout << "Exception: " << e.what() << std::endl;
      }
    }
    
    pystdebug("Quit pyst_service_start\n");
  }


// ----------------------------------- pyst_service_stop -----------------------------------
  void pyst_service_stop(){
    if(server_is_alive()){
      try{
        stop_server();
      } catch(std::exception& e){
        std::cout << "Exception: " << e.what() << std::endl;
      }
    }
  }


// ----------------------------------- pyst_service_stop -----------------------------------
  int pyst_service_alive(){
    return server_is_alive();
  }

// ----------------------------------- pyst_has_message -----------------------------------
  int pyst_has_message(){
    bool ans = false;
    try{
      ans = !server_is_empty();
    } catch(std::exception& e){
      std::cout << "Exception: " << e.what() << std::endl;
    }
    return ans;
  }


// ----------------------------------- pyst_receive_message -----------------------------------
#if defined(VCS)
  int pyst_receive_message(int sv_len, svOpenArrayHandle data, int is_c_call){
    uint8_t* p = nullptr;
    if(is_c_call){
      p = (uint8_t*)data;
    } else {
      p = (uint8_t*)svGetArrayPtr(data);
    }
#else
  int pyst_receive_message(int sv_len, uint8_t* data, int is_c_call){
    uint8_t* p = (uint8_t*)data;
#endif // defined

    int c_len = 0;
    try{
      c_len = get_next_message(p);
    } catch(std::exception& e){
      std::cout << "Exception: " << e.what() << std::endl;
    }

    if(sv_len < c_len){
      pysterror("SV byte size(%d) should be >= C byte size(%d)\n", sv_len, c_len);
      std::abort();
    }

    return c_len;
  }


// ----------------------------------- pyst_send_message -----------------------------------
#if defined(VCS)
  void pyst_send_message(int len, svOpenArrayHandle data, int is_c_call){
    uint8_t* p = nullptr;
    if(is_c_call){
      p = (uint8_t*)data;
    } else {
      p = (uint8_t*)svGetArrayPtr(data);
    }
#else
  void pyst_send_message(int len, uint8_t* data, int is_c_call){
    uint8_t* p = (uint8_t*)data;
#endif // defined

    uint8_t* p_sv_msg = new uint8_t[len];
    for(int i=0;i<len;i++){
      p_sv_msg[i] = p[i];
    }

    try{
      put_next_message(len, p_sv_msg);
    } catch(std::exception& e){
      std::cout << "Exception: " << e.what() << std::endl;
    }
    delete [] p_sv_msg;
  }



#ifdef __cplusplus
}
#endif


#endif
