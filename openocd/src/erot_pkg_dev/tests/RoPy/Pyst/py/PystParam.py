import enum
import logging


@enum.unique
class PacketType(enum.IntEnum):
    '''
    Denote packet intent
    '''
    # req with same rsp
    # 0-999
    WRITE = 0

    # req with customized rsp
    # 1000-1999
    READ = 1000
    FUNC = 1001  # req = args, rsp = return

    # special req
    ABORT = 2000

@enum.unique
class ArgumentType(enum.IntEnum):
    CHAR = 0
    UCHAR = 1
    SHORT = 2
    USHORT = 3
    INT = 4
    UINT = 5
    LONG = 6
    ULONG = 7
    FLOAT = 8
    DOUBLE = 9
    STRING = 10


class Param:
    MAX_PACKET_TOTAL_BYTES_LIMIT = 8192
    N_ID_BYTES = 4
    N_TYPE_BYTES = 4
    N_PORT_BYTES = 4
    N_USER_BYTES = 4
    N_NBR_FIELD_BYTES = 1
    N_EACH_NBR_FIELD_BYTES = 2
    BYTE_ORDER = 'big'
    FIELD_BYTE_DEFAULT_VALUE = 255


def dim(a):
    if not a or not isinstance(a, list):
        return 0
    return 1 + dim(a[0])


def bytes_stringfy(byte_stream):
    return ' '.join(f"0x{b:02X}" for b in byte_stream)



__log = logging.getLogger("RockPy")
# __title = "[PystClient]"
__title = ""

def rpdebug(s):
    __log.debug(f"{__title}{s}")

def rpinfo(s):
    __log.info(f"{__title}{s}")

def rpwarning(s):
    __log.warning(f"{__title}{s}")

def rperror(s):
    __log.error(f"{__title}{s}")

def rpfatal(s):
    ks = f"{__title}{s}"
    __log.critical(ks)
    raise Exception(ks)

def inner_trace(s):
    __log.trace(f"{__title}{s}")
