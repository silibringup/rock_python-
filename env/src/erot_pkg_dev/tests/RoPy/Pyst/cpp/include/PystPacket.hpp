#ifndef __PYST_PACKET_HPP__
#define __PYST_PACKET_HPP__

#include <stdint.h>
#include <vector>
#include <iostream>
#include <iomanip>

typedef enum packet_type_t {
  // req with same rsp
  // 0-999
  WRITE = 0,

  // req with customized rsp
  // 1000-1999
  READ = 1000,
  FUNC = 1001, // req = args, rsp = return

  // special req
  ABORT	= 2000
} packet_type_t;



class PystPacket{
public:
  uint32_t id;
  packet_type_t ptype;
  uint32_t component;
  uint32_t routine;
  uint32_t n_fields;
  std::vector<uint32_t> n_each_field_bytes;
  std::vector<uint8_t> bytes;
  std::vector< std::vector<uint8_t> > fields;

  /*
    partitioin new byte vector out of the given byte vector v from position X to Y
  */
  template <typename T>
  std::vector<T> slicing(std::vector<T> const& v, int X, int Y){
    auto first = v.begin() + X;
    auto last = v.begin() + Y + 1;
    std::vector<T> vec(first, last);
    return vec;
  }

  /*
    concatanate bytes vector v to int from position X to Y
  */
  template <typename T>
  uint32_t concat_bytes(std::vector<T> const& v, int X, int Y){
    std::vector<T> vec = slicing<uint8_t>(v, X, Y);
    uint32_t ans = 0;
    int vec_size = vec.size();
    for(int i=0;i<vec_size;i++){
      ans |= (vec[i] << ((vec_size-1-i)*8));
    }
    return ans;
  }

  void parse_from_byte_stream(uint8_t* _data, int len){
    std::vector<uint8_t> data(_data, _data + len);

    int idx = 0;
    id = concat_bytes<uint8_t>(data, idx, idx+N_ID_BYTES-1);
    idx += N_ID_BYTES;
    ptype = static_cast<packet_type_t>(concat_bytes<uint8_t>(data, idx, idx+N_TYPE_BYTES-1));
    idx += N_TYPE_BYTES;
    component = concat_bytes<uint8_t>(data, idx, idx+N_PORT_BYTES-1);
    idx += N_PORT_BYTES;
    routine = concat_bytes<uint8_t>(data, idx, idx+N_USER_BYTES-1);
    idx += N_USER_BYTES;
    n_fields = concat_bytes<uint8_t>(data, idx, idx+N_NBR_FIELD_BYTES-1);
    idx += N_NBR_FIELD_BYTES;

    for(int i=0; i<(int)n_fields; i++, idx+=N_EACH_NBR_FIELD_BYTES){
      uint32_t t = concat_bytes<uint8_t>(data, idx, idx+N_EACH_NBR_FIELD_BYTES-1);
      n_each_field_bytes.push_back(t);
    }

    for(auto& n_fld_bytes : n_each_field_bytes){
      std::vector<uint8_t> fq = slicing<uint8_t>(data, idx, idx+n_fld_bytes-1);
      idx += n_fld_bytes;
      fields.push_back(fq);
    }

    for(int i=0;i<idx;i++){
      bytes.push_back(data[i]);
    }
    
  }

  int get_bytes_length(){
    return bytes.size();
  }

  uint32_t bytes_to_uint(std::vector<uint8_t>& b){
    uint32_t ans = 0;
    for(auto i = b.rbegin(); i<b.rend(); i++) {
        ans = ans << 8;
        ans += *i;
    }
    return ans;
  }

  std::vector<uint8_t> uint_to_bytes(uint32_t v){
    std::vector<uint8_t> arr(4);
    for (int i = 0; i < 4; i++){
      arr[3 - i] = (v >> (i * 8));
    }
    return arr;
  }

  void update_from_fields(){
    uint32_t n_tot_bytes = 0;
    uint32_t idx = 0;
    n_fields = fields.size();
    n_each_field_bytes.clear();
    for(auto& fld : fields){
      n_each_field_bytes.push_back(fld.size());
      n_tot_bytes += fld.size();
    }

    n_tot_bytes += (N_ID_BYTES +
                    N_TYPE_BYTES +
                    N_PORT_BYTES +
                    N_USER_BYTES +
                    N_NBR_FIELD_BYTES +
                    n_fields * N_EACH_NBR_FIELD_BYTES);
    bytes.resize(n_tot_bytes);
    for(int i=0; i<N_ID_BYTES; i++){
      bytes[i] = (id >> (N_ID_BYTES-1-i)*8);
    }
    for(int i=ID_BYTE_POS+1, j=0; j<N_TYPE_BYTES; i++, j++){
      bytes[i] = (ptype >> (N_TYPE_BYTES-1-j)*8);
    }
    for(int i=TYPE_BYTE_POS+1, j=0; j<N_PORT_BYTES; i++, j++){
      bytes[i] = (component >> (N_PORT_BYTES-1-j)*8);
    }
    for(int i=PORT_BYTE_POS+1, j=0; j<N_USER_BYTES; i++, j++){
      bytes[i] = (routine >> (N_USER_BYTES-1-j)*8);
    }
    bytes[N_NBR_FIELD_BYTE_POS] = (uint8_t)n_fields;

    for(int i=N_NBR_FIELD_BYTE_POS+1, j=0;
        i<(int)(N_NBR_FIELD_BYTE_POS+1+n_fields*N_EACH_NBR_FIELD_BYTES);
        i+=N_EACH_NBR_FIELD_BYTES, j++){
      std::vector<uint8_t> t = uint_to_bytes(n_each_field_bytes[j]);
      for(int k=0;k<N_EACH_NBR_FIELD_BYTES;k++){
        bytes[i+k] = t[t.size() - N_EACH_NBR_FIELD_BYTES + k];
      }
    }

    idx = N_NBR_FIELD_BYTE_POS+1+n_fields*N_EACH_NBR_FIELD_BYTES;
    for(auto& fld : fields){
      for(auto& b : fld){
        bytes[idx] = b;
        idx++;
      }
    }
  }

  void print(){
    std::cout << "id:" << id << std::endl;
    std::cout << "type:" << ptype << std::endl;
    std::cout << "component:" << component << std::endl;
    std::cout << "routine:" << routine << std::endl;
    std::cout << "n_fields:" << n_fields << std::endl;
    for(int i=0; i<(int)n_each_field_bytes.size(); i++){
      std::cout << "field " << i << ": "<< n_each_field_bytes[i] << " bytes" << std::endl;
      std::cout << "  value: ";
      for(int j=0; j<(int)n_each_field_bytes[i]; j++){
        std::cout << "0x" << std::hex << std::setfill('0') << std::setw(2) << static_cast<unsigned>(fields[i][j]);
        std::cout << " ";
      }
      std::cout << std::endl;
    }
  }
};

#endif // __PYST_PACKET_CPP__
