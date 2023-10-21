`ifndef __RP_COMPONENT_COMMON__
`define __RP_COMPONENT_COMMON__


class rp_common extends uvm_component;
  localparam int unsigned ID = 0;

  typedef enum {
    FINISH = 0,
    HDL_RELEASE = 1,
    HDL_DEPOSIT = 2,
    HDL_FORCE = 3,
    HDL_READ = 4,
    WAIT_SIM_TIME = 5,
    FOPEN = 6,
    FCLOSE = 7,
    GET_SIM_TIME = 8
  } routine_t;

  `uvm_component_utils_begin(rp_common)
  `uvm_component_utils_end

  function new(string name="rp_common", uvm_component parent);
    super.new(name, parent);
  endfunction : new

  function void build_phase(uvm_phase phase);
    super.build_phase(phase);
  endfunction : build_phase

  function void connect_phase(uvm_phase phase);
    super.connect_phase(phase);
  endfunction : connect_phase

  function void arg_parse(pyst::pyst_packet pkt, ref string hdl_path, ref byte unsigned value[$]);
    pyst::pyst_argument_string string_arg;
    pyst::pyst_argument_uint8_t uint8_arg;
    pyst::pyst_argument_parser parser = pyst::pyst_argument_parser::type_id::create("parser");
    void'(parser.parse(pkt));

    if(!$cast(string_arg, parser.args[0])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[0] Unable to cast to string"))
    end
    hdl_path = string_arg.value[0];

    if(parser.args.size() > 1) begin
      if(!$cast(uint8_arg, parser.args[1])) begin
        `uvm_fatal(this.get_name(), $sformatf("arg[1] Unable to cast to uint8"))
      end
      value = uint8_arg.value;  
    end
  endfunction

  function void arg_parse_hdl(pyst::pyst_packet pkt, ref string hdl_path, ref byte unsigned value[$]);
    pyst::pyst_argument_string string_arg;
    pyst::pyst_argument_uint8_t uint8_arg;
    pyst::pyst_argument_parser parser = pyst::pyst_argument_parser::type_id::create("parser");
    void'(parser.parse(pkt));

    if(!$cast(string_arg, parser.args[0])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[0] Unable to cast to string"))
    end
    hdl_path = string_arg.value[0];

    if(parser.args.size() > 1) begin
      if(!$cast(uint8_arg, parser.args[1])) begin
        `uvm_fatal(this.get_name(), $sformatf("arg[1] Unable to cast to uint8"))
      end
      value = uint8_arg.value;  
    end
  endfunction : arg_parse_hdl

  function void arg_parse_fileopen(pyst::pyst_packet pkt, ref string fpath, ref string mode);
    pyst::pyst_argument_string string_arg;
    pyst::pyst_argument_parser parser = pyst::pyst_argument_parser::type_id::create("parser");
    void'(parser.parse(pkt));

    if(!$cast(string_arg, parser.args[0])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[0] Unable to cast to string"))
    end
    fpath = string_arg.value[0];
    mode = string_arg.value[1];
  endfunction : arg_parse_fileopen

  function void arg_parse_fileclose(pyst::pyst_packet pkt, ref int fd);
    pyst::pyst_argument_int32_t int32_arg;
    pyst::pyst_argument_parser parser = pyst::pyst_argument_parser::type_id::create("parser");
    void'(parser.parse(pkt));

    if(!$cast(int32_arg, parser.args[0])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[0] Unable to cast to int32"))
    end
    fd = int32_arg.value[0];
  endfunction

  function void arg_parse_time(pyst::pyst_packet pkt, ref string unit, ref real value);
    pyst::pyst_argument_string string_arg;
    pyst::pyst_argument_double double_arg;
    pyst::pyst_argument_parser parser = pyst::pyst_argument_parser::type_id::create("parser");
    void'(parser.parse(pkt));

    if(!$cast(string_arg, parser.args[0])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[0] Unable to cast to string"))
    end
    unit = string_arg.value[0];

    if(!$cast(double_arg, parser.args[1])) begin
      `uvm_fatal(this.get_name(), $sformatf("arg[1] Unable to cast to uint8"))
    end
    value = double_arg.value[0];
  endfunction : arg_parse_time

  task hdl_deposit(string hdl_path, uvm_hdl_data_t value);
    if(!uvm_hdl_check_path(hdl_path)) begin
      `uvm_fatal(this.get_name(), $sformatf("No such hdl path %s", hdl_path))
    end
    uvm_hdl_deposit(hdl_path, value);
  endtask : hdl_deposit

  task hdl_release(string hdl_path);
    if(!uvm_hdl_check_path(hdl_path)) begin
      `uvm_fatal(this.get_name(), $sformatf("No such hdl path %s", hdl_path))
    end
    uvm_hdl_release(hdl_path);
  endtask

  task hdl_force(string hdl_path, uvm_hdl_data_t value);
    if(!uvm_hdl_check_path(hdl_path)) begin
      `uvm_fatal(this.get_name(), $sformatf("No such hdl path %s", hdl_path))
    end
    uvm_hdl_force(hdl_path, value);
  endtask : hdl_force

  task hdl_read(string hdl_path, output uvm_hdl_data_t value);
    if(!uvm_hdl_check_path(hdl_path)) begin
      `uvm_fatal(this.get_name(), $sformatf("No such hdl path %s", hdl_path))
    end
    uvm_hdl_read(hdl_path, value);
    // DPI returns only 32-bit int
    value = value[31:0];
  endtask : hdl_read

  task wait_sim_time(string unit, real value);
    case(unit)
      "s":  #(value * 1s);
      "ms": #(value * 1ms);
      "us": #(value * 1us);
      "ns": #(value * 1ns);
      "ps": #(value * 1ps);
      "fs": #(value * 1fs);
    endcase
  endtask : wait_sim_time

  function string get_sim_time();
    return $sformatf("%fns", $realtime/1ns);
  endfunction : get_sim_time

endclass : rp_common


`endif

