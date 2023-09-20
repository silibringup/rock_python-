`ifndef __PYST_SERVICE_SUBSCRIBER__
  `define __PYST_SERVICE_SUBSCRIBER__

class pyst_service_subscriber extends uvm_component;
  uint32_t user_id;

  uvm_analysis_port#(pyst_packet)     analysis_port;
  uvm_analysis_export#(pyst_packet)   analysis_export;
  uvm_tlm_analysis_fifo#(pyst_packet) analysis_fifo;

  `uvm_component_utils_begin(pyst_service_subscriber)
  `uvm_component_utils_end

  function new(string name="pyst_service_subscriber", uvm_component parent);
    super.new(name, parent);
  endfunction : new

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
    this.analysis_port = new("ap", this);
    this.analysis_export = new("exp", this);
    this.analysis_fifo = new("fifo", this);
  endfunction : build_phase

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
    this.analysis_export.connect(this.analysis_fifo.analysis_export);
  endfunction : connect_phase

  task run_phase(uvm_phase phase);
    phase.raise_objection(this);
    forever begin
      pyst_packet pkt;
      this.analysis_fifo.get(pkt);
      if(pkt.ptype == ABORT) begin
        break;
      end

      if(pkt.routine == this.user_id) begin
        this.packet_handler(pkt);
      end
    end
    phase.drop_objection(this);
    `uvm_info(this.get_name(), "Service subscriber stopped", UVM_MEDIUM)
  endtask : run_phase

  virtual task packet_handler(ref pyst_packet pkt);
    case(pkt.ptype)
      WRITE: begin
        this.write_handler(pkt);
      end // case : WRITE

      READ: begin
        this.read_handler(pkt);
      end // case : READ

      FUNC: begin
        pyst_argument ret;
        this.function_handler(pkt, ret);
      end // case: FUNC
    endcase
  endtask : packet_handler


  // ----------------------------------------------
  // write
  virtual task write_handler(ref pyst_packet pkt);
    this.write_call(pkt);
  endtask : write_handler

  virtual task write_call(ref pyst_packet pkt);
  endtask : write_call  


  // ----------------------------------------------
  // read
  virtual task read_handler(ref pyst_packet pkt);
    pyst_packet rd_pkt;
    this.read_call(pkt, rd_pkt);
    if(rd_pkt == null) begin
      if(!$cast(rd_pkt, pkt.clone())) begin
        `uvm_fatal(this.get_name(), "Unable to cast")
      end
    end
    if((pkt.bytes.size() != 0 && rd_pkt.bytes.size() == 0) ||
       (pkt.fields.size() != 0 && rd_pkt.fields.size() == 0)) begin
      `uvm_fatal(this.get_name(), "readback packet has no data to return")
    end
    this.analysis_port.write(rd_pkt);
  endtask : read_handler

  virtual task read_call(ref pyst_packet pkt, ref pyst_packet rd_pkt);
  endtask : read_call

  // ----------------------------------------------
  // function
  virtual task function_handler(ref pyst_packet pkt, ref pyst_argument ret);
    pyst_argument_parser arg_parser = pyst_argument_parser::type_id::create("arg_parser");
    string function_name = arg_parser.parse(pkt);
    this.function_call(function_name, arg_parser.args, ret);
    if(ret != null) begin
      uint8_q func_name = pkt.fields[0];
      // has return value, field[1] for ret
      uint8_q ret_field = ret.to_bytes();
      pkt.fields = {};
      pkt.fields.push_back(func_name);
      pkt.fields.push_back(ret_field);
      pkt.update_from_fields();
    end
    this.analysis_port.write(pkt);
  endtask : function_handler

  virtual task function_call(string function_name, ref pyst_argument args[$], ref pyst_argument ret);
    `uvm_fatal(this.get_name(), "Must implement in subclass")
  endtask : function_call

  virtual function void set_id(uint32_t id);
    this.user_id = id;
  endfunction : set_id

endclass : pyst_service_subscriber

`endif
