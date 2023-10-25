// SPDX-License-Identifier: GPL-2.0-or-later

/***************************************************************************
 *   Copyright (C) 2005 by Dominic Rath                                    *
 *   Dominic.Rath@gmx.de                                                   *
 *                                                                         *
 *   Copyright (C) 2007-2010 Øyvind Harboe                                 *
 *   oyvind.harboe@zylin.com                                               *
 *                                                                         *
 *   Copyright (C) 2008 Richard Missenden                                  *
 *   richard.missenden@googlemail.com                                      *
 ***************************************************************************/

#ifdef HAVE_CONFIG_H
#include "config.h"
#endif

#include "openocd.h"
#include <jtag/adapter.h>
#include <jtag/jtag.h>
#include <transport/transport.h>
#include <helper/util.h>
#include <helper/configuration.h>
#include <flash/nor/core.h>
#include <flash/nand/core.h>
#include <pld/pld.h>
#include <target/arm_cti.h>
#include <target/arm_adi_v5.h>
#include <target/arm_tpiu_swo.h>
#include <rtt/rtt.h>

#include <server/server.h>
#include <server/gdb_server.h>
#include <server/rtt_server.h>
#include "jtag/drivers/mpsse.h"

#include <unistd.h>
#include <stdio.h>
#include "PystParam.hpp"
#include "PystMain.hpp"
#include "PystForPureC.h"
#include "local_util.h"

#ifdef HAVE_STRINGS_H
#include <strings.h>
#endif

#ifdef PKGBLDDATE
#define OPENOCD_VERSION	\
	"Open On-Chip Debugger " VERSION RELSTR " (" PKGBLDDATE ")"
#else
#define OPENOCD_VERSION	\
	"Open On-Chip Debugger " VERSION RELSTR
#endif


static uint32_t port = 0;
int no_scan_verbo = 0;
int irscan_num_bits = 0;
int scan_num_bits = 0;
uint8_t* scan_values;
struct mpsse_ctx *mpsse_ctx_hack = NULL;
uint8_t ftdi_jtag_mode_hack;

void capture_port(int* argc, char *argv[]){
  char port_arg[] = "-socket";
  int found = 0;
  for(int i=0; i<*argc; i++){
    if(found){
      argv[i-2] = argv[i];
    } else if(!strcmp(argv[i], port_arg)){
      found = 1;
      port = atoi(argv[i+1]);
      i++;
    }
  }
  if(found){
    *argc -= 2;
  }
}

void capture_verbosity(int* argc, char *argv[]){
  char verbo_arg[] = "-no_scan_verbo";
  int found = 0;
  for(int i=0; i<*argc; i++){
    if(found){
      argc[i-1] = argc[i];
    } else if(!strcmp(argv[i], verbo_arg)){
      found = 1;
      no_scan_verbo = 1;
    }
  }
  if(found){
	*argc -= 1;
  }
}

char value_str[65536] = {0};
void dump_to_hex(const uint8_t* arr, uint32_t len, bool reverse){
	memset(value_str, 0, 65536);
	if(!reverse){
		for(int32_t b=0; b<(int)len; b++){
			sprintf(&value_str[2*b], "%02x", arr[b]);
		}
	} else {
		for(int32_t i=len-1,j=0; j<(int)len; i--,j++){
			sprintf(&value_str[2*j], "%02x", arr[i]);
		}
	}
	
	value_str[2*len] = '\0';
}

void set_scan_value(const uint8_t* value){
	int n_byte = (scan_num_bits+7)/8;
	scan_values = (uint8_t*)malloc(n_byte);
	memset(scan_values, 0, n_byte);
	for(int i=0; i<n_byte; i++){
		scan_values[i] = value[i];
	}
}

void reset_scan_value(void){
	if(scan_values != NULL){
		free(scan_values);
	}
}

uint32_t bytes4_to_u32(unsigned char field[4]){
  return (field[0] << 0)  |
         (field[1] << 8)  |
         (field[2] << 16) |
         (field[3] << 24);
}

void u32_to_bytes4(uint32_t u32, unsigned char field[4]){
  field[0] = (u32 >> 0)  & 0xff;
  field[1] = (u32 >> 8)  & 0xff;
  field[2] = (u32 >> 16) & 0xff;
  field[3] = (u32 >> 24) & 0xff;
}


void display_pkt(PystPacketStruct* p_pkt){
	LOG_USER("-> id = %d\n", p_pkt->id);
	LOG_USER("-> type = %d\n", p_pkt->ptype);
	LOG_USER("-> component = %d\n", p_pkt->component);
	LOG_USER("-> routine = %d\n", p_pkt->routine);
	LOG_USER("-> n_fields = %d\n", p_pkt->n_fields);
	for(int i=0;i<(int)p_pkt->n_fields;i++){
		LOG_USER("  -> n_bytes_field[%d] = %d\n", i, p_pkt->n_each_field_bytes[i]);
		for(int j=0;j<(int)p_pkt->n_each_field_bytes[i];j++){
			LOG_USER("    -> 0x%x\n", p_pkt->fields[i][j]);
		}
	}
}


static const char openocd_startup_tcl[] = {
#include "startup_tcl.inc"
0 /* Terminate with zero */
};

/* Give scripts and TELNET a way to find out what version this is */
static int jim_version_command(Jim_Interp *interp, int argc,
	Jim_Obj * const *argv)
{
	if (argc > 2)
		return JIM_ERR;
	const char *str = "";
	char *version_str;
	version_str = OPENOCD_VERSION;

	if (argc == 2)
		str = Jim_GetString(argv[1], NULL);

	if (strcmp("git", str) == 0)
		version_str = GITVERSION;

	Jim_SetResult(interp, Jim_NewStringObj(interp, version_str, -1));

	return JIM_OK;
}

#ifdef __NO_USE__
static int log_target_callback_event_handler(struct target *target,
	enum target_event event,
	void *priv)
{
	switch (event) {
		case TARGET_EVENT_GDB_START:
			target->verbose_halt_msg = false;
			break;
		case TARGET_EVENT_GDB_END:
			target->verbose_halt_msg = true;
			break;
		case TARGET_EVENT_HALTED:
			if (target->verbose_halt_msg) {
				/* do not display information when debugger caused the halt */
				target_arch_state(target);
			}
			break;
		default:
			break;
	}

	return ERROR_OK;
}
#endif

static bool init_at_startup = true;

COMMAND_HANDLER(handle_noinit_command)
{
	if (CMD_ARGC != 0)
		return ERROR_COMMAND_SYNTAX_ERROR;
	init_at_startup = false;
	return ERROR_OK;
}


// char  global_tdo_value[32]; //MAX 256 bit

// ----------------------------------------------------------
char  global_tdo_value[1024];
uint8_t global_tdo[1024/2];

int hex2int(char ch){
    if (ch >= '0' && ch <= '9')
        return ch - '0';
    if (ch >= 'A' && ch <= 'F')
        return ch - 'A' + 10;
    if (ch >= 'a' && ch <= 'f')
        return ch - 'a' + 10;
    return -1;
}

char int2hex(int x){
	if(x <= 9){
		return '0'+x;
	} else {
		return 'A'+x-10;
	}
}

void print_global_tdo(int n_bits){
	int len_bytes = (n_bits+7)/8;
	dump_to_hex(global_tdo, len_bytes, true);
	if(!no_scan_verbo){
		LOG_USER("TDO = %s", value_str);
	}
}

// global_tdo is directly set from core.c, this function is no longer needed.
void tdo2bytes(uint32_t scan_nbits){
	int n_char = (scan_nbits+7)/8 * 2;
	memset(global_tdo, 0, 1024/2);
	for(int i=n_char-1,j=0; i>=0; i-=2,j++){
		global_tdo[j] = hex2int(global_tdo_value[i]) & 0xf;
		if(i-1 >= 0){
			global_tdo[j] |= ((hex2int(global_tdo_value[i-1]) & 0xf) << 4);
		}
	}
}

// ----------------------------------------------------------

/* OpenOCD can't really handle failure of this command. Patches welcome! :-) */
COMMAND_HANDLER(handle_init_command)
{
	if (CMD_ARGC != 0)
		return ERROR_COMMAND_SYNTAX_ERROR;

	int retval;
	static int initialized;
	if (initialized)
		return ERROR_OK;

	initialized = 1;

	//bool save_poll_mask = jtag_poll_mask();

	retval = command_run_line(CMD_CTX, "target init");
	if (retval != ERROR_OK)
		return ERROR_FAIL;

	retval = adapter_init(CMD_CTX);
	if (retval != ERROR_OK) {
		/* we must be able to set up the debug adapter */
		return retval;
	}

	LOG_DEBUG("Debug Adapter init complete");


  {
	uint32_t last_rst_val = 0; 
    uint32_t ports[1] = {port};
    int len = 0;
	uint8_t i2c_rd_data[32] = {0};
    uint8_t message[MAX_PACKET_TOTAL_BYTES_LIMIT];
    PystPacketStruct* p_in_pkt = packet_new();
    PystPacketStruct* p_out_pkt = packet_new();

	uint8_t SMBus_read_command = 0;
    uint32_t SMBus_read_address = 0;

	// BMC i2c init
	FT_HANDLE ftHandle = NULL;
    if(!SMBus_init(20, &ftHandle)){
		LOG_USER("BMC I2C initialization failed\n");
        return 1;
    } else {
		LOG_USER("BMC I2C initialization Succeeded\n");
	}

	//AP0 SPI init
	FT_HANDLE fthandle_spi = NULL;
	if(!SPI_init(&fthandle_spi)){
		LOG_USER("SPI initialization failed\n");
        return 1;
	}else{
		LOG_USER("SPI initialization Succeeded\n");
	}


    pyst_service_start(1, ports, 1);

	// sneak tap state only for openocd, 10 is abitrary
	command_context_mode(CMD_CTX, COMMAND_CONFIG);
	command_run_linef(CMD_CTX,"jtag newtap EROT TAP -irlen 10 -enable");
	command_context_mode(CMD_CTX, COMMAND_EXEC);

    while(1){
      while(!pyst_has_message()){}
      len = pyst_receive_message(MAX_PACKET_TOTAL_BYTES_LIMIT, message, 1);
      bytes2pkt(len, message, p_in_pkt);

 	//   display_pkt(p_in_pkt);

      switch(p_in_pkt->component){
        case 1: {
			LOG_USER("COMPONENT_CAR unsupported");
			packet_copy(p_in_pkt, p_out_pkt);
			break;
		}
        case 2: {
			LOG_USER("COMPONENT_SIM_PRIV unsupported");
			packet_copy(p_in_pkt, p_out_pkt);
			break;
		}
        case 3: {
          switch(p_in_pkt->routine){
            case 0:{
              uint32_t value = bytes4_to_u32(p_in_pkt->fields[0]);
              LOG_USER("ftdi set_signal nTRST %d", value);
              command_context_mode(CMD_CTX, COMMAND_EXEC);
              command_run_linef(CMD_CTX, "ftdi set_signal nTRST %d", value);
			  last_rst_val = value;
              packet_copy(p_in_pkt, p_out_pkt);
              break;
            }
            case 1: {
              uint32_t value = bytes4_to_u32(p_in_pkt->fields[0]);
              LOG_USER("ftdi set_signal LED %d", value);
              command_context_mode(CMD_CTX, COMMAND_EXEC);
              command_run_linef(CMD_CTX, "ftdi set_signal LED %d", value);
              packet_copy(p_in_pkt, p_out_pkt);
              break;
            }
            case 2: { //jtag_tap
            //   uint32_t value = bytes4_to_u32(p_in_pkt->fields[0]);
            //   command_context_mode(CMD_CTX, COMMAND_CONFIG);
            //   LOG_USER("jtag newtap EROT TAP -irlen %d -enable", value);
			//   irscan_num_bits = value;
			//   command_run_linef(CMD_CTX,"jtag newtap EROT TAP -irlen %d -enable", value);
            //   command_context_mode(CMD_CTX, COMMAND_EXEC);
              packet_copy(p_in_pkt, p_out_pkt);
              break;
            }
            case 3: { //jtag_irscan
              uint32_t numbits = bytes4_to_u32(p_in_pkt->fields[0]);

			  dump_to_hex(p_in_pkt->fields[1], p_in_pkt->n_each_field_bytes[1], true);
			  if(!no_scan_verbo){
				LOG_USER("irscan, %d bits, scan in 0x%s", numbits, value_str);
			  }
              command_context_mode(CMD_CTX, COMMAND_EXEC);
			  scan_num_bits = numbits;
			  set_scan_value(p_in_pkt->fields[1]);
              command_run_linef(CMD_CTX, "irscan EROT.TAP %d ", 0);
			  reset_scan_value();
              print_global_tdo(scan_num_bits);
              packet_copy(p_in_pkt, p_out_pkt);
			  add_ret(p_out_pkt, (uint32_t*)&len, global_tdo, p_in_pkt->n_each_field_bytes[1]);
              break;
            }
            case 4: {
              uint32_t numbits = bytes4_to_u32(p_in_pkt->fields[0]);

              dump_to_hex(p_in_pkt->fields[1], p_in_pkt->n_each_field_bytes[1], true);
			  if(!no_scan_verbo){
				LOG_USER("drscan, %d bits, scan in 0x%s", numbits, value_str);
			  }
              command_context_mode(CMD_CTX, COMMAND_EXEC);
			  scan_num_bits = numbits;
			  set_scan_value(p_in_pkt->fields[1]);
              command_run_linef(CMD_CTX,"jtag drscan EROT.TAP %d 0x%x", 0, 0);
			  reset_scan_value();
			  print_global_tdo(scan_num_bits);
              packet_copy(p_in_pkt, p_out_pkt);
              add_ret(p_out_pkt, (uint32_t*)&len, global_tdo, p_in_pkt->n_each_field_bytes[1]);
              break;
            }
			case 5: { // jtag wait
              // p_in_pkt->fields[0]: number of TCK cycles
              uint32_t ncycle = bytes4_to_u32(p_in_pkt->fields[0]);
			  uint8_t* fake_in_values = (uint8_t*)malloc((ncycle+7)/8);
			  uint8_t* fake_out_values = (uint8_t*)malloc((ncycle+7)/8);
			  memset(fake_in_values, 0, (ncycle+7)/8);
			  memset(fake_out_values, 0, (ncycle+7)/8);

			  if(!no_scan_verbo){
				LOG_USER("wait, %d cycles", ncycle);
			  }
			  
			  command_run_linef(CMD_CTX, "ftdi set_signal nTRST %d", last_rst_val);
              mpsse_clock_data(mpsse_ctx_hack,
				fake_out_values,
				0,
				fake_in_values,
				0,
				ncycle - 1,
				ftdi_jtag_mode_hack);
			  command_run_linef(CMD_CTX, "ftdi set_signal nTRST %d", last_rst_val);
			  if(fake_in_values != NULL){
				free(fake_in_values);
			  }
			  if(fake_out_values != NULL){
				free(fake_out_values);
			  }
			  packet_copy(p_in_pkt, p_out_pkt);
              break;
            }
            default: {
				LOG_USER("Error: Unknown JTAG case");
				packet_copy(p_in_pkt, p_out_pkt);
				break;
			}    
          } // switch routine

		  break; // component 3 break
		}  

        case 4: // component 4, same as component 5, 6, leave it empty
		        // 4 -> AP0 I2C, 5 -> AP1 I2C, 6 -> BMC I2C
		case 5: // component 4, same as component 5, 6, leave it empty

		case 6: { // component 6
			// fld[0]: addr
			// fld[1]: data (real in wr, fake in rd)

			uint32_t en_10bits_addr = 0;
			uint32_t addr = bytes4_to_u32(p_in_pkt->fields[0]);
			uint8_t* data = NULL;
			uint32_t send_size = 0;
			
			if (p_in_pkt->n_each_field_bytes[1] == 0){
				LOG_USER("Error: Data send size = %d is invalid. Should be >= 1 ", p_in_pkt->n_each_field_bytes[1]);
			} else {
				send_size = p_in_pkt->n_each_field_bytes[1];
			}
			
			data = (uint8_t*)malloc(send_size);

			// meaningful in write
			for(uint32_t i=0;i<send_size;i++){
				data[i] = p_in_pkt->fields[1][i];
			}
			
			if (((addr & 0xffff0000) >> 16) == 0xffff){
				en_10bits_addr = 1;
			} else if (((addr & 0xffff0000) >> 16) == 0){
				en_10bits_addr = 0;
			} else {
				LOG_USER("Error: Unsupported addr 0x%x", addr);
			}
			
			addr = en_10bits_addr? (addr & 0x3ff) : (addr & 0x7f);

			switch(p_in_pkt->routine){
				case 0: { // issue_write_req
					uint32_t i2c_id = 1;
					if(p_in_pkt->component == 5){
						i2c_id = 2;
					} else if (p_in_pkt->component == 6){
						i2c_id = 3;
					}

					if(p_in_pkt->component == 6){ // only does BMC I2C support SMBus write now
						if(send_size == 1){ // SMbus read command phase
							SMBus_read_command = data[0];
							SMBus_read_address = addr;
							if(!no_scan_verbo){
								LOG_USER("[IGNORE] BMC I2C wants to write 1 byte command to addr 0x%x, captured command = 0x%x\n", SMBus_read_address, SMBus_read_command);
							}
						} else { // real SMBus write
							if(!no_scan_verbo){
								LOG_USER("BMC SMBus write to 0x%x with command 0x%x count 0x%x\n", addr, data[0], data[1]);
							}
							if(!SMBus_write(ftHandle, addr, data[0], data[1], &data[2])){
								LOG_USER("Error: I2C SMbus write failed!\n");
							}
						}					
					} else { // Normal I2C write
						if(i2ctransfer(i2c_id, addr, p_in_pkt->routine, send_size, data)){
							if(!no_scan_verbo){
								LOG_USER("I2C write request sent\n");
							}
						} else {
							LOG_USER("Error: I2C write request sent failed!\n");
						}
					}
					packet_copy(p_in_pkt, p_out_pkt);
					break;
				}
				
				case 1: { // issue_read_req
					uint32_t i2c_id = 1;
					if(p_in_pkt->component == 5){
						i2c_id = 2;
					} else if (p_in_pkt->component == 6){
						i2c_id = 3;
					}

					if(p_in_pkt->n_fields >= 3){ // SMbus read
						if(p_in_pkt->component == 6){ // only does BMC I2C support SMBus read now
							if(p_in_pkt->fields[2][0] == 1){
								// WAS Sr Addr Rd [A] [Count]  HRER, BUT I DON'T NEED IT
								// do nothing
								if(!no_scan_verbo){
									LOG_USER("[IGNORE] BMC I2C wants to read 1 byte count from 0x%x, but I don't care about it. Will fake 32 for the following bytes to read.\n", SMBus_read_address);
								}
								send_size = 1; // [Count] is 1 byte
								i2c_rd_data[0] = 32;
							} else {
								// time to send the real SMBus read
								// don't know how much to read, but i2c_rd_data 32 bytes long should be enough
									uint16_t n_bytes_rd = SMBus_read(ftHandle, SMBus_read_address, SMBus_read_command, 32, i2c_rd_data);
									send_size = n_bytes_rd;
									if(!no_scan_verbo){
										LOG_USER("BMC SMBus read from 0x%x with command 0x%x\n", SMBus_read_address, SMBus_read_command);
									}
							}
						}
					} else { // Normal I2C read
						if(i2ctransfer(i2c_id, addr, p_in_pkt->routine, send_size, data)){
							if(!no_scan_verbo){
								LOG_USER("I2C read request sent\n");
							}
							memset(i2c_rd_data, 0, 32);
							for(uint32_t i=0;i<send_size;i++){
								i2c_rd_data[i] = data[i];
							}
						} else {
							LOG_USER("Error: I2C read request sent failed!\n");
						}
					}
					packet_copy(p_in_pkt, p_out_pkt);
					p_out_pkt->n_fields = 1; // get rid of original fake in rd data
					add_ret(p_out_pkt, (uint32_t*)&len, i2c_rd_data, send_size);
					break;
				}
				
				default: {
					LOG_USER("Error: Unknown I2C routine");
					break;
				}
			}

			if(data != NULL){
				free(data);
			}

		  	break; // I2C component break
		}

		//case 7: //component 7, same as component 8, 9, leave it empty
		//		// 7 -> AP0 SPI, 8 -> AP1 SPI, 9 -> OOB SPI
		case 7: //component 7, same as component 8, leave it empty

		case 8: {

				uint32_t op_type    = p_in_pkt->fields[0][0];
				uint32_t spi_id 	= p_in_pkt->fields[1][0];
				uint32_t cs_id  	= p_in_pkt->fields[2][0];
				uint8_t* data       = NULL;
				uint32_t data_lane  = p_in_pkt->fields[3][0];
				uint32_t data_size  = p_in_pkt->n_each_field_bytes[4];
				uint32_t inst_lane  = 0;
				uint32_t inst_bits  = 0;
				uint32_t inst_size  = 0;
				uint8_t* inst       = NULL;
				uint32_t addr_lane  = 0;
				uint32_t addr_bits  = 0;
				uint32_t addr_size  = 0;
				uint8_t* addr       = NULL;
				uint32_t dummy_cycles = 0;

				if(!SPI_config(fthandle_spi,CLK_DIV_128,cs_id)){
					LOG_USER("\nSPI Trans : SPI config failed");
				}else{
					LOG_USER("\nSPI Trans : SPI config Succeeded");
				}


				LOG_USER("SPI Trans : op_type = %d (0 read, 1 write), spi_id = %d, cs_id = %d (2 spi target), iolane = %d",op_type,spi_id,cs_id,data_lane);
				LOG_USER("SPI Trans : field size = %d",sizeof(p_in_pkt->n_each_field_bytes));
				if (sizeof(p_in_pkt->n_each_field_bytes) > 3){
					inst_lane = p_in_pkt->fields[5][0];
					inst_bits = p_in_pkt->fields[6][0];
					addr_lane = p_in_pkt->fields[8][0];
					addr_bits = p_in_pkt->fields[9][0];
					inst_size = inst_bits/8;
					LOG_USER("SPI Trans : instruction info : inst_lane = %d, inst_bits = %d",inst_lane,inst_bits);
					if (inst_size > 0){
						inst = (uint8_t*)malloc(inst_bits/8);
						for(uint32_t i=0;i<inst_bits/8;i++){
							inst[i] = p_in_pkt->fields[7][i];
							LOG_USER("SPI Trans : inst[%d] = %02x",i,inst[i]);
						}
					}
					addr_size = addr_bits/8;
					LOG_USER("SPI Trans : address info : addr_lane = %d, addr_bits = %d",addr_lane,addr_bits);
					if (addr_size > 0){
						addr = (uint8_t*)malloc(addr_bits/8);
						for(uint32_t i=0;i<addr_bits/8;i++){
							addr[i] = p_in_pkt->fields[10][i];
							LOG_USER("SPI Trans : addr[%d] = %02x",i,addr[i]);
						}
					}
					if (op_type == 0 && p_in_pkt->fields[11][0] != 0xff ){
						dummy_cycles = bytes4_to_u32(p_in_pkt->fields[11]);
					}
					//for(uint32_t i=0;i<4;i++){
					//	LOG_USER("SPI Trans : dummy_cycle[%d] = %02x",i,p_in_pkt->fields[11][i]);
					//}

				}
					LOG_USER("SPI Trans : dummy_cycles = %d",dummy_cycles);

				if (data_size == 0){
					LOG_USER("Error: Data send size = %d is invalid. Should be >= 1 ", p_in_pkt->n_each_field_bytes[1]);
				} else {
					LOG_USER("SPI Trans : data_size = %d",data_size);
				}

				switch(op_type){
					case 0 : { // spi read
						uint32_t recvLen = 0; //bytes number
						uint32_t sendLen = 0; //bytes number
						uint32_t singleBytes = 0; //bytes number
						uint8_t* sbuf;							
						uint8_t* rbuf;							
						
						recvLen = data_size + data_lane*dummy_cycles/8;
						sendLen = inst_size + addr_size; 
						singleBytes = sendLen;
						sbuf = (uint8_t*)malloc(sendLen);
						LOG_USER("\nSPI Trans : SPI READ Transfer Begin\n");
						for(uint32_t i=0;i<sendLen;i++){
							if (i < inst_size){
								sbuf[i] = inst[i];
							} else if  (i >= inst_size && i < inst_size + addr_size){
								sbuf[i] = addr[i - inst_size];
							} else {
								sbuf[i] = data[i - inst_size - addr_size];
							}
							LOG_USER("SPI Trans : sbuf[%d] = %02x",i,sbuf[i]);
						}
						rbuf = (uint8_t*)malloc(recvLen);
						if(!SPI_read(fthandle_spi,cs_id,data_lane,sendLen,sbuf,recvLen,rbuf,true,singleBytes)){
							LOG_USER("Error: SPI read failed!\n");
						}
						for(uint32_t i=0;i<recvLen;i++){
							LOG_USER("SPI Trans : rbuf[%d] = %02x",i,rbuf[i]);
						}

						uint8_t *rbuf2 = &rbuf[dummy_cycles*data_lane/8];
						for(uint32_t i=0;i<recvLen-(dummy_cycles*data_lane/8);i++){
							LOG_USER("SPI Trans : rbuf2[%d] = %02x",i,rbuf2[i]);
						}
						packet_copy(p_in_pkt, p_out_pkt);
						p_out_pkt->n_fields = 4; // field number before return data
						add_ret(p_out_pkt, (uint32_t*)&len, rbuf2, recvLen-(dummy_cycles*data_lane/8));
						free(rbuf);
						if (sbuf != NULL){
							free(sbuf);
						}
						break;
					}

					case 1 : { // spi write
						uint32_t send_size = data_size;
						uint32_t sendLen = 0; //bytes number
						uint32_t singleBytes = 0; //bytes number
						uint8_t* sbuf;
						

						LOG_USER("\nSPI Trans : SPI WRITE Transfer Begin\n");
						data = (uint8_t*)malloc(send_size);
						// meaningful in write
						for(uint32_t i=0;i<send_size;i++){
							data[i] = p_in_pkt->fields[4][i];
							LOG_USER("SPI Trans : data[%d] = %02x",i,data[i]);
						}

						sendLen = inst_size + addr_size + send_size;
						singleBytes = inst_size + addr_size;
						sbuf = (uint8_t*)malloc(sendLen);
						for(uint32_t i=0;i<sendLen;i++){
							if (i < inst_size){
								sbuf[i] = inst[i];
							} else if  (i >= inst_size && i < inst_size + addr_size){
								sbuf[i] = addr[i - inst_size];
							} else {
								sbuf[i] = data[i - inst_size - addr_size];
							}
							LOG_USER("SPI Trans : sbuf[%d] = %02x",i,sbuf[i]);
						}
						if(!SPI_write(fthandle_spi,cs_id,data_lane,sendLen,sbuf,true,singleBytes)){
							LOG_USER("Error: SPI write failed!\n");
						}
						packet_copy(p_in_pkt, p_out_pkt);
						free(sbuf);
						break;
					}
					case 2 : { // spi set sck frequency
						break;
					}

					default: {
						LOG_USER("Error: Unknown SPI routine");
						break;
					}
				}

				if(data != NULL){
					free(data);
				}
				if(inst != NULL){
					free(inst);
				}
				if(addr != NULL){
					free(addr);
				}
				LOG_USER("\nSPI Trans : SPI Transfer END\n");
				break;
		}

        default: {
			if(p_in_pkt->component != 0 && p_in_pkt->routine != 0){ // not "DONE" routine
				LOG_USER("Warning: Unsupported component %d, routine %d for FPGA", p_in_pkt->component, p_in_pkt->routine);
			}
		  	
			packet_copy(p_in_pkt, p_out_pkt);
			break;
		} 
      }
	  // display_pkt(p_out_pkt);
      pyst_send_message(len, p_out_pkt->bytes, 1);

      if(p_in_pkt->ptype == 2000){
        // break;
      }
    }
    packet_free(p_in_pkt);
    packet_free(p_out_pkt);
	SMBus_close(ftHandle);
	SPI_close(fthandle_spi);
    pyst_service_stop();

  }



	#ifdef __NO_USE__
	retval = command_run_line(CMD_CTX, "transport init");
	if (retval != ERROR_OK)
		return ERROR_FAIL;

	retval = command_run_line(CMD_CTX, "dap init");
	if (retval != ERROR_OK)
		return ERROR_FAIL;

	LOG_DEBUG("Examining targets...");
	if (target_examine() != ERROR_OK)
		LOG_DEBUG("target examination failed");

	command_context_mode(CMD_CTX, COMMAND_CONFIG);

	if (command_run_line(CMD_CTX, "flash init") != ERROR_OK)
		return ERROR_FAIL;

	if (command_run_line(CMD_CTX, "nand init") != ERROR_OK)
		return ERROR_FAIL;

	if (command_run_line(CMD_CTX, "pld init") != ERROR_OK)
		return ERROR_FAIL;
	command_context_mode(CMD_CTX, COMMAND_EXEC);

	/* in COMMAND_EXEC, after target_examine(), only tpiu or only swo */
	if (command_run_line(CMD_CTX, "tpiu init") != ERROR_OK)
		return ERROR_FAIL;

	jtag_poll_unmask(save_poll_mask);

	/* initialize telnet subsystem */
	gdb_target_add_all(all_targets);

	target_register_event_callback(log_target_callback_event_handler, CMD_CTX);

	if (command_run_line(CMD_CTX, "_run_post_init_commands") != ERROR_OK)
		return ERROR_FAIL;
	#endif
	return ERROR_OK;
}

COMMAND_HANDLER(handle_add_script_search_dir_command)
{
	if (CMD_ARGC != 1)
		return ERROR_COMMAND_SYNTAX_ERROR;

	add_script_search_dir(CMD_ARGV[0]);

	return ERROR_OK;
}

static const struct command_registration openocd_command_handlers[] = {
	{
		.name = "version",
		.jim_handler = jim_version_command,
		.mode = COMMAND_ANY,
		.help = "show program version",
	},
	{
		.name = "noinit",
		.handler = &handle_noinit_command,
		.mode = COMMAND_CONFIG,
		.help = "Prevent 'init' from being called at startup.",
		.usage = ""
	},
	{
		.name = "init",
		.handler = &handle_init_command,
		.mode = COMMAND_ANY,
		.help = "Initializes configured targets and servers.  "
			"Changes command mode from CONFIG to EXEC.  "
			"Unless 'noinit' is called, this command is "
			"called automatically at the end of startup.",
		.usage = ""
	},
	{
		.name = "add_script_search_dir",
		.handler = &handle_add_script_search_dir_command,
		.mode = COMMAND_ANY,
		.help = "dir to search for config files and scripts",
		.usage = "<directory>"
	},
	COMMAND_REGISTRATION_DONE
};

static int openocd_register_commands(struct command_context *cmd_ctx)
{
	return register_commands(cmd_ctx, NULL, openocd_command_handlers);
}

/*
 * TODO: to be removed after v0.12.0
 * workaround for syntax change of "expr" in jimtcl 0.81
 * replace "expr" with openocd version that prints the deprecated msg
 */
struct jim_scriptobj {
	void *token;
	Jim_Obj *filename_obj;
	int len;
	int subst_flags;
	int in_use;
	int firstline;
	int linenr;
	int missing;
};

static int jim_expr_command(Jim_Interp *interp, int argc, Jim_Obj * const *argv)
{
	if (argc == 2)
		return Jim_EvalExpression(interp, argv[1]);

	if (argc > 2) {
		Jim_Obj *obj = Jim_ConcatObj(interp, argc - 1, argv + 1);
		Jim_IncrRefCount(obj);
		const char *s = Jim_String(obj);
		struct jim_scriptobj *script = Jim_GetIntRepPtr(interp->currentScriptObj);
		if (interp->currentScriptObj == interp->emptyObj ||
				strcmp(interp->currentScriptObj->typePtr->name, "script") ||
				script->subst_flags ||
				script->filename_obj == interp->emptyObj)
			LOG_WARNING("DEPRECATED! use 'expr { %s }' not 'expr %s'", s, s);
		else
			LOG_WARNING("DEPRECATED! (%s:%d) use 'expr { %s }' not 'expr %s'",
						Jim_String(script->filename_obj), script->linenr, s, s);
		int retcode = Jim_EvalExpression(interp, obj);
		Jim_DecrRefCount(interp, obj);
		return retcode;
	}

	Jim_WrongNumArgs(interp, 1, argv, "expression ?...?");
	return JIM_ERR;
}

static const struct command_registration expr_handler[] = {
	{
		.name = "expr",
		.jim_handler = jim_expr_command,
		.mode = COMMAND_ANY,
		.help = "",
		.usage = "",
	},
	COMMAND_REGISTRATION_DONE
};

static int workaround_for_jimtcl_expr(struct command_context *cmd_ctx)
{
	return register_commands(cmd_ctx, NULL, expr_handler);
}

struct command_context *global_cmd_ctx;

static struct command_context *setup_command_handler(Jim_Interp *interp)
{
	log_init();
	LOG_DEBUG("log_init: complete");

	struct command_context *cmd_ctx = command_init(openocd_startup_tcl, interp);

	/* register subsystem commands */
	typedef int (*command_registrant_t)(struct command_context *cmd_ctx_value);
	static const command_registrant_t command_registrants[] = {
		&workaround_for_jimtcl_expr,
		&openocd_register_commands,
		&server_register_commands,
		&gdb_register_commands,
		&log_register_commands,
		&rtt_server_register_commands,
		&transport_register_commands,
		&adapter_register_commands,
		&target_register_commands,
		&flash_register_commands,
		&nand_register_commands,
		&pld_register_commands,
		&cti_register_commands,
		&dap_register_commands,
		&arm_tpiu_swo_register_commands,
		NULL
	};
	for (unsigned i = 0; command_registrants[i]; i++) {
		int retval = (*command_registrants[i])(cmd_ctx);
		if (retval != ERROR_OK) {
			command_done(cmd_ctx);
			return NULL;
		}
	}
	LOG_DEBUG("command registration: complete");

	LOG_OUTPUT(OPENOCD_VERSION "\n"
		"Licensed under GNU GPL v2\n");

	global_cmd_ctx = cmd_ctx;

	return cmd_ctx;
}

/** OpenOCD runtime meat that can become single-thread in future. It parse
 * commandline, reads configuration, sets up the target and starts server loop.
 * Commandline arguments are passed into this function from openocd_main().
 */
static int openocd_thread(int argc, char *argv[], struct command_context *cmd_ctx)
{
	int ret;

	if (parse_cmdline_args(cmd_ctx, argc, argv) != ERROR_OK)
		return ERROR_FAIL;

	if (server_preinit() != ERROR_OK)
		return ERROR_FAIL;

	ret = parse_config_file(cmd_ctx);
	if (ret == ERROR_COMMAND_CLOSE_CONNECTION) {
		server_quit(); /* gdb server may be initialized by -c init */
		return ERROR_OK;
	} else if (ret != ERROR_OK) {
		server_quit(); /* gdb server may be initialized by -c init */
		return ERROR_FAIL;
	}

	//ret = server_init(cmd_ctx);
	//if (ret != ERROR_OK)
	//	return ERROR_FAIL;

	if (init_at_startup) {
		ret = command_run_line(cmd_ctx, "init");
		if (ret != ERROR_OK) {
			//server_quit();
			return ERROR_FAIL;
		}
	}

	//ret = server_loop(cmd_ctx);

	//int last_signal = server_quit();
	//if (last_signal != ERROR_OK)
	//	return last_signal;

	if (ret != ERROR_OK)
		return ERROR_FAIL;
	return ERROR_OK;
}

/* normally this is the main() function entry, but if OpenOCD is linked
 * into application, then this fn will not be invoked, but rather that
 * application will have it's own implementation of main(). */
int openocd_main(int argc, char *argv[])
{
	int ret;

	/* initialize commandline interface */
	struct command_context *cmd_ctx;

    capture_port(&argc, argv);
	capture_verbosity(&argc, argv);

	cmd_ctx = setup_command_handler(NULL);

	if (util_init(cmd_ctx) != ERROR_OK)
		return EXIT_FAILURE;

	if (rtt_init() != ERROR_OK)
		return EXIT_FAILURE;

	LOG_OUTPUT("For bug reports, read\n\t"
		"http://openocd.org/doc/doxygen/bugs.html"
		"\n");

	command_context_mode(cmd_ctx, COMMAND_CONFIG);
	command_set_output_handler(cmd_ctx, configuration_output_handler, NULL);

	server_host_os_entry();

	/* Start the executable meat that can evolve into thread in future. */
	ret = openocd_thread(argc, argv, cmd_ctx);

	flash_free_all_banks();
	gdb_service_free();
	arm_tpiu_swo_cleanup_all();
	server_free();

	unregister_all_commands(cmd_ctx, NULL);
	help_del_all_commands(cmd_ctx);

	/* free all DAP and CTI objects */
	arm_cti_cleanup_all();
	dap_cleanup_all();

	adapter_quit();

	server_host_os_close();

	/* Shutdown commandline interface */
	command_exit(cmd_ctx);

	rtt_exit();
	free_config();

	log_exit();

	if (ret == ERROR_FAIL)
		return EXIT_FAILURE;
	else if (ret != ERROR_OK)
		exit_on_signal(ret);

	return ret;
}
