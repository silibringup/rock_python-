`ifndef __PYST_PARAM__
`define __PYST_PARAM__


localparam int unsigned MAX_PACKET_TOTAL_BYTES_LIMIT = 8192;
localparam int unsigned N_ID_BYTES = 4;
localparam int unsigned N_TYPE_BYTES = 4;
localparam int unsigned N_PORT_BYTES = 4;
localparam int unsigned N_USER_BYTES = 4;
localparam int unsigned N_NBR_FIELD_BYTES = 1;
localparam int unsigned N_EACH_NBR_FIELD_BYTES = 2;
localparam int unsigned FIELD_BYTE_DEFAULT_VALUE = 255;

localparam int unsigned ID_BYTE_POS   = N_ID_BYTES - 1;
localparam int unsigned TYPE_BYTE_POS = ID_BYTE_POS + N_TYPE_BYTES;
localparam int unsigned PORT_BYTE_POS = TYPE_BYTE_POS + N_PORT_BYTES;
localparam int unsigned USER_BYTE_POS = PORT_BYTE_POS + N_USER_BYTES;
localparam int unsigned N_NBR_FIELD_BYTE_POS = USER_BYTE_POS + N_NBR_FIELD_BYTES;

typedef enum {
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

typedef enum {
  CHAR = 0,
  UCHAR = 1,
  SHORT = 2,
  USHORT = 3,
  INT = 4,
  UINT = 5,
  LONG = 6,
  ULONG = 7,
  FLOAT = 8,
  DOUBLE = 9,
  STRING = 10
} argument_type_t;

typedef byte              int8_t;
typedef byte unsigned     uint8_t;
typedef shortint          int16_t;
typedef shortint unsigned uint16_t;
typedef int               int32_t;
typedef int unsigned      uint32_t;
typedef longint           int64_t;
typedef longint unsigned  uint64_t;
typedef uint8_t uint8_q[$];
typedef uint8_t uint8_da[];

function automatic string arg_enum2typename(argument_type_t argT);
  case(argT) inside
    CHAR: return $typename(int8_t);
    UCHAR: return $typename(uint8_t);
    SHORT: return $typename(int16_t);
    USHORT: return $typename(uint16_t);
    INT: return $typename(int32_t);
    UINT: return $typename(uint32_t);
    LONG: return $typename(int64_t);
    ULONG: return $typename(uint64_t);
    FLOAT, DOUBLE: return $typename(real);
    STRING: return $typename(string);
  endcase
endfunction : arg_enum2typename

function automatic argument_type_t typename2arg_enum(string Tname);
  case(Tname) inside
    $typename(int8_t): return CHAR;
    $typename(uint8_t): return UCHAR;
    $typename(int16_t): return SHORT;
    $typename(uint16_t): return USHORT;
    $typename(int32_t): return INT;
    $typename(uint32_t): return UINT;
    $typename(int64_t): return LONG;
    $typename(uint64_t): return ULONG;
    $typename(real): return DOUBLE;
    $typename(string): return STRING;
    default: $fatal("Wrong type name");
  endcase
endfunction : typename2arg_enum

`endif
