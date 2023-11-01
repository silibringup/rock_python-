from RoPy import rpinfo, rpdebug, rperror, rpfatal
from RoPy import PystPacket
from driver.components.EROTComponent import EROTComponent
from enum import IntEnum

class SPI_OPERATION_TYPE(IntEnum):
    SPI_RD          = 0
    SPI_WR          = 1
    SPI_FREQ_CFG    = 2

class SPI_SCLK_FREQ_SEL(IntEnum):
    SPI_SCLK_10MHZ  = 0
    SPI_SCLK_50MHZ  = 1
    SPI_SCLK_70MHZ  = 2
    SPI_SCLK_75MHZ  = 3
    SPI_SCLK_125MHZ = 4

class SPIMaster(EROTComponent):
    def write(self, rockpy_handle, spi_port, cs_id, 
            n_instruction_lane, n_instruction_bits, instruction, 
            n_address_lane, n_address_bits, address, 
            n_data_lane, data):
        if not isinstance(instruction, list):
            rpfatal(f"SPI instruction is not list")
        if len(instruction) > 4:
            rpfatal(f"SPI instruction byte size must be <= 4")
        if not isinstance(address, list):
            rpfatal(f"SPI address is not list")
        if len(address) > 4:
            rpfatal(f"SPI address byte size must be <= 4")
        if not isinstance(data, list):
            rpfatal(f"SPI data is not list")

        fields = [[int(SPI_OPERATION_TYPE.SPI_WR)], [spi_port], [cs_id],
                  [n_data_lane], data]
        n_each_field_bytes = [1, 1, 1,
                              1, len(data)]

        if n_instruction_bits >= 0:
            fields += [[n_instruction_lane], [n_instruction_bits], instruction]
            n_each_field_bytes += [1, 1, len(instruction)]

        if n_address_bits >= 0:
            fields += [[n_address_lane], [n_address_bits], address]
            n_each_field_bytes += [1, 1, len(address)]

        x = PystPacket(pcomponent=spi_port+EROTComponent.AP0_SPI, proutine=0, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)


    def read(self, rockpy_handle, spi_port, cs_id, 
            n_instruction_lane, n_instruction_bits, instruction, 
            n_address_lane, n_address_bits, address, 
            n_data_lane, nbr_rd_bytes, dummy_cycles):
        if not isinstance(instruction, list):
            rpfatal(f"SPI instruction is not list")
        if len(instruction) > 4:
            rpfatal(f"SPI instruction byte size must be <= 4")
        if not isinstance(address, list):
            rpfatal(f"SPI address is not list")
        if nbr_rd_bytes <= 0:
            rpfatal(f"Number of bytes to read must be > 0")

        data = [0]*nbr_rd_bytes

        fields = [[int(SPI_OPERATION_TYPE.SPI_RD)], [spi_port], [cs_id],
                  [n_data_lane], data]
        n_each_field_bytes = [1, 1, 1,
                              1, len(data)]

        if n_instruction_bits >= 0:
            fields += [[n_instruction_lane], [n_instruction_bits], instruction]
            n_each_field_bytes += [1, 1, len(instruction)]

        if n_address_bits >= 0:
            fields += [[n_address_lane], [n_address_bits], address]
            n_each_field_bytes += [1, 1, len(address)]

        fields += [dummy_cycles.to_bytes(4, 'little')]
        n_each_field_bytes += [4]

        x = PystPacket(pcomponent=spi_port+EROTComponent.AP0_SPI, proutine=0, n_each_field_bytes=n_each_field_bytes, fields=fields)
        ans = rockpy_handle.transport(x)
        return list(ans.payload.fields[4])
    
    def set_sclk_frequency(self, rockpy_handle, spi_port, freq_sel: SPI_SCLK_FREQ_SEL):
        fields = [[int(SPI_OPERATION_TYPE.SPI_FREQ_CFG)], [spi_port], [int(freq_sel)]]
        n_each_field_bytes = [1, 1, 1]
        x = PystPacket(pcomponent=spi_port+EROTComponent.AP0_SPI, proutine=0, n_each_field_bytes=n_each_field_bytes, fields=fields)
        rockpy_handle.transport(x)
