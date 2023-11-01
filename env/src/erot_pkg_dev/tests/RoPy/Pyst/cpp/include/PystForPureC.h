#ifndef __PYST_H__
#define __PYST_H__

typedef struct PystPacketStruct_t {
  unsigned int id;
  unsigned int ptype;
  unsigned int component;
  unsigned int routine;
  unsigned int n_fields;
  unsigned int* n_each_field_bytes;
  unsigned char* bytes;
  unsigned char** fields;
} PystPacketStruct;


#ifdef __cplusplus
extern "C"{
#endif

  PystPacketStruct* packet_new(void);
  void packet_resource_free(PystPacketStruct* p_pkt);
  void packet_free(PystPacketStruct* p_pkt);
  void bytes2pkt(unsigned int len, unsigned char* msg, PystPacketStruct* p_pkt);
  void pkt2bytes(PystPacketStruct* p_pkt, int* len, unsigned char* msg);
  void packet_copy(PystPacketStruct* p_src_pkt, PystPacketStruct* p_dst_pkt);
  void add_ret(PystPacketStruct* p_pkt, uint32_t* pkt_len, const uint8_t* ret, uint32_t ret_len);
  int i2ctransfer(uint32_t i2c_dev_id, uint32_t slv_addr, bool rw, uint32_t n_byte, uint8_t* data);
#ifdef __cplusplus
}
#endif



#endif
