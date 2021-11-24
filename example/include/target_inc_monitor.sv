

  target_item resp;

  task run_phase(uvm_phase phase);
    `uvm_info(get_type_name(), "run_phase", UVM_HIGH)
    vif.proxy_back_ptr = this;
    do_mon();
  endtask : run_phase

  function void sample();
    //resp.input_signal  = vif.input_signal ;
    //resp.output_signal = vif.output_signal;
  endfunction : sample

  task do_mon();
    //`uvm_info(get_type_name(), "do_mon ", UVM_HIGH)
    //resp = target_item::type_id::create("resp");
    //  fork vif.run(); join_none

    monitor_test_seq();

    //forever @(posedge vif.input_signal)
    //begin
    //  resp = target_item::type_id::create("resp");
    //  sample();
    //  analysis_port.write(resp);
    //end

  endtask : do_mon

  function void write(target_item resp);
    analysis_port.write(resp);
  endfunction

  task monitor_test_seq();
    //`uvm_info(get_type_name(), $sformatf( "%s started  ",  "test " ), UVM_HIGH )
    //fork
    //    mycheck();
    //    mymeasure();
    //join_none
  endtask

