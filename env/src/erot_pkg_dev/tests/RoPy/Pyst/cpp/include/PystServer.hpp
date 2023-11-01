#ifndef __PYST_SERVER_HPP__
#define __PYST_SERVER_HPP__

void signal_handler(int signum);
int build_server(uint32_t port);
int start_server();
int stop_server();
int free_server();
int server_is_alive();
int server_is_empty();
uint32_t get_next_message(uint8_t* msg);
void put_next_message(uint32_t len, uint8_t* msg);

#endif