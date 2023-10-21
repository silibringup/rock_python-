#ifndef __PYST_C__
#define __PYST_C__

#include <stdint.h>
#include <vector>
#include <sstream>
#include <iomanip>
#include <regex>
#include "PystParam.hpp"
#include "PystPacket.hpp"
#include "PystMain.hpp"
#include "PystForPureC.h"


#ifdef __cplusplus
extern "C" {
#endif

  PystPacketStruct* packet_new(void){
    PystPacketStruct* p_pkt = new PystPacketStruct;
    p_pkt->id = 0;
    p_pkt->ptype = 0;
    p_pkt->component = 0;
    p_pkt->routine = 0;
    p_pkt->n_fields = 0;
    p_pkt->n_each_field_bytes = NULL;
    p_pkt->bytes = NULL;
    p_pkt->fields = NULL;
    return p_pkt;
  }

  void packet_resource_free(PystPacketStruct* p_pkt){
    if(p_pkt->n_each_field_bytes != NULL){
      delete [] p_pkt->n_each_field_bytes;
    }
    if(p_pkt->bytes != NULL){
      delete [] p_pkt->bytes;
    }
    if(p_pkt->fields != NULL){
      delete [] p_pkt->fields;
    }
  }

  void packet_free(PystPacketStruct* p_pkt){
    packet_resource_free(p_pkt);
    if(p_pkt != NULL){
      delete p_pkt;
    }
  }

  // in: len, msg
  // out: p_pkt
  void bytes2pkt(unsigned int len, unsigned char* msg, PystPacketStruct* p_pkt){
    PystPacket pkt;
    pkt.parse_from_byte_stream(msg, len);
    p_pkt->id = pkt.id;
    p_pkt->ptype = pkt.ptype;
    p_pkt->component = pkt.component;
    p_pkt->routine = pkt.routine;
    p_pkt->n_fields = pkt.n_fields;

    packet_resource_free(p_pkt);

    p_pkt->n_each_field_bytes = new unsigned int[pkt.n_each_field_bytes.size()];
    for(int i=0; i<(int)pkt.n_each_field_bytes.size(); i++){
      p_pkt->n_each_field_bytes[i] = pkt.n_each_field_bytes[i];
    }

    p_pkt->bytes = new unsigned char[pkt.bytes.size()];
    for(int i=0; i<(int)pkt.bytes.size(); i++){
      p_pkt->bytes[i] = pkt.bytes[i];
    }

    p_pkt->fields = new unsigned char*[pkt.fields.size()];
    for(int i=0; i<(int)pkt.fields.size(); i++){
      p_pkt->fields[i] = new unsigned char[pkt.fields[i].size()];
      for(int j=0; j<(int)pkt.fields[i].size(); j++){
        p_pkt->fields[i][j] = pkt.fields[i][j];
      }
    }
  }

  // in: p_pkt
  // out: len, msg
  void pkt2bytes(PystPacketStruct* p_pkt, int* len, unsigned char* msg){
    PystPacket pkt;
    pkt.id = p_pkt->id;
    pkt.ptype = static_cast<packet_type_t>(p_pkt->ptype);
    pkt.component = p_pkt->component;
    pkt.routine = p_pkt->routine;
    pkt.n_fields = p_pkt->n_fields;

    for(int i=0; i<(int)p_pkt->n_fields; i++){
      std::vector<uint8_t> field(p_pkt->fields[i], p_pkt->fields[i] + p_pkt->n_each_field_bytes[i]);
      pkt.fields.push_back(field);
    }
    pkt.update_from_fields();

    *len = pkt.bytes.size();
    msg = new unsigned char[*len];
    for(int i=0;(int)i<(*len); i++){
      msg[i] = pkt.bytes[i];
    }
  }

  void packet_copy(PystPacketStruct* p_src_pkt, PystPacketStruct* p_dst_pkt){
    int len = 17 + p_src_pkt->n_fields*2;
    for(int i=0;i<(int)p_src_pkt->n_fields;i++){
      len += p_src_pkt->n_each_field_bytes[i];
    }
    bytes2pkt(len, p_src_pkt->bytes, p_dst_pkt);
  }

  void add_ret(PystPacketStruct* p_pkt, uint32_t* pkt_len, const uint8_t* ret, uint32_t ret_len){
    PystPacket pkt;
    pkt.id = p_pkt->id;
    pkt.ptype = static_cast<packet_type_t>(p_pkt->ptype);
    pkt.component = p_pkt->component;
    pkt.routine = p_pkt->routine;
    pkt.n_fields = p_pkt->n_fields;

    for (size_t i = 0; i < p_pkt->n_fields; i++){
      std::vector<uint8_t> field;
      for (size_t j = 0; j < p_pkt->n_each_field_bytes[i]; j++){
        field.push_back(p_pkt->fields[i][j]);
      }
      pkt.fields.push_back(field);
    }
    
    std::vector<uint8_t> field;
    for(uint32_t i=0;i<ret_len;i++){
      field.push_back(ret[i]);
    }
    pkt.fields.push_back(field);
    pkt.update_from_fields();
    *pkt_len = pkt.bytes.size();
    bytes2pkt(*pkt_len, &pkt.bytes[0], p_pkt);
  }

  std::vector<uint8_t> regex_i2ctransfer_result(std::string result){
      std::vector<uint8_t> ans;
      std::regex pat("(0x[a-f0-9]{2})");
      std::smatch res;
      while (regex_search(result, res, pat)) {
          ans.push_back(std::stoul(res[0], nullptr, 16));
          result = res.suffix();
      }
      return ans;
  }

  std::string i2ctransfer_command(uint32_t i2c_dev_id, uint32_t slv_addr, bool rw, uint32_t n_byte, uint8_t* data) {
    std::stringstream sstrm;
    sstrm << "i2ctransfer -y " << std::to_string(i2c_dev_id);

    if(rw){ // 1: read
      sstrm << " r";
    } else { // 0: write
      sstrm << " w";
    }

    sstrm << std::to_string(n_byte) << "@" << std::hex << std::setw(2) << std::setfill('0') << "0x" << slv_addr;
    
    if(!rw){ // attach data only in write
      for(uint32_t i=0; i<n_byte; i++){
          sstrm << " 0x" << std::setfill('0') << std::setw(2) << std::right << std::hex << (unsigned)data[i];
      }
    }
    
    return sstrm.str();
  }

  int i2ctransfer(uint32_t i2c_dev_id, uint32_t slv_addr, bool rw, uint32_t n_byte, uint8_t* data) {
    std::array<char, 4096> buffer{};
    std::string result;
    
    std::string t_cmd = i2ctransfer_command(i2c_dev_id, slv_addr, rw, n_byte, data);
    std::cout << "I2C command: " << t_cmd << std::endl;
    t_cmd += R"( | sed 's/\r/\n/g')";
    
    FILE *pipe = popen(t_cmd.c_str(), "r");
    
    if (pipe == nullptr) {
      throw std::runtime_error("popen() failed!");
      return 0;
    }
    try {
      size_t bytesread;
      while ((bytesread = fread(buffer.data(), sizeof(buffer.at(0)),
                                sizeof(buffer), pipe)) != 0) {
        result += std::string(buffer.data(), bytesread);
      }
    } catch (...) {
      pclose(pipe);
      throw;
      return 0;
    }
    pclose(pipe);

    if(result.empty()){
      result = "NULL";
    }
    std::cout << "Result:\n" << result << std::endl;

    // 0x12 0x06 0x08 0x10 0x21 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x18 0x00
    std::vector<uint8_t> ans = regex_i2ctransfer_result(result);
    if(rw){ // read
      if(ans.empty()){
        return 0; // read nothing. error.
      } else {
        for(uint32_t i=0; i<n_byte; i++){
          data[i] = ans[i];
        }
        return 1;
      }
    } else { // write
      return 1; // do nothing
    }
  }

#ifdef __cplusplus
}
#endif



#endif


