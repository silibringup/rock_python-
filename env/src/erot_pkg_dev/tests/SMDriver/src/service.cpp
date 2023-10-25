#include <iostream>
#include <fstream>
#include <cstring>
#include <chrono>
#include <thread>
#include "PystParam.hpp"
#include "PystMain.hpp"
#include "PystForPureC.h"
#include "local_util.h"




/////////////////////////////////
#include <sstream>
#include <iomanip>
std::string bytes_stringfy(uint8_t* data, uint32_t len){
    std::stringstream sstrm;
    for(uint32_t i=0; i<len; i++){
        sstrm << "0x" << std::uppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << (unsigned)data[i];
        if(i < len-1){
            sstrm << " ";
        }
    }
    return sstrm.str();
}
/////////////////////////////////


uint32_t capture_port(int* argc, char *argv[]){
    uint32_t port = 0;
    char port_arg[] = "-socket";
    for(int i=0; i<*argc; i++){
        if(!strcmp(argv[i], port_arg)){
            port = atoi(argv[i+1]);
            printf("Given port = %d\n", port);
            return port;
        }
    }
    printf("Port was not provided\n");
    return 0;
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
	printf("-> id = %d\n", p_pkt->id);
	printf("-> type = %d\n", p_pkt->ptype);
	printf("-> component = %d\n", p_pkt->component);
	printf("-> routine = %d\n", p_pkt->routine);
	printf("-> n_fields = %d\n", p_pkt->n_fields);
	for(int i=0;i<(int)p_pkt->n_fields;i++){
		printf("  -> n_bytes_field[%d] = %d\n", i, p_pkt->n_each_field_bytes[i]);
		for(int j=0;j<(int)p_pkt->n_each_field_bytes[i];j++){
			printf("    -> 0x%x\n", p_pkt->fields[i][j]);
		}
	}
}



int main(int argc, char *argv[]){
    uint32_t port = capture_port(&argc, argv);

    uint32_t ports[1] = {port};
    int len = 0;
	uint8_t i2c_rd_data[32] = {0};
    uint8_t message[MAX_PACKET_TOTAL_BYTES_LIMIT];
    PystPacketStruct* p_in_pkt = packet_new();
    PystPacketStruct* p_out_pkt = packet_new();

	uint8_t SMBus_read_command = 0;
    uint32_t SMBus_read_address = 0;
    std::ofstream rd_log ("read.log");
    if (!rd_log.is_open()){
        printf("read.log open failed\n");
        return 1;
    }


	// BMC i2c init
	FT_HANDLE ftHandle = NULL;
    // if(!SMBus_init(1000, &ftHandle)){
    if(!SMBus_init(20, &ftHandle)){
		printf("BMC I2C initialization failed\n");
        return 1;
    } else {
		printf("BMC I2C initialization Succeeded\n");
	}

    pyst_service_start(1, ports, 1);

    while(1){
        while(!pyst_has_message()){}

        len = pyst_receive_message(MAX_PACKET_TOTAL_BYTES_LIMIT, message, 1);
        bytes2pkt(len, message, p_in_pkt);

        // printf("|================= input packet:\n");
        // display_pkt(p_in_pkt);

        switch(p_in_pkt->component){
            case 4: ;
            case 5: ;
            case 6: { // I2C
                uint32_t en_10bits_addr = 0;
                uint32_t addr = bytes4_to_u32(p_in_pkt->fields[0]);
                uint8_t* data = NULL;
                uint32_t send_size = 0;
                
                if (p_in_pkt->n_each_field_bytes[1] == 0){
                    printf("Error: Data send size = %d is invalid. Should be >= 1\n", p_in_pkt->n_each_field_bytes[1]);
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
                    printf("Error: Unsupported addr 0x%x\n", addr);
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
                            	printf("[IGNORE] BMC I2C wants to write 1 byte command to addr 0x%x, captured command = 0x%x\n", SMBus_read_address, SMBus_read_command);
                            } else { // real SMBus write
                            	printf("BMC SMBus write to 0x%x with command 0x%x count 0x%x\n", addr, data[0], data[1]);
                            	if(!SMBus_write(ftHandle, addr, data[0], data[1], &data[2])){
                            		printf("Error: I2C SMbus write failed!\n");
                            	}
                            }
                        } else { // Normal I2C write
                            if(i2ctransfer(i2c_id, addr, p_in_pkt->routine, send_size, data)){
                                printf("I2C write request sent\n");
                            } else {
                                printf("Error: I2C write request sent failed!\n");
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
                            		// WAS  Sr Addr Rd [A] [Count]  HRER, BUT I DON'T NEED IT
                            		// do nothing
                            		printf("[IGNORE] BMC I2C wants to read 1 byte count from 0x%x, but I don't care about it. Will fake 32 for the following bytes to read.\n", SMBus_read_address);
                                    send_size = 1; // [Count] is 1 byte
                                    i2c_rd_data[0] = 32;
                            	} else {
                            		// time to send the real SMBus read
                            		// don't know how much to read, but i2c_rd_data 32 bytes long should be enough
                            		 uint16_t n_bytes_rd = SMBus_read(ftHandle, SMBus_read_address, SMBus_read_command, 32, i2c_rd_data);
                            		 send_size = n_bytes_rd;
                            		 printf("BMC SMBus read from 0x%x with command 0x%x\n", SMBus_read_address, SMBus_read_command);
                            		//  for(int k=0;k<(int)send_size;k++){
                            		// 	printf("rd[%d] = 0x%x\n", k, i2c_rd_data[k]);
                            		//  }
                                    std::string rd_data_txt = bytes_stringfy(i2c_rd_data, send_size);
                                    rd_log << "BMC SMBus read from " << "0x" << std::uppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << SMBus_read_address;
                                    rd_log << " with command " << "0x" << std::uppercase << std::setfill('0') << std::setw(2) << std::right << std::hex << (unsigned)SMBus_read_command << std::endl;
                                    rd_log << rd_data_txt << std::endl;
                            	}
                            }
                        } else { // Normal I2C read
                            if(i2ctransfer(i2c_id, addr, p_in_pkt->routine, send_size, data)){
                                printf("I2C read request sent\n");
                                memset(i2c_rd_data, 0, 32);
                                for(uint32_t i=0;i<send_size;i++){
                                    i2c_rd_data[i] = data[i];
                                }
                            } else {
                                printf("Error: I2C read request sent failed!\n");
                            }
                        }
                        packet_copy(p_in_pkt, p_out_pkt);
                        p_out_pkt->n_fields = 1; // get rid of original fake in rd data
                        add_ret(p_out_pkt, (uint32_t*)&len, i2c_rd_data, send_size);
                        break;
                    }
                    
                    default: {
                        printf("Error: Unknown I2C routine");
                        break;
                    }
                }

                if(data != NULL){
                    free(data);
                }

                break; // I2C component break                    
            }

            default: {
                printf("Warning: Unsupported component %d, routine %d for FPGA\n", p_in_pkt->component, p_in_pkt->routine);
                packet_copy(p_in_pkt, p_out_pkt);
                break;
		    }
        }

        // printf("|================= output packet:\n");
        // display_pkt(p_out_pkt);
        pyst_send_message(len, p_out_pkt->bytes, 1);

        if(p_in_pkt->ptype == 2000){
            printf("Quit service\n");
            break;
        }


    }

    packet_free(p_in_pkt);
    packet_free(p_out_pkt);

	SMBus_close(ftHandle);
    rd_log.close();

    pyst_service_stop();

    return 0;
}