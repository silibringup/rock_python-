`ifndef __PYST_PACKET__
`define __PYST_PACKET__

class pyst_packet extends uvm_sequence_item;

  uint32_t id;
  uint8_t client_id;
  uint8_t thread_id;
  uint16_t pkt_nbr;
  packet_type_t ptype;
  uint32_t component;
  uint32_t routine;
  uint32_t n_fields;
  uint32_t n_each_field_bytes[$];
  uint8_t bytes[];
  uint8_q fields[$];
  
  `uvm_object_utils_begin(pyst_packet)
    `uvm_field_int(id, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_enum(packet_type_t, ptype, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_int(component, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_int(routine, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_int(n_fields, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_queue_int(n_each_field_bytes, UVM_ALL_ON|UVM_NOPRINT)
    `uvm_field_array_int(bytes, UVM_ALL_ON|UVM_NOPRINT)
  `uvm_object_utils_end

  function new(string name = "pyst_packet");
    super.new(name);
  endfunction

  function bit parse_from_byte_stream(int len, byte unsigned data[]);
    this.bytes = new[len](data);
    this.id = {this.bytes[0], this.bytes[1], this.bytes[2], this.bytes[3]};
    this.client_id = this.bytes[0];
    this.thread_id = this.bytes[1];
    this.pkt_nbr = {this.bytes[2], this.bytes[3]};
    this.ptype = packet_type_t'( {this.bytes[4], this.bytes[5], this.bytes[6], this.bytes[7]} );
    this.component = {this.bytes[8], this.bytes[9], this.bytes[10], this.bytes[11]};
    this.routine = {this.bytes[12], this.bytes[13], this.bytes[14], this.bytes[15]};
    this.n_fields = {this.bytes[16]};

    for(int i=N_NBR_FIELD_BYTE_POS+1; i<N_NBR_FIELD_BYTE_POS+1+this.n_fields*N_EACH_NBR_FIELD_BYTES; i+=N_EACH_NBR_FIELD_BYTES) begin
      bit[8*N_EACH_NBR_FIELD_BYTES-1:0] t = {>>{this.bytes[i +: N_EACH_NBR_FIELD_BYTES]}};
      this.n_each_field_bytes.push_back(uint32_t'(t));
    end

    // payload fields
    begin
      int s = N_NBR_FIELD_BYTE_POS+1 + this.n_fields*N_EACH_NBR_FIELD_BYTES;
      foreach(this.n_each_field_bytes[i]) begin
        int n_bytes = this.n_each_field_bytes[i];
        uint8_q fq;
        for(int j=s; j<s+n_bytes; j++) begin
          fq.push_back(this.bytes[j]);
        end
        this.fields.push_back(fq);
        s += n_bytes;
      end
    end

    return (this.ptype != ABORT); // return is_run
  endfunction : parse_from_byte_stream

  virtual function void update_from_fields();
    uint32_t n_tot_bytes;
    uint32_t idx = 0;
    this.n_fields = this.fields.size();
    this.n_each_field_bytes = {};
    foreach(this.fields[i]) begin
      this.n_each_field_bytes.push_back(this.fields[i].size());
    end

    n_tot_bytes = N_NBR_FIELD_BYTE_POS+1 + this.n_fields*N_EACH_NBR_FIELD_BYTES + this.n_each_field_bytes.sum();
    this.bytes = new[n_tot_bytes](this.bytes);
    this.bytes[N_NBR_FIELD_BYTE_POS] = uint8_t'(this.n_fields);

    for(int i=N_NBR_FIELD_BYTE_POS+1, j=0; 
        i<N_NBR_FIELD_BYTE_POS+1+this.n_fields*N_EACH_NBR_FIELD_BYTES;
        i+=N_EACH_NBR_FIELD_BYTES, j++) begin
      bit[8*N_EACH_NBR_FIELD_BYTES-1:0] t = this.n_each_field_bytes[j];
      for(int k=0;k<N_EACH_NBR_FIELD_BYTES;k++) begin
        this.bytes[i+k] = t[(N_EACH_NBR_FIELD_BYTES-k)*8-1 -: 8];
      end
    end

    idx = N_NBR_FIELD_BYTE_POS+1+this.n_fields*N_EACH_NBR_FIELD_BYTES;
    foreach(this.fields[i]) begin
      foreach(this.fields[i][j]) begin
        this.bytes[idx] = this.fields[i][j];
        idx++;
      end
    end
  endfunction : update_from_fields


  function string i2h(uint32_t n);
    string ans;
    if(n > uint32_t'((1<<24)-1)) begin
      ans = $sformatf("h'%08H", n);
    end else if(n > uint32_t'((1<<16)-1)) begin
      ans = $sformatf("h'%06H", n);
    end else if(n > uint32_t'((1<<8)-1)) begin
      ans = $sformatf("h'%04H", n);
    end else begin
      ans = $sformatf("h'%02H", n);
    end
    return ans;
  endfunction : i2h

  function void do_copy(uvm_object rhs);
    pyst_packet _rhs;
    super.do_copy(rhs);
    if(!$cast(_rhs, rhs)) begin
      `uvm_fatal(this.get_name(), "Unable to cast rhs")
    end
    foreach(_rhs.fields[i]) begin
      this.fields.push_back(_rhs.fields[i]);
    end
  endfunction : do_copy

  function void do_print(uvm_printer printer);
    super.do_print(printer);
    printer.print_generic(.name("id"), .type_name("uint"), .size($bits(this.id)), .value(i2h(this.id)));
    printer.print_generic(.name("client"), .type_name("uint"), .size($bits(this.client_id)), .value(i2h(this.client_id)));
    printer.print_generic(.name("thread"), .type_name("uint"), .size($bits(this.thread_id)), .value(i2h(this.thread_id)));
    printer.print_generic(.name("No"), .type_name("uint"), .size($bits(this.pkt_nbr)), .value(i2h(this.pkt_nbr)));
    printer.print_generic(.name("ptype"), .type_name("packet_type_t"), .size($bits(this.ptype)), .value(this.ptype.name()));
    printer.print_generic(.name("component"), .type_name("uint"), .size($bits(this.component)), .value(i2h(this.component)));
    printer.print_generic(.name("routine"), .type_name("uint"), .size($bits(this.routine)), .value(i2h(this.routine)));
    printer.print_generic(.name("n_fields"), .type_name("uint"), .size($bits(this.n_fields)), .value(i2h(this.n_fields)));

    printer.print_generic(.name("n_each_field_bytes"), .type_name("uintq"), .size(this.n_each_field_bytes.size()), .value("-"));

    foreach(this.n_each_field_bytes[i]) begin
      printer.print_generic(.name($sformatf("  n_field_bytes[%0d]",i)), .type_name("uint"), .size($bits(this.n_each_field_bytes[i])), .value(i2h(this.n_each_field_bytes[i])));
    end

    printer.print_generic(.name("fields"), .type_name("ubyteqq"), .size(this.fields.size()), .value("-"));
    foreach(this.fields[i]) begin
      printer.print_generic(.name($sformatf("  fields[%0d]",i)), .type_name("ubyteq"), .size(this.fields[i].size()), .value("-"));
      foreach(this.fields[i][j]) begin
        printer.print_generic(.name($sformatf("    field_byte[%0d]",j)), .type_name("ubyte"), .size($bits(this.fields[i][j])), .value(i2h(this.fields[i][j])));
      end
    end
  endfunction : do_print
  
endclass : pyst_packet

`endif

