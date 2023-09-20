import enum
from RoPy.Pyst import PystArgument, ArgumentType, PystPacket, PystFunctionPacket
from RoPy.Component.py.RPComponent import RPComponent

class RPCommon(RPComponent):
    _ID = 0
    class ROUTINE(enum.IntEnum):
        FINISH = 0
        HDL_RELEASE = 1
        HDL_DEPOSIT = 2
        HDL_FORCE = 3
        HDL_READ = 4
        WAIT_SIM_TIME = 5
        FOPEN = 6
        FCLOSE = 7
        GET_SIM_TIME = 8
        HDL_WAIT = 9
        BATCH_HDL_DEPOSIT = 10

    def __init__(self, link, *args, **kwargs):
        super(RPCommon, self).__init__(link, *args, **kwargs)

    def Finish(self):
        pass
        # pkt = PystPacket(pcomponent=EROTComponent.COMMON, proutine=EROTComponent.COMMON_FINISH)
        # self.link.transport(pkt)

    def ReleaseVerilogPath(self, hdl_path):
        if not isinstance(hdl_path, str):
            raise Exception(f"{hdl_path} must be string")

        args = [PystArgument(ArgumentType.STRING, [hdl_path])]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.HDL_RELEASE,
                                      function_name="ReleaseVerilogPath",
                                      args=args)
        self.link.transport(func_pkt)


    def DepositVerilogPath(self, hdl_path, value):
        if not isinstance(hdl_path, str):
            raise Exception(f"{hdl_path} must be string")
        if not isinstance(value, list):
            raise Exception(f"{value} must be 8-bit integer array")

        args = [PystArgument(ArgumentType.STRING, [hdl_path])]
        args += [PystArgument(ArgumentType.UCHAR, value)]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.HDL_DEPOSIT,
                                      function_name="DepositVerilogPath",
                                      args=args)
        self.link.transport(func_pkt)

    def ForceVerilogPath(self, hdl_path, value):
        if not isinstance(hdl_path, str):
            raise Exception(f"{hdl_path} must be string")
        if not isinstance(value, list):
            raise Exception(f"{value} must be 8-bit integer array")

        args = [PystArgument(ArgumentType.STRING, [hdl_path])]
        args += [PystArgument(ArgumentType.UCHAR, value)]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.HDL_FORCE,
                                      function_name="ForceVerilogPath",
                                      args=args)
        self.link.transport(func_pkt)

    def ReadVerilogPath(self, hdl_path):
        if not isinstance(hdl_path, str):
            raise Exception(f"{hdl_path} must be string")

        args = [PystArgument(ArgumentType.STRING, [hdl_path])]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.HDL_READ,
                                      function_name="ReadVerilogPath",
                                      args=args)
        x = self.link.transport(func_pkt)
        x = PystFunctionPacket(byte_stream=x.bytes)
        ans = x.ret.get_value(0)
        if x.ret.get_type() == ArgumentType.STRING:
            ans = ans[-32:]
        return ans

    def WaitSimTime(self, unit, value):
        if unit == "s":
            us_scale = 1e6
        elif unit == "ms":
            us_scale = 1e3
        elif unit == "us":
            us_scale = 1
        elif unit == "ns":
            us_scale = 1e-3
        elif unit == "ps":
            us_scale = 1e-6
        elif unit == "fs":
            us_scale = 1e-9
        else:
            RoPy.rpfatal(f"Unrecognized time unit {unit}")
        
        value *= us_scale
        go_wait_us = []
        if value <= 100:
            go_wait_us = [value]
        else:
            n = int(value // 100)
            r = value - 100*n
            if r != 0:
                go_wait_us = [100] * n + [r]
            else:
                go_wait_us = [100] * n

        for i in go_wait_us:
            args = [PystArgument(ArgumentType.STRING, ["us"])]
            args += [PystArgument(ArgumentType.DOUBLE, [i])]
            func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                        proutine=RPCommon.ROUTINE.WAIT_SIM_TIME,
                                        function_name="WaitSimTime",
                                        args=args)
            self.link.transport(func_pkt)

    def WaitReset(self, reset):
        x = self.ReadVerilogPath(reset)
        while x != 1:
            self.WaitSimTime("ns", 100)
            x = self.ReadVerilogPath(reset)

    def DepositVerilogPath32(self, hdl_path, value):
        if not isinstance(value, int):
            raise Exception(f"{value} is not int")
        v = list(value.to_bytes(4, 'little'))
        self.DepositVerilogPath(hdl_path, v)

    def ForceVerilogPath32(self, hdl_path, value):
        if not isinstance(value, int):
            raise Exception(f"{value} is not int")
        v = list(value.to_bytes(4, 'little'))
        self.ForceVerilogPath(hdl_path, v)

    def GetSimTime(self):
        pkt = PystPacket(pcomponent=RPCommon._ID,
                         proutine=RPCommon.ROUTINE.GET_SIM_TIME)
        x = self.link.transport(pkt)
        x = PystFunctionPacket(byte_stream=x.bytes)
        ans = x.ret.get_value(0)
        return ans


    def WaitVerilogPath(self, hdl_path, value):
        if not isinstance(hdl_path, str):
            raise Exception(f"{hdl_path} must be string")
        if not isinstance(value, list):
            raise Exception(f"{value} must be 8-bit integer array")

        args = [PystArgument(ArgumentType.STRING, [hdl_path])]
        args += [PystArgument(ArgumentType.UCHAR, value)]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.HDL_WAIT,
                                      function_name="WaitVerilogPath",
                                      args=args)
        self.link.transport(func_pkt)

    def WaitVerilogPath32(self, hdl_path, value):
        if not isinstance(value, int):
            raise Exception(f"{value} is not int")
        v = list(value.to_bytes(4, 'little'))
        self.WaitVerilogPath(hdl_path, v)

    def BatchDepositVerilogPath(self, filepath):
        if not isinstance(filepath, str):
            raise Exception(f"{filepath} must be string")

        args = [PystArgument(ArgumentType.STRING, [filepath])]
        func_pkt = PystFunctionPacket(pcomponent=RPCommon._ID,
                                      proutine=RPCommon.ROUTINE.BATCH_HDL_DEPOSIT,
                                      function_name="BatchDepositVerilogPath",
                                      args=args)
        self.link.transport(func_pkt)
