`ifndef __PYST_ARGUMENT__
`define __PYST_ARGUMENT__

// -------------------------------------------------------------------------------------------
// bytes to X
// -------------------------------------------------------------------------------------------
import "DPI-C" context function void bytestoint8(  inout byte unsigned b[], inout int8_t   v);
function automatic int8_t bytes_to_int8(uint8_da b);
  int8_t v;
  bytestoint8(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestouint8( inout byte unsigned b[], inout uint8_t  v);
function automatic uint8_t bytes_to_uint8(uint8_da b);
  uint8_t v;
  bytestouint8(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestoint16( inout byte unsigned b[], inout int16_t  v);
function automatic int16_t bytes_to_int16(uint8_da b);
  int16_t v;
  bytestoint16(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestouint16(inout byte unsigned b[], inout uint16_t v);
function automatic uint16_t bytes_to_uint16(uint8_da b);
  uint16_t v;
  bytestouint16(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestoint32( inout byte unsigned b[], inout int32_t  v);
function automatic int32_t bytes_to_int32(uint8_da b);
  int32_t v;
  bytestoint32(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestouint32(inout byte unsigned b[], inout uint32_t v);
function automatic uint32_t bytes_to_uint32(uint8_da b);
  uint32_t v;
  bytestouint32(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestoint64( inout byte unsigned b[], inout int64_t  v);
function automatic int64_t bytes_to_int64(uint8_da b);
  int64_t v;
  bytestoint64(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestouint64(inout byte unsigned b[], inout uint64_t v);
function automatic uint64_t bytes_to_uint64(uint8_da b);
  uint64_t v;
  bytestouint64(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestofloat( inout byte unsigned b[], inout real     v);
function automatic real bytes_to_float(uint8_da b);
  real v;
  bytestofloat(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestodouble(inout byte unsigned b[], inout real     v);
function automatic real bytes_to_double(uint8_da b);
  real v;
  bytestodouble(b, v);
  return v;
endfunction

import "DPI-C" context function void bytestostring(inout int unsigned len, inout byte unsigned b[], inout string   v);
function automatic string bytes_to_string(uint8_da b);
  uint32_t len = b.size();
  string v = {len{"*"}};
  bytestostring(len, b, v);
  return v;
endfunction


// -------------------------------------------------------------------------------------------
// X to bytes
// -------------------------------------------------------------------------------------------
import "DPI-C" context function void int8tobytes(  inout byte unsigned b[], inout int8_t   v);
function automatic uint8_da int8_to_bytes(int8_t v);
  uint8_t b[1];
  int8tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void uint8tobytes( inout byte unsigned b[], inout uint8_t  v);
function automatic uint8_da uint8_to_bytes(uint8_t v);
  uint8_t b[1];
  uint8tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void int16tobytes( inout byte unsigned b[], inout int16_t  v);
function automatic uint8_da int16_to_bytes(int16_t v);
  uint8_t b[2];
  int16tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void uint16tobytes(inout byte unsigned b[], inout uint16_t v);
function automatic uint8_da uint16_to_bytes(uint16_t v);
  uint8_t b[2];
  uint16tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void int32tobytes( inout byte unsigned b[], inout int32_t  v);
function automatic uint8_da int32_to_bytes(int32_t v);
  uint8_t b[4];
  int32tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void uint32tobytes(inout byte unsigned b[], inout uint32_t v);
function automatic uint8_da uint32_to_bytes(uint32_t v);
  uint8_t b[4];
  uint32tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void int64tobytes( inout byte unsigned b[], inout int64_t  v);
function automatic uint8_da int64_to_bytes(int64_t v);
  uint8_t b[8];
  int64tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void uint64tobytes(inout byte unsigned b[], inout uint64_t v);
function automatic uint8_da uint64_to_bytes(uint64_t v);
  uint8_t b[8];
  uint64tobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void floattobytes( inout byte unsigned b[], inout real     v);
function automatic uint8_da float_to_bytes(real v);
  uint8_t b[8];
  floattobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void doubletobytes(inout byte unsigned b[], inout real     v);
function automatic uint8_da double_to_bytes(real v);
  uint8_t b[8];
  doubletobytes(b, v);
  return b;
endfunction

import "DPI-C" context function void stringtobytes(inout int unsigned len, inout byte unsigned b[], inout string   v);
function automatic uint8_da string_to_bytes(string v);
  uint32_t len = v.len();
  uint8_t b[] = new[len];
  stringtobytes(len, b, v);
  return b;
endfunction





typedef class pyst_packet;

class pyst_argument extends uvm_object;
  protected uint32_t n_arg;
  protected uint32_t n_arg_bytes[$];
  protected uint8_da arg_bytes[$];

  `uvm_object_utils(pyst_argument)

  function new(string name="pyst_argument");
    super.new(name);
  endfunction : new

  // separate individual argument from a packed arg payload field
  virtual function void load_arg_bytes(uint8_q b);
    uint32_t idx = 0;
    argument_type_t arg_enum = argument_type_t'(b[idx]);
    idx++;
    this.n_arg = uint32_t'({b[idx]});
    idx++;

    for(int i=0; i<this.n_arg; i++) begin
      this.n_arg_bytes.push_back( uint32_t'({b[idx], b[idx+1]}) );
      idx += 2;
    end

    foreach(this.n_arg_bytes[i]) begin
      uint8_t x[] = new[n_arg_bytes[i]];
      foreach(x[i]) begin
        x[i] = b[idx];
        idx++;
      end
      this.arg_bytes.push_back(x);
    end
  endfunction : load_arg_bytes

  // convert this argument object to bytes, value has to be provided first
  virtual function uint8_q to_bytes();
    `uvm_fatal(this.get_name(), "Must implement in subclass")
  endfunction : to_bytes

  virtual function uint32_t value_type_byte_nbr(uint32_t idx);
    `uvm_fatal(this.get_name(), "Must implement in subclass")
  endfunction : value_type_byte_nbr

  // tend to create arg value array in subclass
  virtual function void create_from_bytes(uint8_q b);
    `uvm_fatal(this.get_name(), "Must implement in subclass")
  endfunction : create_from_bytes

endclass : pyst_argument


// title begin
`define pyst_arg_class_begin(T) \
class pyst_argument_``T`` extends pyst_argument; \
  `uvm_object_utils(pyst_argument_``T``) \
  function new(string name={"pyst_argument_", `"T`"}); \
    super.new(name); \
  endfunction : new

// title end
`define pyst_arg_class_end \
endclass


// member function
`define to_bytes_implement(T) \
  virtual function uint8_q to_bytes(); \
    this.n_arg = this.value.size(); \
    foreach(this.value[i]) begin \
      uint8_da b = ``T``_to_bytes(this.value[i]); \
      this.arg_bytes.push_back(b); \
    end \
    begin \
      uint8_q bq; \
      argument_type_t arg_enum = typename2arg_enum($typename(this.value[0])); \
      bq.push_back(uint8_t'(arg_enum)); \
      bq.push_back(this.n_arg); \
      foreach(this.value[i]) begin \
        bit[31:0] n_arg_byte = this.value_type_byte_nbr(i); \
        this.n_arg_bytes.push_back(n_arg_byte); \
        for(int i=N_EACH_NBR_FIELD_BYTES;i>0;i--) begin \
          bq.push_back(n_arg_byte[i*8-1 -: 8]); \
        end \
      end \
      foreach(this.arg_bytes[i]) begin \
        bq = {bq, this.arg_bytes[i]}; \
      end \
      return bq; \
    end \
  endfunction : to_bytes


`define value_type_byte_nbr_implement \
  virtual function uint32_t value_type_byte_nbr(uint32_t idx); \
    case($typename(this.value[idx])) inside \
      $typename(int8_t): return 1; \
      $typename(uint8_t): return 1; \
      $typename(int16_t): return 2; \
      $typename(uint16_t): return 2; \
      $typename(int32_t): return 4; \
      $typename(uint32_t): return 4; \
      $typename(int64_t): return 8; \
      $typename(uint64_t): return 8; \
      $typename(real): return 8; \
      default: `uvm_fatal(this.get_name(), "Wrong type") \
    endcase \
  endfunction : value_type_byte_nbr


// title
`define pyst_arg_class(T) \
`pyst_arg_class_begin(``T``_t) \
  ``T``_t value[$]; \
  function void create_from_bytes(uint8_q b); \
    this.load_arg_bytes(b); \
    foreach(this.arg_bytes[i]) begin \
      ``T``_t v = bytes_to_``T``(this.arg_bytes[i]); \
      this.value.push_back(v); \
    end \
  endfunction : create_from_bytes \
`value_type_byte_nbr_implement \
`to_bytes_implement(``T``) \
`pyst_arg_class_end



`pyst_arg_class(int8)
`pyst_arg_class(uint8)
`pyst_arg_class(int16)
`pyst_arg_class(uint16)
`pyst_arg_class(int32)
`pyst_arg_class(uint32)
`pyst_arg_class(int64)
`pyst_arg_class(uint64)

// ----------------------------------------
// float
// ----------------------------------------
`pyst_arg_class_begin(float)
  real value[$];
  function void create_from_bytes(uint8_q b);
    this.load_arg_bytes(b);
    foreach(this.arg_bytes[i]) begin
      real v = bytes_to_float(this.arg_bytes[i]);
      this.value.push_back(v);
    end
  endfunction : create_from_bytes
`value_type_byte_nbr_implement
`to_bytes_implement(float)
`pyst_arg_class_end

// ----------------------------------------
// double
// ----------------------------------------
`pyst_arg_class_begin(double)
  real value[$];
  function void create_from_bytes(uint8_q b);
    this.load_arg_bytes(b);
    foreach(this.arg_bytes[i]) begin
      real v = bytes_to_double(this.arg_bytes[i]);
      this.value.push_back(v);
    end
  endfunction : create_from_bytes
`value_type_byte_nbr_implement
`to_bytes_implement(double)
`pyst_arg_class_end

// ----------------------------------------
// float
// ----------------------------------------
`pyst_arg_class_begin(string)
  string value[$];
  function void create_from_bytes(uint8_q b);
    this.load_arg_bytes(b);
    foreach(this.arg_bytes[i]) begin
      string v = bytes_to_string(this.arg_bytes[i]);
      this.value.push_back(v);
    end
  endfunction : create_from_bytes
  virtual function uint32_t value_type_byte_nbr(uint32_t idx);
    return this.value[idx].len();
  endfunction : value_type_byte_nbr
`to_bytes_implement(string)
`pyst_arg_class_end




class pyst_argument_parser extends uvm_object;
  pyst_argument args[$];

  `uvm_object_utils(pyst_argument_parser)

`define parse_arg(T, field) \
  pyst_argument_``T`` a = pyst_argument_``T``::type_id::create(`"T`"); \
  a.create_from_bytes(field); \
  this.args.push_back(a);

  function new(string name="pyst_argument_parser");
    super.new(name);
  endfunction : new

  virtual function string parse(pyst_packet pkt);
    // function name
    string function_name = this.parse_function_name(pkt.fields[0]);
    // arguments
    for(int i=1;i<pkt.fields.size();i++) begin
      argument_type_t arg_enum = argument_type_t'(pkt.fields[i][0]);
      case(arg_enum) inside
        CHAR:   begin
          `parse_arg(int8_t, pkt.fields[i])
        end
        UCHAR:  begin
          `parse_arg(uint8_t, pkt.fields[i])
        end
        SHORT:  begin
          `parse_arg(int16_t, pkt.fields[i])
        end
        USHORT: begin
          `parse_arg(uint16_t, pkt.fields[i])
        end
        INT:    begin
          `parse_arg(int32_t, pkt.fields[i])
        end
        UINT:   begin
          `parse_arg(uint32_t, pkt.fields[i])
        end
        LONG:   begin
          `parse_arg(int64_t, pkt.fields[i])
        end
        ULONG:  begin
          `parse_arg(uint64_t, pkt.fields[i])
        end
        FLOAT:  begin
          `parse_arg(float, pkt.fields[i])
        end
        DOUBLE: begin
          `parse_arg(double, pkt.fields[i])
        end
        STRING: begin
          `parse_arg(string, pkt.fields[i])
        end
      endcase // case (arg_enum)
    end

    return function_name;
  endfunction : parse


  virtual function string parse_function_name(uint8_q bq);
    pyst_argument_string a;
    if(argument_type_t'(bq[0]) != STRING) begin
      `uvm_fatal(this.get_name(), "Function name must be string type")
    end
    a = pyst_argument_string::type_id::create("string");
    a.create_from_bytes(bq);
    return a.value[0];
  endfunction : parse_function_name

endclass : pyst_argument_parser


`endif

