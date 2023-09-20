#include <iostream>
#include <cstring>
#include <csignal>
#include <stdexcept>
#include <thread>
#include <chrono>
#include <time.h>
#include <vector>
#include <queue>
#include <unordered_map>
#include <sstream>
#include <iomanip>
#include <mutex>
#include <cstdlib>
#include <sys/ioctl.h>
#include <errno.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <fcntl.h>
#include "PystParam.hpp"
#include "PystPacket.hpp"
#include "PystSimLib.hpp"
#include "PystServer.hpp"

extern int __PYST_DEBUG;

unsigned int pyst_conn_timeout_limit = 60; // 60 sec default to wait connect
unsigned int pyst_read_timeout_limit = 1800; // 1800 sec default to wait for rd data comming in
unsigned int pyst_last_recv_time = 0;

bool pyst_is_alive = false;
std::thread pyst_heartbeat_thread;
bool pyst_heartbeat_running = false;
std::unordered_map<int, std::thread> pyst_accept_threads; // server socket id, thread
std::unordered_map<int, std::thread> pyst_client_serve_threads; // client socket id, thread
std::unordered_map<int, int> pyst_client_socket_map; // client id, client socket id
std::unordered_map<int, bool> pyst_accept_handler_running; // server socket id, running ctrl
std::unordered_map<int, bool> pyst_client_serve_handler_running; // client socket id, running ctrl


#define PYST_C_BUFFER_SIZE 128
uint8_t  pyst_client_in_messages[PYST_C_BUFFER_SIZE][MAX_PACKET_TOTAL_BYTES_LIMIT] = {0}; // temp recv buffer, [arbitrary slot number][max allowed packet size]
uint32_t pyst_client_in_message_length[PYST_C_BUFFER_SIZE] = {0};
uint32_t pyst_read_ptr  = 0; 
uint32_t pyst_write_ptr = 0; 


typedef struct pyst_packet_id_t {
    uint32_t p_pkt_nbr;
    uint32_t p_thread_id;
    uint32_t p_client_id;
} pyst_packet_id;


void print_logo(){
  std::string welcome_banner = "";
  welcome_banner += "+--------------------------------------------------------+\n"; 
  welcome_banner += "|                                                        |\n";
  welcome_banner += "|   **********   Rock Python Kernel 0.211   **********   |\n";
  welcome_banner += "|                                                        |\n";
  welcome_banner += "+--------------------------------------------------------+\n";
  printf("%s", welcome_banner.c_str());
}


pyst_packet_id decode_pid(uint8_t* msg){
    pyst_packet_id pid;
    pid.p_client_id = msg[0];
    pid.p_thread_id = msg[1];
    pid.p_pkt_nbr   = (msg[2] << 8 | msg[3]);
    return pid;
}

void show_pkt(char* prefix, int len, uint8_t* msg){
    if(__PYST_DEBUG){
        pyst_packet_id pid = decode_pid((uint8_t*)msg);
        std::stringstream ss;

        ss << "[" << prefix << "] client[" << pid.p_client_id << "].thread[" << pid.p_thread_id << "],";
        for(int i=0;i<len;i++){
            ss << " [" << std::hex << std::setw(2) << std::setfill('0') << 
                "0x" << std::uppercase << (uint32_t)msg[i] << "]";
        }

        pystdebug("%s\n", ss.str().c_str());
    }
}


int set_socket_non_blocking(int skt){
    int flags = fcntl(skt, F_GETFL);
    if(flags < 0){
        pysterror("Can't Get Server Socket Flags: %s\n", strerror(errno));
        return -1;
    }
    
    if(fcntl(skt, F_SETFL, flags | O_NONBLOCK) < 0){
        pysterror("Can't Set Socket to Non-blocking: %s\n", strerror(errno));
        return -1;
    }

    return 0;
}


int get_env_var_value(std::string env_var_name){
    int value = -1;
    const char* env_str = std::getenv(env_var_name.c_str());
    if (env_str) {
        value = std::stoi(std::string(env_str));
    }
    return value;
}

void set_timeout_limit(){
    int val = get_env_var_value("PYST_READ_TIMEOUT");
    pyst_read_timeout_limit = val>0? val:pyst_read_timeout_limit;
    val = get_env_var_value("PYST_TIMEOUT");
    pyst_conn_timeout_limit = (val > 0? val:pyst_conn_timeout_limit) * 1000;
}


int recv_from_socket(int skt){
  uint8_t  tmp[MAX_PACKET_TOTAL_BYTES_LIMIT];
  int len = recv(skt, tmp, MAX_PACKET_TOTAL_BYTES_LIMIT, 0);
  if(len > 0){
    int n_remain = len;
    while(n_remain > 0){
        PystPacket pkt;
        pkt.parse_from_byte_stream(&tmp[len-n_remain], n_remain);
        int len_pkt = pkt.get_bytes_length();
        pyst_packet_id pid = decode_pid(&tmp[len-n_remain]);
        for(int i=0;i<len_pkt;i++){
            pyst_client_in_messages[pyst_write_ptr][i] = pkt.bytes[i];
        }
        pyst_client_in_message_length[pyst_write_ptr] = len_pkt;
        pyst_client_socket_map[pid.p_client_id] = skt;

        show_pkt((char*)"recv_from_socket", len_pkt, pyst_client_in_messages[pyst_write_ptr]);

        pyst_write_ptr = (pyst_write_ptr+1) % PYST_C_BUFFER_SIZE;

        n_remain -= len_pkt;
    }
  }

  return len;
}


/*
Should any message comes at client socket,
the message will be buffered for target to fetch.
pyst_client_serve_handler_running[skt] = false to stop this routine
*/
void client_serve_handler(int skt, struct sockaddr_in t_addr){
    if(set_socket_non_blocking(skt) < 0){
        pysterror("set non blocking failed for client socket %d\n", skt);
        return;
    }

    pystdebug("Server starts to serve client socket %d @ %s:%d ...\n", skt, inet_ntoa(t_addr.sin_addr), t_addr.sin_port);

    pyst_client_serve_handler_running[skt] = true;
    while(pyst_client_serve_handler_running[skt]){
        int recv_len = recv_from_socket(skt);
        if(recv_len == 0){ // disconnected
            break;
        } else if(recv_len > 0){
            pyst_last_recv_time = cpu_time();
        } else { // recv failed
            if(errno != EWOULDBLOCK) {
                pysterror("Client socket %d message Receiving Error: %s\n", skt, strerror(errno));
                break;
            }
        }
    }

    while(recv_from_socket(skt) != 0);
    pystdebug("Client socket %d @ %s:%d disconnected. Serve stops serving it\n", skt, inet_ntoa(t_addr.sin_addr), t_addr.sin_port);
}



/*
Should at least one client connected to server socket in given countdown timeout,
a client serve worker will spwan.
pyst_accept_handler_running = false to stop this routine
*/
void accept_handler(int svr_skt){
    pystdebug("Server waits for clients to Connect ...\n");    
    bool connected = false;
    int timestep = 100;
    int timeout = pyst_conn_timeout_limit;
    
    pyst_accept_handler_running[svr_skt] = true;
    while(pyst_accept_handler_running[svr_skt]){
        int clt_skt;
        struct sockaddr_in t_addr;
        socklen_t sin_size = sizeof(struct sockaddr_in);
        clt_skt = accept(svr_skt, (struct sockaddr *)&t_addr, &sin_size);

        if(clt_skt < 0){ // no connection
            if(errno != EWOULDBLOCK) {
                pysterror("Unable to Connect to Client Socket Error: %s\n", strerror(errno));
                break;
            }
        } else { // has connection
            pystdebug("Connected to Client via %s:%d, client skt = %d\n", inet_ntoa(t_addr.sin_addr), t_addr.sin_port, clt_skt);
            // spin off thread to serve this client socket
            pyst_client_serve_threads[clt_skt] = std::thread(client_serve_handler, clt_skt, t_addr);
            connected = true;
        }

        std::this_thread::sleep_for(std::chrono::milliseconds(timestep));
        timeout -= timestep;
        if(timeout <= 0 && !connected){
            pysterror("Timeout, no client to connect in %d s. Did you start python test properly?\n", pyst_conn_timeout_limit/1000);
            // no valid connection in timeout. close the opened server socket.
            close(svr_skt);
            usleep(1);
        }
    }

    pystdebug("Server socket %d stops accepting new clients to connect\n", svr_skt);
}


void stop_accept(){
    // terminate accept thread
    for (auto& sock_running : pyst_accept_handler_running) {
        sock_running.second = false;
    }
    for (auto& sock_thread : pyst_accept_threads) {
        if(sock_thread.second.get_id() != std::thread::id()){// wait for run if start gets called
            sock_thread.second.join();
        }
        // close server socket
        close(sock_thread.first);
        pystdebug("Server socket %d closed\n", sock_thread.first);
    }
}

void stop_client_serve(){
    // terminate client serve thread
    for (auto& sock_running : pyst_client_serve_handler_running) {
        sock_running.second = false;
    }
    for (auto& sock_thread : pyst_client_serve_threads) {
        if(sock_thread.second.get_id() != std::thread::id()){// wait for run if start gets called
            sock_thread.second.join();
        }
        // close client socket
        close(sock_thread.first);
        pystdebug("Client socket %d closed\n", sock_thread.first);
    }
}

void stop_heartbeat(){
    pyst_heartbeat_running = false;
    if(pyst_heartbeat_thread.get_id() != std::thread::id()){// wait for run if start gets called
        pyst_heartbeat_thread.join();
    }
}


int stop_server(){
    stop_heartbeat();
    stop_client_serve();
    stop_accept();
    pyst_is_alive = false;
    pystdebug("Server stopped\n");
    return 1;
}

void heartbeat_handler(int beat_step_sec){
    static long long unsigned int life_sec = 0;

    pystdebug("Heart beat started\n");
    pyst_heartbeat_running = true;
    while(pyst_heartbeat_running){
        std::this_thread::sleep_for(std::chrono::seconds(beat_step_sec));
        life_sec += beat_step_sec;
        if(pyst_last_recv_time > 0 && 
           cpu_time() - pyst_last_recv_time >= pyst_read_timeout_limit){
           pysterror("Recv Timeout, no client was found to send data in %d s. If you ensure that test was correctly running, you may set PYST_READ_TIMEOUT=<seconds> environment variable to adjust the timeout limit.\n", pyst_read_timeout_limit);
           stop_accept();
           stop_client_serve();
           pyst_is_alive = false;
           break;
        }
        pystdebug("Heart beat %d seconds\n", life_sec);
    }
    pystdebug("Heart beat stopped\n");
}


void signal_handler(int signum){
  switch(signum){
    case SIGINT:
        pysterror("Received SIGINT to stop\n");
        stop_server();
        usleep(1);
        exit(signum);
    default:
        break;
  }
}


int build_server(uint32_t port){
    srand(time(NULL));
    print_logo();
    std::signal(SIGINT, signal_handler);
    set_timeout_limit();

    // server info
    struct sockaddr_in serv;
    std::memset(&serv, 0, sizeof(serv));
    serv.sin_family = AF_INET;
    serv.sin_port = htons(port);
    serv.sin_addr.s_addr = htonl(INADDR_ANY);
  
    int svr_skt = socket(serv.sin_family, SOCK_STREAM, 0);
    if(svr_skt < 0){
      pysterror("Create Server Socket Error: %s\n", strerror(errno));
      return -1;
    }
    pystdebug("Server Built Socket %d\n", svr_skt);

    if(set_socket_non_blocking(svr_skt) < 0){
      pysterror("set non blocking socket failed in m_build_socket\n");
      return -1;
    }

    // set server socket to reusable to avoid "Already in use" issue
    int opt = 1;
    setsockopt(svr_skt, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    int bd_res = bind(svr_skt, (struct sockaddr *)&serv, sizeof(struct sockaddr));
    if(bd_res < 0) {
      pysterror("Bind Server Socket Error: %s\n", strerror(errno));
      return -1;
    }
    pystdebug("Server Bind Socket %d\n", svr_skt);

    int ltn_res = listen(svr_skt, SOMAXCONN);
    if(ltn_res < 0) {
      pysterror("Server Listen error:%s\n", strerror(errno));
      return -1;
    }
    pystdebug("Server Activated Socket %d\n", svr_skt);

    pyst_accept_threads[svr_skt] = std::thread(accept_handler, svr_skt);
    pyst_heartbeat_thread = std::thread(heartbeat_handler, 1);

    pyst_is_alive = true;

    return 1;
}


int server_is_alive(){
    return pyst_is_alive;
}


int server_is_empty(){
    int ans = (pyst_read_ptr == pyst_write_ptr);
    return ans;
}


uint32_t get_next_message(uint8_t* msg){
    if(server_is_empty()){
        return 0;
    }

    uint32_t len = pyst_client_in_message_length[pyst_read_ptr];
    for(uint32_t i=0; i<len; i++){
        msg[i] = pyst_client_in_messages[pyst_read_ptr][i];
    }

    pyst_read_ptr = (pyst_read_ptr + 1) % PYST_C_BUFFER_SIZE;

    show_pkt((char*)"  sv_get_message", len, msg);

    return len;
}


void put_next_message(uint32_t len, uint8_t* msg){
    pyst_packet_id pid = decode_pid(msg);
    if(pyst_client_socket_map.find(pid.p_client_id) == pyst_client_socket_map.end()){
        pysterror("Unregistered pid %d is going to put in echo message\n", pid.p_client_id);
        throw std::runtime_error("Unregistered pid");
        return;
    }

    show_pkt((char*)"  sv_put_message", len, msg);

    int skt = pyst_client_socket_map[pid.p_client_id];
    send(skt, msg, len, 0);
    // pystdebug("Message has been put in output buffer\n");
}




