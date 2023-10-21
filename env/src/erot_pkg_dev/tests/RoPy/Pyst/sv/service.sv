`ifndef __PYST_SERVICE__
`define __PYST_SERVICE__



import "DPI-C" context function void pyst_service_start(input int len, inout int unsigned ports[], input int is_c_call);
import "DPI-C" context function void pyst_service_stop();
import "DPI-C" context function int  pyst_has_message();
import "DPI-C" context function int  pyst_service_alive();
import "DPI-C" context function int  pyst_receive_message(input int sv_len, output byte unsigned data[], input int is_c_call);
import "DPI-C" context task pyst_send_message(input int len, input byte unsigned data[], input int is_c_call);
import "DPI-C" context function real cpu_time();

class pyst_profiler extends uvm_object;
  real total_sim_time = cpu_time();
  real pyst_time = 0;
  int unsigned pkt_nbr[int][int]; // comp, func
  real routine_time[int][int]; // comp, func
  int unsigned pkt_in_processing[int][int]; // clt, th

  `uvm_object_utils(pyst_profiler)

  function new(string name="pyst_profiler");
    super.new(name);
  endfunction : new
  
  function int unsigned get_total_pkt_nbr();
    int unsigned ans = 0;
    foreach(pkt_nbr[c]) begin
      foreach(pkt_nbr[c][f]) begin
        ans += pkt_nbr[c][f];
      end
    end
    return ans;
  endfunction : get_total_pkt_nbr
  
endclass : pyst_profiler

class pyst_service extends uvm_component;
  pyst_profiler profiler;
  uvm_analysis_port#(pyst_packet)     analysis_port;
  uvm_analysis_export#(pyst_packet)   analysis_export;
  uvm_tlm_analysis_fifo#(pyst_packet) analysis_fifo;

  bit en_dbg = 0;
  int unsigned ports[];
  semaphore pkt_in_processing_lock;

  `uvm_component_utils_begin(pyst_service)
  `uvm_component_utils_end

  function new(string name="pyst_service", uvm_component parent);
    super.new(name, parent);
    `uvm_info(this.get_name(), "Attempt to start service ...", UVM_MEDIUM)
    this.process_cmdline_args();
    if(this.en_dbg) begin
      `uvm_info(this.get_name(), $sformatf("ports = %p", this.ports), UVM_MEDIUM)
    end
    pyst_service_start(this.ports.size(), this.ports, 0);
  endfunction : new

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    this.profiler = pyst_profiler::type_id::create("profiler");
    this.pkt_in_processing_lock = new(1);
    this.analysis_fifo = new($sformatf("fifo"), this);
    this.analysis_port = new($sformatf("ap"), this);
    this.analysis_export = new($sformatf("exp"), this);
  endfunction : build_phase

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    this.analysis_export.connect(this.analysis_fifo.analysis_export);
  endfunction : connect_phase

  virtual function void process_cmdline_args();
    uvm_cmdline_processor clp = uvm_cmdline_processor::get_inst();

    begin
      string arg;
      this.en_dbg = clp.get_arg_value("+PYST_DEBUG", arg);
    end

    begin
      string args[$];
      int unsigned pp[$];
      int num = clp.get_arg_values("+PORT=", args);
      foreach(args[i]) begin
        string tmp[$];
        uvm_split_string(args[i], ",", tmp);
        foreach(tmp[j]) begin
          pp.push_back(tmp[j].atoi());
        end
      end
      pp = pp.unique();
      this.ports = new[pp.size()](pp);
    end
  endfunction : process_cmdline_args
  
  task main_phase(uvm_phase phase);
    bit py_still_run;
    longint unsigned pkt_in_processing = 0;
    byte unsigned indata[MAX_PACKET_TOTAL_BYTES_LIMIT];
    byte unsigned outdata[MAX_PACKET_TOTAL_BYTES_LIMIT];

    if(!pyst_service_alive()) begin
      `uvm_fatal(this.get_name(), "Starting service failed")
    end
    `uvm_info(this.get_name(), "Service started", UVM_MEDIUM)

    phase.raise_objection(this);
    
    fork
      forever begin
        pyst_packet t;
        this.analysis_fifo.get(t);
        foreach(t.bytes[i]) begin
          outdata[i] = t.bytes[i];
        end
        pyst_send_message(t.bytes.size(), outdata, 0);

        pkt_in_processing_lock.get(1);
          pkt_in_processing--;
          this.profiler.pkt_in_processing[t.client_id][t.thread_id]--;
        pkt_in_processing_lock.put(1);
        if(this.en_dbg) begin
          `uvm_info(this.get_name(), $sformatf("Sent acknowledge. Has %0d packets left in processing.", pkt_in_processing), UVM_MEDIUM)
          foreach(this.profiler.pkt_in_processing[c]) begin
            foreach(this.profiler.pkt_in_processing[c][t]) begin
              `uvm_info(this.get_name(), $sformatf("client[%0d]thread[%0d] has %0d packets left", c, t, this.profiler.pkt_in_processing[c][t]), UVM_MEDIUM)
            end
          end
        end
      end
    join_none

    while(pyst_service_alive()) begin
      real pyst_pkt_time = cpu_time();
      while(pyst_service_alive() && !pyst_has_message()) #0;
      pyst_pkt_time = cpu_time() - pyst_pkt_time;
      this.profiler.pyst_time += pyst_pkt_time;
      this.abnormal_termination_check();

      while(pyst_has_message()) begin
        pyst_packet pkt = pyst_packet::type_id::create("pyst_pkt");
        int len = pyst_receive_message(MAX_PACKET_TOTAL_BYTES_LIMIT, indata, 0);
        py_still_run = pkt.parse_from_byte_stream(len, indata);
        if(this.en_dbg) begin
          `uvm_info(this.get_name(), $sformatf("Detect new data, fetching it ...\n%s", pkt.sprint()), UVM_MEDIUM)
          if(!py_still_run) begin
            `uvm_info(this.get_name(), $sformatf("Py has notified stop"), UVM_MEDIUM)
          end
        end

        pkt_in_processing_lock.get(1);
          pkt_in_processing++;
          this.profiler.pkt_in_processing[pkt.client_id][pkt.thread_id]++;
        pkt_in_processing_lock.put(1);
        this.analysis_port.write(pkt);
        this.profiler.pkt_nbr[pkt.component][pkt.routine]++;
        this.profiler.routine_time[pkt.component][pkt.routine] += pyst_pkt_time;
      end

      fork
        begin : pkt_in_processing_wait
          wait(pkt_in_processing == 0);
        end
        begin : pyst_has_message_wait
          forever begin
            real pyst_pkt_time = cpu_time();
            bit contin = pyst_service_alive() && !pyst_has_message();
            pyst_pkt_time = cpu_time() - pyst_pkt_time;
            this.profiler.pyst_time += pyst_pkt_time;
            if(!contin) break;
            #1;
          end
          this.abnormal_termination_check();
        end
      join_any
      disable pkt_in_processing_wait;
      disable pyst_has_message_wait;

      if(!py_still_run) begin
        break;
      end
    end // while

    this.abnormal_termination_check();

    // py has stopped
    wait(pkt_in_processing == 0);
    disable fork;

    `uvm_info(this.get_name(), "Stopping service ...", UVM_MEDIUM)
    pyst_service_stop();
    phase.drop_objection(this);
    `uvm_info(this.get_name(), "Service stopped", UVM_MEDIUM)
  endtask


  function void abnormal_termination_check();
    if(!pyst_service_alive()) begin
      `uvm_fatal(this.get_name(), "Service aborted abnomally while during execution. Python source may be timed out or lost its connection. You may use environment variable PYST_READ_TIMEOUT to set the customized timeout value in seconds.")
    end
  endfunction : abnormal_termination_check

  function void report_phase(uvm_phase phase);
    super.report_phase(phase);
    this.profiler.total_sim_time = cpu_time() - this.profiler.total_sim_time;
    `uvm_info("PROFILER", $sformatf("TOTAL TIME = %0.2f, ROCK TIME = %0.2f, ROCK COST = %0.1f%%, ROCK PACKET Num = %0d",
      this.profiler.total_sim_time, 
      this.profiler.pyst_time, 
      100.0*this.profiler.pyst_time/this.profiler.total_sim_time,
      this.profiler.get_total_pkt_nbr()),
      UVM_MEDIUM)
    foreach(this.profiler.pkt_nbr[c]) begin
      foreach(this.profiler.pkt_nbr[c][f]) begin
        `uvm_info("PROFILER", $sformatf("\tCOMPONENT %0d ROUTINE %0d : PACKET NUMBER %6d, ROCK TIME %0.2f",
          c, f, this.profiler.pkt_nbr[c][f], this.profiler.routine_time[c][f]), UVM_MEDIUM)
      end
    end 
  endfunction : report_phase

endclass : pyst_service


`endif // __PYST_SERVICE__




